import logging
from sqlalchemy.orm import Session
from app.models.entities import AuditLog
from app.services.router import MODEL_REGISTRY

logger = logging.getLogger(__name__)

class PrivacyPolicyViolation(Exception):
    """Raised when an action violates repository confidentiality."""
    pass

class PrivacyGuard:
    """
    Independent Policy Engine Boundary for Confidential Repositories.
    Enforces local-only inference at the architectural level outside LLM control.
    Prompt injection CANNOT override this policy (Test 3 & Test C).
    """

    @classmethod
    def validate_inference_request(
        cls,
        db: Session,
        session_id: str,
        user_id: str,
        is_confidential: bool,
        requested_model: str,
        prompt_text: str = ""
    ) -> bool:
        """
        Validates model inference request against confidentiality rules.
        Throws PrivacyPolicyViolation and records critical audit log if violated.
        """
        if not is_confidential:
            return True
            
        model_meta = MODEL_REGISTRY.get(requested_model, {})
        is_local = model_meta.get("is_local", False)
        provider = model_meta.get("provider", "unknown")
        
        # Check if requested model or provider is cloud-based
        if not is_local or provider in ["openai", "groq", "anthropic"]:
            # Record security audit event
            audit = AuditLog(
                session_id=session_id,
                user_id=user_id,
                event_type="privacy_block",
                severity="critical",
                details={
                    "reason": "Cloud inference attempted on confidential repository",
                    "requested_model": requested_model,
                    "provider": provider,
                    "prompt_sample": prompt_text[:100] if prompt_text else ""
                }
            )
            db.add(audit)
            db.commit()
            
            logger.error(f"PRIVACY BLOCKED: Confidential repository session {session_id} attempted cloud model {requested_model}")
            raise PrivacyPolicyViolation(
                f"Confidential Repository Policy Violation: Cloud model '{requested_model}' ({provider}) is strictly prohibited. "
                "Only local models are authorized."
            )
            
        return True

