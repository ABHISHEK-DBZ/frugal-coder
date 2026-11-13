from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.security import get_current_user
from app.models.entities import User, Approval, ApprovalStatus, Project, Session as CodingSession, ActionType
from app.schemas.api_models import ApprovalOut, ApprovalDecisionIn
from app.policy.approval import ActionApprovalEngine
from app.services.repository import resolve_safe_path
from app.tools.execution import ToolExecutionEngine
from app.events.hub import event_hub

router = APIRouter(prefix="/approvals", tags=["Approvals"])

@router.get("", response_model=List[ApprovalOut])
def list_pending_approvals(
    session_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists pending action approval proposals."""
    query = db.query(Approval).join(CodingSession).filter(CodingSession.user_id == current_user.id)
    if session_id:
        query = query.filter(Approval.session_id == session_id)
    return query.filter(Approval.status == ApprovalStatus.PENDING).all()

@router.post("/{approval_id}/decision")
async def decide_approval(
    approval_id: str,
    decision_in: ApprovalDecisionIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submits user decision: 'approve' or 'reject'.
    If approved, executes the verified mutating operation immediately.
    """
    approval = db.query(Approval).join(CodingSession).filter(
        Approval.id == approval_id,
        CodingSession.user_id == current_user.id
    ).first()
    
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")

    decided_approval = ActionApprovalEngine.decide(
        db, approval.id, current_user.id, decision_in.decision, decision_in.reason
    )

    session = db.query(CodingSession).filter(CodingSession.id == approval.session_id).first()
    project = db.query(Project).filter(Project.id == session.project_id).first()

    execution_result = None
    if decision_in.decision == "approve":
        # Execute the approved action safely
        if approval.action_type in [ActionType.WRITE_FILE, ActionType.PROPOSE_PATCH]:
            if approval.patch_diff:
                # If unified diff has proposed patch, parse and apply or write proposed content
                if approval.target_path:
                    # Look up if proposed content is tracked, or apply patch
                    full_target = resolve_safe_path(project.repo_path, approval.target_path)
                    if full_target.exists():
                        with open(full_target, "r", encoding="utf-8") as f:
                            current_content = f.read()
                        
                        # Apply patch logic
                        lines = approval.patch_diff.splitlines()
                        removals = [l[1:].strip() for l in lines if l.startswith("-") and not l.startswith("---")]
                        additions = [l[1:].strip() for l in lines if l.startswith("+") and not l.startswith("+++")]
                        
                        if removals and additions:
                            target_sub = removals[0]
                            replacement_sub = additions[0]
                            execution_result = ToolExecutionEngine.apply_patch(
                                db, project.repo_path, approval.target_path,
                                original_snippet=target_sub,
                                replacement_snippet=replacement_sub,
                                approval_id=approval.id
                            )
                        else:
                            execution_result = {"status": "patch_applied", "target": approval.target_path}
                    else:
                        execution_result = {"status": "target_file_not_found", "target": approval.target_path}
            elif approval.command:
                # Run shell
                execution_result = ToolExecutionEngine.run_sandboxed_shell(
                    db, project.repo_path, approval.command, approval.id
                )
        elif approval.action_type == ActionType.RUN_SHELL:
            execution_result = ToolExecutionEngine.run_sandboxed_shell(
                db, project.repo_path, approval.command, approval.id
            )
        elif approval.action_type == ActionType.GIT_COMMIT:
            execution_result = ToolExecutionEngine.git_commit(
                db, project.repo_path, approval.command or "Commit approved by user", approval.id
            )

        # Notify clients
        await event_hub.broadcast_event(session.id, "action_executed", {
            "approval_id": approval.id,
            "result": execution_result
        })
    else:
        await event_hub.broadcast_event(session.id, "action_rejected", {
            "approval_id": approval.id,
            "reason": decision_in.reason
        })

    return {
        "approval_id": approval.id,
        "status": decided_approval.status.value,
        "execution_result": execution_result
    }

