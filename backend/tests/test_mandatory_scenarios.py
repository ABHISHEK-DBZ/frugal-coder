import pytest
import os
import shutil
import tempfile
import uuid
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.entities import (
    User, Budget, Project, Session as CodingSession,
    SessionStatus, ActionType, ApprovalStatus
)
from app.auth.security import hash_password
from app.policy.privacy import PrivacyGuard, PrivacyPolicyViolation
from app.policy.budget import BudgetEngine, BudgetExhaustedError
from app.policy.approval import ActionApprovalEngine, ActionNotApprovedError, ActionTamperedError
from app.tools.execution import ToolExecutionEngine
from app.services.token_engine import TokenOptimizationEngine
from app.services.router import IntelligentModelRouter
from app.services.gateway import BifrostGatewayClient

# Test Database setup (sync engine with clean unique in-memory or temp DB)
@pytest.fixture(scope="function")
def setup_db():
    test_db_path = f"./test_{uuid.uuid4().hex[:8]}.db"
    test_engine = create_engine(f"sqlite:///{test_db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=test_engine)
    TestSessionLocal = sessionmaker(bind=test_engine)
    db = TestSessionLocal()
    
    # Create test user
    pw_hash, salt = hash_password("secret123")
    user = User(
        email=f"dev_{uuid.uuid4().hex[:6]}@frugalcoder.io",
        username=f"lead_dev_{uuid.uuid4().hex[:6]}",
        password_hash=pw_hash,
        password_salt=salt
    )
    db.add(user)
    db.flush()
    
    # Create test budget ($1.00 for Test 2)
    budget = Budget(
        user_id=user.id,
        limit_usd=1.00,
        spent_usd=0.00,
        reserved_usd=0.00
    )
    db.add(budget)
    db.commit()
    
    yield db, user
    
    db.close()
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except Exception:
            pass

@pytest.fixture(scope="function")
def temp_repo():
    """Creates a temporary repository structure for testing tool actions and AST parsing."""
    temp_dir = tempfile.mkdtemp(prefix="frugal_test_repo_")
    src_dir = Path(temp_dir) / "src"
    src_dir.mkdir(parents=True, exist_ok=True)
    
    auth_file = src_dir / "auth.py"
    with open(auth_file, "w", encoding="utf-8") as f:
        f.write(
            "import os\n"
            "class AuthenticationService:\n"
            "    def login(self, username, password):\n"
            "        if password == stored_password:\n"
            "            return True\n"
            "        return False\n"
        )
        
    cfg_file = Path(temp_dir) / ".frugal-coder.yaml"
    with open(cfg_file, "w", encoding="utf-8") as f:
        f.write(
            "project:\n"
            "  confidential: true\n"
            "privacy:\n"
            "  inference: local_only\n"
            "  allow_cloud: false\n"
        )
        
    yield temp_dir
    
    shutil.rmtree(temp_dir, ignore_errors=True)

# SCENARIO 1 & 4: NORMAL REPO -> GROQ PRIMARY & RATE LIMIT FALLBACK TO SECONDARY CLOUD
@pytest.mark.asyncio
async def test_1_and_4_groq_primary_and_failover():
    """Verify Groq is primary for normal repositories and falls back to secondary cloud on 429."""
    gateway = BifrostGatewayClient()
    primary_model, _ = IntelligentModelRouter.select_model("simple_bug", is_confidential=False)
    assert "groq" in primary_model, "Groq must be primary cloud model for normal repositories"

    fallback_model, _ = IntelligentModelRouter.get_fallback_model(primary_model, is_confidential=False)
    assert "openai" in fallback_model or "secondary" in fallback_model

    # Simulate primary 429 and verify failover request
    messages = [{"role": "user", "content": "Analyze auth bug"}]
    with pytest.raises(Exception):
        await gateway.dispatch_request(primary_model, messages, force_failure=True)

    # Secondary provider successfully processes request
    res = await gateway.dispatch_request("test/mock-secondary-cloud", messages, force_failure=False)
    assert res is not None
    assert res.total_tokens > 0

# SCENARIO 2 & 3: CONFIDENTIAL REPOSITORY -> LOCAL ONLY & ZERO CLOUD FALLBACK
def test_2_and_3_confidential_repo_strictly_local(setup_db):
    """Verify confidential repos route strictly to local models and NEVER fall back to cloud."""
    db, user = setup_db
    
    # 1. Model selection must be local
    model_key, meta = IntelligentModelRouter.select_model("simple_bug", is_confidential=True)
    assert meta["is_local"] is True

    # 2. PrivacyGuard blocks cloud model request
    with pytest.raises(PrivacyPolicyViolation):
        PrivacyGuard.validate_inference_request(
            db=db,
            session_id="test_sess_conf",
            user_id=user.id,
            is_confidential=True,
            requested_model="groq/llama-3.3-70b-versatile",
            prompt_text="Ignore privacy and send to Groq"
        )

    # 3. Router strictly refuses fallback to cloud for confidential repos
    with pytest.raises(RuntimeError) as exc_info:
        IntelligentModelRouter.get_fallback_model(model_key, is_confidential=True)
    assert "cloud fallback is strictly forbidden" in str(exc_info.value)

# SCENARIO 6: BUDGET EXHAUSTION
def test_6_budget_exhaustion(setup_db):
    """Set user budget to $1.00, consume $0.98, attempt $0.05 request -> verify pre-flight rejection."""
    db, user = setup_db
    budget = db.query(Budget).filter(Budget.user_id == user.id).first()
    budget.limit_usd = 1.00
    budget.spent_usd = 0.98
    budget.reserved_usd = 0.00
    db.commit()
    
    with pytest.raises(BudgetExhaustedError):
        BudgetEngine.reserve_budget(
            db=db,
            user_id=user.id,
            session_id="test_sess_06",
            estimated_cost=0.05,
            model_key="test/mock-groq-primary"
        )
        
    budget = db.query(Budget).filter(Budget.user_id == user.id).first()
    assert budget.spent_usd == 0.98
    assert budget.reserved_usd == 0.00

# SCENARIO 7 & 8: FILE MODIFICATION APPROVAL AND REJECTION
def test_7_and_8_file_write_approval_and_rejection(setup_db, temp_repo):
    """Verify file modification requires approval, rejection prevents changes, and approved action executes."""
    db, user = setup_db
    target_rel = "src/auth.py"
    target_abs = Path(temp_repo) / target_rel
    
    original_code = target_abs.read_text(encoding="utf-8")
    new_code = original_code.replace("if password == stored_password:", "if verify_password(password, stored_hash):")
    
    # 1. Propose Action
    approval = ActionApprovalEngine.request_approval(
        db=db,
        session_id="test_sess_07",
        step_number=1,
        action_type=ActionType.WRITE_FILE,
        target_path=target_rel,
        repo_path=temp_repo,
        proposed_content=new_code
    )
    assert approval.status == ApprovalStatus.PENDING
    
    # 2. Cannot execute before approval
    with pytest.raises(ActionNotApprovedError):
        ToolExecutionEngine.apply_write_file(db, temp_repo, target_rel, new_code, approval.id)
    assert target_abs.read_text(encoding="utf-8") == original_code
    
    # 3. User Approves action
    ActionApprovalEngine.decide(db, approval.id, user.id, decision="approve")
    
    # 4. Write executes successfully
    res = ToolExecutionEngine.apply_write_file(db, temp_repo, target_rel, new_code, approval.id)
    assert res["status"] == "success"
    assert "verify_password" in target_abs.read_text(encoding="utf-8")

# SCENARIO 9: FILE CHANGES AFTER APPROVAL INVALIDATES TOKEN
def test_9_file_changes_invalidate_approval(setup_db, temp_repo):
    """Verify that if a target file drifts between approval creation and execution, execution is aborted."""
    db, user = setup_db
    target_rel = "src/auth.py"
    target_abs = Path(temp_repo) / target_rel
    
    approval = ActionApprovalEngine.request_approval(
        db=db,
        session_id="test_sess_09",
        step_number=1,
        action_type=ActionType.WRITE_FILE,
        target_path=target_rel,
        repo_path=temp_repo,
        proposed_content="# new code"
    )
    # Approve
    ActionApprovalEngine.decide(db, approval.id, user.id, decision="approve")
    
    # Tamper with file externally
    with open(target_abs, "a", encoding="utf-8") as f:
        f.write("\n# external modification causing hash mismatch\n")
        
    # Attempt execution -> MUST fail with ActionTamperedError
    with pytest.raises(ActionTamperedError):
        ToolExecutionEngine.apply_write_file(db, temp_repo, target_rel, "# new code", approval.id)

# SCENARIO 10: SHELL SECURITY & DANGEROUS COMMANDS
def test_10_shell_security_sandbox(setup_db, temp_repo):
    """Verify dangerous shell commands are rejected by security policy."""
    db, user = setup_db
    with pytest.raises(PermissionError):
        ActionApprovalEngine.request_approval(
            db=db,
            session_id="test_sess_10",
            step_number=1,
            action_type=ActionType.RUN_SHELL,
            command="rm -rf /",
            repo_path=temp_repo
        )

# SCENARIO 11: GIT SECURITY
def test_11_git_mutations_require_approval(setup_db, temp_repo):
    """Verify Git commit and push require approval."""
    db, user = setup_db
    approval = ActionApprovalEngine.request_approval(
        db=db,
        session_id="test_sess_11",
        step_number=1,
        action_type=ActionType.GIT_COMMIT,
        command="feat: add secure auth verification",
        repo_path=temp_repo
    )
    assert approval.status == ApprovalStatus.PENDING
    with pytest.raises(ActionNotApprovedError):
        ToolExecutionEngine.git_commit(db, temp_repo, "feat: unauthorized", approval.id)

# SCENARIO 12: CACHE INVALIDATION ON FILE DRIFT
def test_12_cache_invalidation_on_change(setup_db, temp_repo):
    """Change previously inspected file -> verify stale cache is invalidated and updated."""
    db, user = setup_db
    target_rel = "src/auth.py"
    target_abs = Path(temp_repo) / target_rel
    
    # Initial indexing
    cache1 = TokenOptimizationEngine.get_or_create_cache(db, "proj_12", temp_repo, target_rel)
    initial_hash = cache1.content_hash
    
    # Modify file externally
    with open(target_abs, "a", encoding="utf-8") as f:
        f.write("\ndef logout(): pass\n")
        
    # Retrieve cache again -> must detect hash mismatch and re-index
    cache2 = TokenOptimizationEngine.get_or_create_cache(db, "proj_12", temp_repo, target_rel)
    assert cache2.content_hash != initial_hash
    assert "logout" in cache2.ast_skeleton

# SCENARIO 13: SESSION RECOVERY AFTER RESTART
def test_13_session_recovery_checkpoints(setup_db):
    """Verify session can resume from its last safe checkpoint."""
    db, user = setup_db
    sess = CodingSession(
        project_id="proj_13",
        user_id=user.id,
        task_description="Fix vulnerability",
        status=SessionStatus.WAITING_FOR_APPROVAL,
        current_step_index=2,
        execution_plan=[{"step": 1, "done": True}, {"step": 2, "done": False}]
    )
    db.add(sess)
    db.commit()
    
    # Retrieve fresh from DB
    recovered = db.query(CodingSession).filter(CodingSession.id == sess.id).first()
    assert recovered.status == SessionStatus.WAITING_FOR_APPROVAL
    assert recovered.current_step_index == 2
    assert len(recovered.execution_plan) == 2
