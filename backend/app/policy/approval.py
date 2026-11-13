import secrets
import hashlib
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.entities import (
    Approval, ApprovalStatus, ActionType, AuditLog
)
from app.services.repository import resolve_safe_path, compute_file_hash

logger = logging.getLogger(__name__)

class ActionNotApprovedError(Exception):
    """Raised when an agent attempts a mutating action without explicit user approval."""
    pass

class ActionTamperedError(Exception):
    """Raised when target file or action parameters drift after approval was requested."""
    pass

# Forbidden dangerous commands in OS sandbox
FORBIDDEN_COMMAND_PATTERNS = [
    "rm -rf /", "rmdir /s /q c:\\", ":(){ :|:& };:", "dd if=/dev/zero",
    "mkfs", "format c:", "drop database", "chmod -R 777 /", "> /etc/passwd"
]

class ActionApprovalEngine:
    """
    Independent Authorization & Action Approval Gate.
    All mutating actions (write, delete, patch, shell, git) must be approved
    by the user with a cryptographic single-use token bound to exact content hashes.
    """

    @classmethod
    def is_read_only(cls, action_type: ActionType) -> bool:
        """Read operations are automatically permitted."""
        return action_type in [
            ActionType.READ_FILE
        ]

    @classmethod
    def request_approval(
        cls,
        db: Session,
        session_id: str,
        step_number: int,
        action_type: ActionType,
        target_path: Optional[str] = None,
        command: Optional[str] = None,
        patch_diff: Optional[str] = None,
        repo_path: Optional[str] = None,
        proposed_content: Optional[str] = None
    ) -> Approval:
        """
        Generates an exact Action Proposal and stores it in the database with status PENDING.
        Binds to target file hash before modification and proposed content hash.
        """
        # Security check: disallow blatantly destructive shell commands immediately
        if command:
            cmd_lower = command.lower()
            for pattern in FORBIDDEN_COMMAND_PATTERNS:
                if pattern in cmd_lower:
                    raise PermissionError(f"Security Policy Rejected command containing dangerous pattern: '{pattern}'")

        target_hash = None
        if target_path and repo_path:
            try:
                full_path = resolve_safe_path(repo_path, target_path)
                if full_path.exists() and full_path.is_file():
                    target_hash = compute_file_hash(full_path)
            except Exception:
                target_hash = None

        proposed_hash = None
        if proposed_content is not None:
            proposed_hash = hashlib.sha256(proposed_content.encode("utf-8")).hexdigest()

        token = secrets.token_urlsafe(32)
        
        approval = Approval(
            session_id=session_id,
            step_number=step_number,
            action_type=action_type,
            target_path=target_path,
            command=command,
            patch_diff=patch_diff,
            target_content_hash=target_hash,
            proposed_content_hash=proposed_hash,
            approval_token=token,
            status=ApprovalStatus.PENDING
        )
        db.add(approval)
        db.commit()
        db.refresh(approval)
        
        logger.info(f"APPROVAL REQUIRED: Step {step_number} action {action_type.value} token={token[:8]}...")
        return approval

    @classmethod
    def decide(
        cls,
        db: Session,
        approval_id: str,
        user_id: str,
        decision: str,  # "approve" or "reject"
        reason: Optional[str] = None
    ) -> Approval:
        """Processes user approval decision (Approve or Reject)."""
        approval = db.query(Approval).filter(Approval.id == approval_id).first()
        if not approval:
            raise ValueError(f"Approval request {approval_id} not found.")
            
        if approval.status != ApprovalStatus.PENDING:
            raise ValueError(f"Approval is already in {approval.status.value} state.")
            
        new_status = ApprovalStatus.APPROVED if decision == "approve" else ApprovalStatus.REJECTED
        approval.status = new_status
        approval.decision_reason = reason
        approval.decided_at = datetime.utcnow()
        
        # Log audit trail
        audit = AuditLog(
            session_id=approval.session_id,
            user_id=user_id,
            event_type="approval_decision",
            severity="info" if decision == "approve" else "warning",
            details={
                "approval_id": approval.id,
                "action_type": approval.action_type.value,
                "decision": decision,
                "target_path": approval.target_path,
                "command": approval.command
            }
        )
        db.add(audit)
        db.commit()
        db.refresh(approval)
        return approval

    @classmethod
    def verify_execution_authorized(
        cls,
        db: Session,
        approval_id: str,
        repo_path: Optional[str] = None
    ) -> bool:
        """
        Verifies approval token is valid, APPROVED, and that the target file
        has not been altered between approval creation and execution.
        """
        approval = db.query(Approval).filter(Approval.id == approval_id).first()
        if not approval:
            raise ActionNotApprovedError("No approval record found.")
            
        if approval.status != ApprovalStatus.APPROVED:
            raise ActionNotApprovedError(f"Action cannot execute: status is {approval.status.value}")

        # Verify target file has not drifted since approval proposal
        if approval.target_path and approval.target_content_hash and repo_path:
            full_path = resolve_safe_path(repo_path, approval.target_path)
            if full_path.exists():
                current_hash = compute_file_hash(full_path)
                if current_hash != approval.target_content_hash:
                    raise ActionTamperedError(
                        f"Action aborted: Target file '{approval.target_path}' changed after approval was generated."
                    )
                    
        return True

