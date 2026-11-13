import os
import sys
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, os.path.abspath("backend"))

from app.core.database import Base, SessionLocal, engine
from app.models.entities import User, Project, Session as CodingSession, ActionType, ApprovalStatus
from app.auth.security import hash_password
from app.policy.approval import ActionApprovalEngine, ActionNotApprovedError
from app.tools.execution import ToolExecutionEngine

def run_workflow_demonstration():
    print("=== STARTING PRIORITY 5 COMPLETE PRODUCT WORKFLOW VERIFICATION ===")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    temp_repo = tempfile.mkdtemp(prefix="workflow_demo_")
    src = Path(temp_repo) / "src"
    src.mkdir(parents=True, exist_ok=True)
    tests = Path(temp_repo) / "tests"
    tests.mkdir(parents=True, exist_ok=True)

    auth_file = src / "auth.py"
    original_code = (
        "def verify_login(username, password, stored_password):\n"
        "    # Insecure plaintext check\n"
        "    if password == stored_password:\n"
        "        return True\n"
        "    return False\n"
    )
    with open(auth_file, "w", encoding="utf-8") as f:
        f.write(original_code)

    test_file = tests / "test_auth.py"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(
            "from src.auth import verify_login\n"
            "def test_login():\n"
            "    assert verify_login('alice', 'pass123', 'pass123') is True\n"
        )

    # Step 1: User Login & Setup
    pw_hash, salt = hash_password("DemoPassword123!")
    user = User(email="demo@frugalcoder.dev", username="lead_demo", password_hash=pw_hash, password_salt=salt)
    db.add(user)
    db.commit()
    print("STEP 1: User created and authenticated (JWT PBKDF2).")

    # Step 2 & 3: Create Project & Connect Repository
    project = Project(
        owner_id=user.id,
        name="workflow-auth-demo",
        repo_path=temp_repo,
        is_confidential=False,
        detected_language="Python",
        detected_framework="Standard"
    )
    db.add(project)
    db.commit()
    print(f"STEP 2 & 3: Connected project repository: {temp_repo}")

    # Step 4: Submit Task & Start Session
    session = CodingSession(
        project_id=project.id,
        user_id=user.id,
        task_description="Fix insecure authentication comparison in src/auth.py",
        privacy_mode="standard",
        budget_limit_usd=5.00
    )
    db.add(session)
    db.commit()
    print("STEP 4: Coding session started with $5.00 budget limit.")

    # Step 8 & 9: Generate Bad Patch, Reject it, Verify File Unchanged
    bad_patch = (
        "--- src/auth.py\n"
        "+++ src/auth.py\n"
        "-    if password == stored_password:\n"
        "+    return True # Bypass all auth\n"
    )
    approval_bad = ActionApprovalEngine.request_approval(
        db=db,
        session_id=session.id,
        step_number=1,
        action_type=ActionType.PROPOSE_PATCH,
        target_path="src/auth.py",
        patch_diff=bad_patch,
        repo_path=temp_repo
    )
    print(f"STEP 8: Bad patch proposed. Approval ID: {approval_bad.id} (Status: {approval_bad.status.value})")

    # Developer Rejects Bad Patch
    ActionApprovalEngine.decide(db, approval_bad.id, user.id, decision="reject", reason="Insecure bypass")
    print("STEP 9: Developer REJECTED bad patch.")
    
    # Verify file is 100% UNCHANGED
    with open(auth_file, "r", encoding="utf-8") as f:
        current_content = f.read()
    assert current_content == original_code
    print("VERIFIED: File on disk remains 100% untouched after rejection.")

    # Step 10 & 11: Generate Cryptographic Fix Patch & Approve
    good_patch = (
        "--- src/auth.py\n"
        "+++ src/auth.py\n"
        "-    if password == stored_password:\n"
        "+    import secrets\n"
        "+    if secrets.compare_digest(password, stored_password):\n"
    )
    approval_good = ActionApprovalEngine.request_approval(
        db=db,
        session_id=session.id,
        step_number=2,
        action_type=ActionType.PROPOSE_PATCH,
        target_path="src/auth.py",
        patch_diff=good_patch,
        repo_path=temp_repo
    )
    print(f"STEP 10: Cryptographic fix patch proposed. Approval ID: {approval_good.id}")

    # Developer Approves Good Patch
    ActionApprovalEngine.decide(db, approval_good.id, user.id, decision="approve")
    print("STEP 11: Developer APPROVED cryptographic fix patch.")

    # Apply the change
    new_auth_code = (
        "import secrets\n"
        "def verify_login(username, password, stored_password):\n"
        "    if secrets.compare_digest(password, stored_password):\n"
        "        return True\n"
        "    return False\n"
    )
    ToolExecutionEngine.apply_write_file(db, temp_repo, "src/auth.py", new_auth_code, approval_good.id)
    with open(auth_file, "r", encoding="utf-8") as f:
        applied_content = f.read()
    assert "compare_digest" in applied_content
    print("VERIFIED: Approved patch applied to disk successfully.")

    # Step 12: Run Project Tests via Sandboxed Shell Tool
    approval_test = ActionApprovalEngine.request_approval(
        db=db,
        session_id=session.id,
        step_number=3,
        action_type=ActionType.RUN_SHELL,
        command="pytest tests -v",
        repo_path=temp_repo
    )
    ActionApprovalEngine.decide(db, approval_test.id, user.id, decision="approve")
    test_run = ToolExecutionEngine.run_sandboxed_shell(db, temp_repo, "pytest tests -v", approval_test.id)
    print(f"STEP 12: Executed sandboxed tests. Exit code: {test_run['exit_code']}")
    assert test_run['exit_code'] == 0
    print("VERIFIED: Project tests pass with approved patch.")

    print("\n=== PRIORITY 5 COMPLETE WORKFLOW VERIFICATION PASSED ===")
    shutil.rmtree(temp_repo, ignore_errors=True)

if __name__ == "__main__":
    run_workflow_demonstration()

