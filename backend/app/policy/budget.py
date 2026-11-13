import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.models.entities import Budget, BudgetTransaction, AuditLog
from app.services.router import MODEL_REGISTRY

logger = logging.getLogger(__name__)

class BudgetExhaustedError(Exception):
    """Raised when an action would exceed user or session budget limits."""
    pass

class BudgetEngine:
    """
    Enforces individual spending limits atomically before model dispatch.
    Implements 2-phase commit: Pre-call estimation & reservation -> Post-call reconciliation.
    """

    @classmethod
    def calculate_cost(cls, model_key: str, input_tokens: int, output_tokens: int) -> float:
        """Calculates exact dollar cost using model registry pricing."""
        meta = MODEL_REGISTRY.get(model_key, {})
        cost_in = (input_tokens / 1000.0) * meta.get("cost_per_1k_input", 0.0)
        cost_out = (output_tokens / 1000.0) * meta.get("cost_per_1k_output", 0.0)
        return round(cost_in + cost_out, 6)

    @classmethod
    def estimate_max_cost(cls, model_key: str, estimated_input_tokens: int, max_output_tokens: int = 1000) -> float:
        """Estimates ceiling cost for pre-call budget reservation."""
        return cls.calculate_cost(model_key, estimated_input_tokens, max_output_tokens)

    @classmethod
    def reserve_budget(
        cls,
        db: Session,
        user_id: str,
        session_id: str,
        estimated_cost: float,
        model_key: str
    ) -> BudgetTransaction:
        """
        Atomically checks remaining budget and reserves estimated cost.
        Throws BudgetExhaustedError if limit would be breached.
        """
        # Lock user budget row
        budget = db.query(Budget).filter(Budget.user_id == user_id).with_for_update().first()
        if not budget:
            # Create default budget for user
            budget = Budget(user_id=user_id, limit_usd=10.0, spent_usd=0.0, reserved_usd=0.0)
            db.add(budget)
            db.flush()

        # Atomic pre-flight check
        projected_spend = budget.spent_usd + budget.reserved_usd + estimated_cost
        if projected_spend > budget.limit_usd:
            # Record audit event
            audit = AuditLog(
                session_id=session_id,
                user_id=user_id,
                event_type="budget_exhausted",
                severity="warning",
                details={
                    "limit_usd": budget.limit_usd,
                    "spent_usd": budget.spent_usd,
                    "reserved_usd": budget.reserved_usd,
                    "attempted_cost_usd": estimated_cost,
                    "model": model_key
                }
            )
            db.add(audit)
            db.commit()
            
            logger.warning(f"BUDGET EXHAUSTED: User {user_id} attempted ${estimated_cost:.4f} but has ${budget.limit_usd - budget.spent_usd:.4f} left.")
            raise BudgetExhaustedError(
                f"Spending limit reached. Available budget: ${max(0.0, budget.limit_usd - budget.spent_usd - budget.reserved_usd):.4f}. "
                f"Estimated call cost: ${estimated_cost:.4f}."
            )

        # Place reservation
        budget.reserved_usd += estimated_cost
        
        transaction = BudgetTransaction(
            budget_id=budget.id,
            session_id=session_id,
            amount_usd=estimated_cost,
            transaction_type="reserve",
            description=f"Pre-flight reservation for model {model_key}"
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    @classmethod
    def reconcile_usage(
        cls,
        db: Session,
        user_id: str,
        session_id: str,
        reservation_tx_id: str,
        actual_input_tokens: int,
        actual_output_tokens: int,
        model_key: str
    ) -> float:
        """
        Settles reservation with actual usage and releases unused reserved funds.
        """
        budget = db.query(Budget).filter(Budget.user_id == user_id).with_for_update().first()
        res_tx = db.query(BudgetTransaction).filter(BudgetTransaction.id == reservation_tx_id).first()
        
        reserved_amount = res_tx.amount_usd if res_tx else 0.0
        actual_cost = cls.calculate_cost(model_key, actual_input_tokens, actual_output_tokens)
        
        # Settle
        budget.reserved_usd = max(0.0, budget.reserved_usd - reserved_amount)
        budget.spent_usd += actual_cost
        
        settle_tx = BudgetTransaction(
            budget_id=budget.id,
            session_id=session_id,
            amount_usd=actual_cost,
            transaction_type="settle",
            description=f"Settled actual usage for {model_key} ({actual_input_tokens} in, {actual_output_tokens} out)"
        )
        db.add(settle_tx)
        db.commit()
        return actual_cost

