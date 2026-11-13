import os
import sys

# Example showing how to invoke Frugal Coder's AST progressive context engine
# directly from Python.

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.database import SessionLocal, init_db
from app.services.token_engine import TokenOptimizationEngine
from app.services.repository import get_repository_tree

def demonstrate_ast_compression():
    init_db()
    db = SessionLocal()
    try:
        repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        print(f"Inspecting repository at: {repo_path}")
        
        # 1. Discover file tree (L0)
        backend_dir = os.path.join(repo_path, "backend")
        tree = get_repository_tree(backend_dir, max_files=50)
        file_paths = [f["relative_path"] for f in tree if f["relative_path"].endswith(".py") and not f["relative_path"].startswith("tests")]
        print(f"Found {len(file_paths)} Python files for AST extraction.")
        
        # 2. Extract L1 progressive context
        context_text, opt_tokens, baseline_tokens = TokenOptimizationEngine.assemble_context(
            db=db,
            project_id="example_project",
            repo_path=backend_dir,
            target_files=file_paths[:4],
            level="L1"
        )
        
        print("\n--- Progressive AST Skeleton Context (Sample) ---")
        print(context_text[:500] + "\n...")
        print(f"\nBaseline estimated full tokens: {baseline_tokens}")
        print(f"Optimized AST skeleton tokens: {opt_tokens}")
        savings = ((baseline_tokens - opt_tokens) / baseline_tokens) * 100 if baseline_tokens > 0 else 0
        print(f"Context Token Reduction: {savings:.2f}%")

    finally:
        db.close()

if __name__ == "__main__":
    demonstrate_ast_compression()
