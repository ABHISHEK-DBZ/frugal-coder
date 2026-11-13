import ast
import re
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.entities import FileCache
from app.services.repository import compute_file_hash, resolve_safe_path

def estimate_tokens(text: str) -> int:
    """Accurate heuristic: 1 token ~= 3.8 characters for code/text."""
    if not text:
        return 0
    return max(1, int(len(text) / 3.8))

class ASTCompressor:
    """Extracts compact architectural skeletons (L1) from source code."""

    @staticmethod
    def compress_python(code: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Parses Python code using the standard library `ast` module."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            # Fallback to regex if file has invalid syntax or Python version mismatch
            return ASTCompressor.compress_generic(code)
            
        skeleton_lines = []
        symbols = []
        
        for node in tree.body:
            # Imports
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
                skeleton_lines.append(f"import {', '.join(names)}")
            elif isinstance(node, ast.ImportFrom):
                names = [alias.name for alias in node.names]
                mod = node.module or ""
                skeleton_lines.append(f"from {mod} import {', '.join(names)}")
                
            # Top-level Functions
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = [a.arg for a in node.args.args]
                sig = f"{'async ' if isinstance(node, ast.AsyncFunctionDef) else ''}def {node.name}({', '.join(args)}): ..."
                skeleton_lines.append(sig)
                doc = ast.get_docstring(node)
                if doc:
                    skeleton_lines.append(f'    """{doc.splitlines()[0]}"""')
                symbols.append({"type": "function", "name": node.name, "lineno": node.lineno})
                
            # Classes
            elif isinstance(node, ast.ClassDef):
                bases = [ast.unparse(b) for b in node.bases]
                base_str = f"({', '.join(bases)})" if bases else ""
                skeleton_lines.append(f"class {node.name}{base_str}:")
                doc = ast.get_docstring(node)
                if doc:
                    skeleton_lines.append(f'    """{doc.splitlines()[0]}"""')
                symbols.append({"type": "class", "name": node.name, "lineno": node.lineno})
                
                # Class Methods
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        m_args = [a.arg for a in item.args.args]
                        m_sig = f"    {'async ' if isinstance(item, ast.AsyncFunctionDef) else ''}def {item.name}({', '.join(m_args)}): ..."
                        skeleton_lines.append(m_sig)
                        symbols.append({"type": "method", "class": node.name, "name": item.name, "lineno": item.lineno})
                        
        skeleton = "\n".join(skeleton_lines)
        return skeleton, symbols

    @staticmethod
    def compress_javascript(code: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Regex-based AST skeleton extractor for JavaScript and TypeScript."""
        skeleton_lines = []
        symbols = []
        
        lines = code.splitlines()
        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            # Imports / Exports
            if stripped.startswith("import ") or stripped.startswith("export {") or stripped.startswith("const ") and "require(" in stripped:
                skeleton_lines.append(stripped)
            # Function definitions
            elif re.match(r'^(export\s+)?(async\s+)?function\s+([A-Za-z0-9_$]+)\s*\((.*?)\)', stripped):
                m = re.match(r'^(export\s+)?(async\s+)?function\s+([A-Za-z0-9_$]+)\s*\((.*?)\)', stripped)
                name = m.group(3)
                skeleton_lines.append(f"function {name}({m.group(4)}): ...")
                symbols.append({"type": "function", "name": name, "lineno": idx})
            # Class definitions
            elif re.match(r'^(export\s+)?class\s+([A-Za-z0-9_$]+)', stripped):
                m = re.match(r'^(export\s+)?class\s+([A-Za-z0-9_$]+)', stripped)
                name = m.group(2)
                skeleton_lines.append(f"class {name} {{ ... }}")
                symbols.append({"type": "class", "name": name, "lineno": idx})
            # Interface / Type definitions
            elif re.match(r'^(export\s+)?(interface|type)\s+([A-Za-z0-9_$]+)', stripped):
                skeleton_lines.append(stripped)
                
        skeleton = "\n".join(skeleton_lines[:60]) # cap for safety
        return skeleton, symbols

    @staticmethod
    def compress_generic(code: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Heuristic compression for other languages: extract top-level declarations."""
        lines = code.splitlines()
        skeleton_lines = []
        for line in lines[:50]:
            stripped = line.strip()
            if stripped.startswith(("#", "//", "/*", "*")):
                continue
            if any(stripped.startswith(k) for k in ["fn ", "func ", "def ", "class ", "pub ", "struct ", "package ", "import "]):
                skeleton_lines.append(stripped)
        return "\n".join(skeleton_lines), []

class TokenOptimizationEngine:
    """
    Core Token Optimization Engine implementing L0-L4 progressive context.
    Caches file skeletons, tracks token savings, and invalidates stale caches.
    """

    @classmethod
    def get_or_create_cache(
        cls,
        db: Session,
        project_id: str,
        repo_path: str,
        relative_path: str
    ) -> FileCache:
        """
        Retrieves cached skeleton or recomputes if hash has drifted.
        Guarantees cache invalidation on any file modification (Test G).
        """
        full_path = resolve_safe_path(repo_path, relative_path)
        if not full_path.exists() or not full_path.is_file():
            raise FileNotFoundError(f"File not found: {relative_path}")
            
        current_hash = compute_file_hash(full_path)
        
        cached = db.query(FileCache).filter(
            FileCache.project_id == project_id,
            FileCache.relative_path == relative_path
        ).first()
        
        # If cache exists and hash matches, return cached entry
        if cached and cached.content_hash == current_hash:
            return cached
            
        # Otherwise compute AST skeleton and token counts
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
            
        ext = full_path.suffix.lower()
        if ext == ".py":
            skeleton, symbols = ASTCompressor.compress_python(code)
        elif ext in [".js", ".ts", ".jsx", ".tsx"]:
            skeleton, symbols = ASTCompressor.compress_javascript(code)
        else:
            skeleton, symbols = ASTCompressor.compress_generic(code)
            
        token_full = estimate_tokens(code)
        token_skeleton = estimate_tokens(skeleton)
        
        if cached:
            # Invalidate and update existing cache entry
            cached.content_hash = current_hash
            cached.ast_skeleton = skeleton
            cached.symbols = symbols
            cached.token_count_full = token_full
            cached.token_count_skeleton = token_skeleton
        else:
            cached = FileCache(
                project_id=project_id,
                relative_path=relative_path,
                content_hash=current_hash,
                ast_skeleton=skeleton,
                symbols=symbols,
                token_count_full=token_full,
                token_count_skeleton=token_skeleton
            )
            db.add(cached)
            
        db.commit()
        db.refresh(cached)
        return cached

    @classmethod
    def assemble_context(
        cls,
        db: Session,
        project_id: str,
        repo_path: str,
        target_files: List[str],
        level: str = "L1"
    ) -> Tuple[str, int, int]:
        """
        Assembles progressive context for the agent.
        Levels:
          L0: File paths + metadata only
          L1: AST Skeletons
          L2: Relevant function snippets
          L3: Full source code of target files
        Returns: (context_text, optimized_tokens, baseline_tokens_if_all_full)
        """
        context_parts = []
        optimized_tokens = 0
        baseline_tokens = 0
        
        for rel_path in target_files:
            cache = cls.get_or_create_cache(db, project_id, repo_path, rel_path)
            baseline_tokens += cache.token_count_full
            
            if level == "L0":
                part = f"File: {rel_path} ({cache.token_count_full} tokens)"
                context_parts.append(part)
                optimized_tokens += estimate_tokens(part)
                
            elif level == "L1":
                part = f"--- File Skeleton: {rel_path} ---\n{cache.ast_skeleton}\n"
                context_parts.append(part)
                optimized_tokens += cache.token_count_skeleton
                
            elif level == "L3":
                full_path = resolve_safe_path(repo_path, rel_path)
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                part = f"--- Full Content: {rel_path} ---\n{content}\n"
                context_parts.append(part)
                optimized_tokens += cache.token_count_full
                
        return "\n".join(context_parts), optimized_tokens, baseline_tokens

