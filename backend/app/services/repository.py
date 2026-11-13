import os
import hashlib
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

IGNORE_DIRS = {
    ".git", ".svn", ".hg", "node_modules", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".venv", "venv", "env", "dist", "build", ".next",
    ".idea", ".vscode", "coverage", ".turbo"
}

IGNORE_EXTS = {
    ".pyc", ".pyo", ".pyd", ".so", ".dll", ".dylib", ".exe", ".bin",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico",
    ".mp4", ".mp3", ".pdf", ".zip", ".tar", ".gz", ".7z", ".rar",
    ".lock", ".sqlite", ".db"
}

def resolve_safe_path(base_dir: str, sub_path: str) -> Path:
    """
    Strict Path Traversal Protection.
    Resolves sub_path strictly within base_dir.
    Raises PermissionError if path resolves outside the repository root.
    """
    base = Path(base_dir).resolve()
    target = (base / sub_path).resolve()
    
    if not str(target).startswith(str(base)):
        raise PermissionError(f"Access denied: Path '{sub_path}' traverses outside repository boundary.")
    return target

def compute_file_hash(file_path: Path) -> str:
    """Computes SHA-256 hash of file contents for strict change detection."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()

def detect_confidentiality(repo_path: str) -> Dict[str, Any]:
    """
    Inspects repository for .frugal-coder.yaml or .frugal-coder.yml
    Returns confidentiality status and custom security rules.
    """
    base = Path(repo_path)
    config_files = [base / ".frugal-coder.yaml", base / ".frugal-coder.yml"]
    
    for cfg in config_files:
        if cfg.exists() and cfg.is_file():
            try:
                with open(cfg, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                
                is_confidential = False
                if data.get("project", {}).get("confidential") is True:
                    is_confidential = True
                if data.get("privacy", {}).get("inference") == "local_only" or data.get("privacy", {}).get("allow_cloud") is False:
                    is_confidential = True
                    
                return {
                    "is_confidential": is_confidential,
                    "privacy": data.get("privacy", {}),
                    "security": data.get("security", {}),
                    "config_source": cfg.name
                }
            except Exception as e:
                # Fail-safe: if config file is invalid or malformed, default to confidential for safety
                return {
                    "is_confidential": True,
                    "error": f"Failed to parse config: {str(e)}",
                    "config_source": cfg.name
                }
                
    return {
        "is_confidential": False,
        "privacy": {},
        "security": {},
        "config_source": None
    }

def detect_language_and_framework(repo_path: str) -> Dict[str, Optional[str]]:
    """Detects primary language and framework from manifest files."""
    base = Path(repo_path)
    lang = None
    framework = None
    
    # Check Python
    if (base / "requirements.txt").exists() or (base / "pyproject.toml").exists() or (base / "setup.py").exists():
        lang = "Python"
        if (base / "manage.py").exists():
            framework = "Django"
        elif any((base / f).exists() for f in ["main.py", "app.py"]):
            framework = "FastAPI / Flask"
            
    # Check Node / JS / TS
    elif (base / "package.json").exists():
        lang = "TypeScript" if (base / "tsconfig.json").exists() else "JavaScript"
        try:
            with open(base / "package.json", "r", encoding="utf-8") as f:
                content = f.read().lower()
                if "next" in content:
                    framework = "Next.js"
                elif "react" in content:
                    framework = "React"
                elif "express" in content:
                    framework = "Express"
                elif "vue" in content:
                    framework = "Vue"
                else:
                    framework = "Node.js"
        except Exception:
            framework = "Node.js"
            
    # Check Go
    elif (base / "go.mod").exists():
        lang = "Go"
        framework = "Standard Go"
        
    # Check Rust
    elif (base / "Cargo.toml").exists():
        lang = "Rust"
        framework = "Cargo"
        
    return {"language": lang or "Unknown", "framework": framework or "Standard"}

def get_repository_tree(repo_path: str, max_files: int = 1000) -> List[Dict[str, Any]]:
    """
    Safely indexes the repository file tree.
    Returns file paths, sizes, line counts, and metadata.
    """
    base = Path(repo_path).resolve()
    if not base.exists() or not base.is_dir():
        raise FileNotFoundError(f"Repository directory does not exist: {repo_path}")
        
    tree = []
    count = 0
    
    for root, dirs, files in os.walk(base):
        # Filter ignore dirs in-place
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]
        
        for file in files:
            ext = Path(file).suffix.lower()
            if ext in IGNORE_EXTS or file.startswith("."):
                continue
                
            full_path = Path(root) / file
            rel_path = str(full_path.relative_to(base)).replace("\\", "/")
            
            try:
                stat = full_path.stat()
                size_bytes = stat.st_size
                # Estimate line count for text files under 2MB
                lines = 0
                if size_bytes < 2 * 1024 * 1024:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = sum(1 for _ in f)
                        
                tree.append({
                    "relative_path": rel_path,
                    "name": file,
                    "extension": ext,
                    "size_bytes": size_bytes,
                    "lines": lines
                })
                count += 1
                if count >= max_files:
                    break
            except Exception:
                continue
                
        if count >= max_files:
            break
            
    return tree

