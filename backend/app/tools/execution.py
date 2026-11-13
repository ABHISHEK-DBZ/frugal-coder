import subprocess
import os
import difflib
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.entities import ActionType, AuditLog
from app.services.repository import resolve_safe_path, compute_file_hash
from app.policy.approval import ActionApprovalEngine, ActionNotApprovedError

logger = logging.getLogger(__name__)

class ToolExecutionEngine:
    """
    Controlled Tool Execution Engine with sandboxed filesystem, git, and shell runners.
    Guarantees that all mutating operations pass through ActionApprovalEngine.
    """

    # READ-ONLY TOOLS (Automatic execution)

    @staticmethod
    def read_file(repo_path: str, relative_path: str) -> Dict[str, Any]:
        """Reads file contents within repository boundary."""
        target = resolve_safe_path(repo_path, relative_path)
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(f"File not found: {relative_path}")
        with open(target, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return {"relative_path": relative_path, "content": content, "size": len(content)}

    @staticmethod
    def list_files(repo_path: str, sub_dir: str = "") -> List[str]:
        """Lists files within a safe sub-directory."""
        target_dir = resolve_safe_path(repo_path, sub_dir)
        files = []
        for item in target_dir.iterdir():
            files.append(item.name + ("/" if item.is_dir() else ""))
        return files

    @staticmethod
    def search_code(repo_path: str, query: str) -> List[Dict[str, Any]]:
        """Searches repository files for exact code queries."""
        base = Path(repo_path).resolve()
        matches = []
        for root, _, files in os.walk(base):
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in [".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".md", ".yaml", ".yml"]:
                    full_p = Path(root) / file
                    try:
                        with open(full_p, "r", encoding="utf-8", errors="ignore") as f:
                            for lineno, line in enumerate(f, 1):
                                if query.lower() in line.lower():
                                    rel = str(full_p.relative_to(base)).replace("\\", "/")
                                    matches.append({"file": rel, "line": lineno, "content": line.strip()})
                                    if len(matches) >= 50:
                                        return matches
                    except Exception:
                        continue
        return matches

    @staticmethod
    def git_status(repo_path: str) -> str:
        """Runs git status in repository working directory."""
        res = subprocess.run(
            ["git", "status", "--short"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        return res.stdout or res.stderr or "Clean working tree"

    @staticmethod
    def git_diff(repo_path: str) -> str:
        """Runs git diff in repository working directory."""
        res = subprocess.run(
            ["git", "diff"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        return res.stdout or "No changes"

    # MUTATING TOOLS (Mandatory Approval Verification)

    @classmethod
    def apply_write_file(
        cls,
        db: Session,
        repo_path: str,
        relative_path: str,
        new_content: str,
        approval_id: str
    ) -> Dict[str, Any]:
        """Writes content to a file after verifying valid approval."""
        ActionApprovalEngine.verify_execution_authorized(db, approval_id, repo_path)
        target = resolve_safe_path(repo_path, relative_path)
        
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(new_content)
            
        new_hash = compute_file_hash(target)
        return {"status": "success", "file": relative_path, "bytes_written": len(new_content), "hash": new_hash}

    @classmethod
    def apply_patch(
        cls,
        db: Session,
        repo_path: str,
        relative_path: str,
        original_snippet: str,
        replacement_snippet: str,
        approval_id: str
    ) -> Dict[str, Any]:
        """Applies targeted patch substitution after verifying approval."""
        ActionApprovalEngine.verify_execution_authorized(db, approval_id, repo_path)
        target = resolve_safe_path(repo_path, relative_path)
        
        with open(target, "r", encoding="utf-8") as f:
            content = f.read()
            
        if original_snippet not in content:
            raise ValueError(f"Patch target snippet not found in {relative_path}")
            
        updated = content.replace(original_snippet, replacement_snippet, 1)
        with open(target, "w", encoding="utf-8") as f:
            f.write(updated)
            
        new_hash = compute_file_hash(target)
        return {"status": "success", "file": relative_path, "hash": new_hash}

    @classmethod
    def delete_file(
        cls,
        db: Session,
        repo_path: str,
        relative_path: str,
        approval_id: str
    ) -> Dict[str, Any]:
        """Deletes file after verifying approval."""
        ActionApprovalEngine.verify_execution_authorized(db, approval_id, repo_path)
        target = resolve_safe_path(repo_path, relative_path)
        if target.exists():
            target.unlink()
        return {"status": "success", "file": relative_path, "deleted": True}

    @classmethod
    def run_sandboxed_shell(
        cls,
        db: Session,
        repo_path: str,
        command: str,
        approval_id: str,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Executes shell command strictly inside the repository working directory
        after explicit user approval and safety policy check.
        """
        ActionApprovalEngine.verify_execution_authorized(db, approval_id, repo_path)
        
        # Restricted environment
        safe_env = {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONPATH": repo_path,
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
            "TEMP": os.environ.get("TEMP", "")
        }
        
        try:
            res = subprocess.run(
                command,
                shell=True,
                cwd=repo_path,
                env=safe_env,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "command": command,
                "exit_code": res.returncode,
                "stdout": res.stdout,
                "stderr": res.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "command": command,
                "exit_code": -1,
                "error": f"Command timed out after {timeout} seconds"
            }

    @classmethod
    def git_commit(
        cls,
        db: Session,
        repo_path: str,
        message: str,
        approval_id: str
    ) -> Dict[str, Any]:
        """Executes git commit after approval."""
        ActionApprovalEngine.verify_execution_authorized(db, approval_id, repo_path)
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        res = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        return {"exit_code": res.returncode, "output": res.stdout or res.stderr}

    @classmethod
    def git_push(
        cls,
        db: Session,
        repo_path: str,
        approval_id: str
    ) -> Dict[str, Any]:
        """Executes git push after approval."""
        ActionApprovalEngine.verify_execution_authorized(db, approval_id, repo_path)
        res = subprocess.run(
            ["git", "push"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        return {"exit_code": res.returncode, "output": res.stdout or res.stderr}

