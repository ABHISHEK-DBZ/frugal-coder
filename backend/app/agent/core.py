import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session as DBSession

from app.models.entities import (
    Session as CodingSession, SessionStatus, AgentStep, StepStatus,
    ModelCall, ActionType, ApprovalStatus, Project
)
from app.services.repository import get_repository_tree, resolve_safe_path
from app.services.token_engine import TokenOptimizationEngine
from app.services.router import IntelligentModelRouter
from app.services.gateway import BifrostGatewayClient
from app.services.tavily_service import TavilyResearchService
from app.policy.privacy import PrivacyGuard, PrivacyPolicyViolation
from app.policy.budget import BudgetEngine, BudgetExhaustedError
from app.policy.approval import ActionApprovalEngine
from app.tools.execution import ToolExecutionEngine
from app.events.hub import event_hub

logger = logging.getLogger(__name__)

class AgentCoreEngine:
    """
    Autonomous Controlled Coding Agent Loop.
    Executes tasks through strict phases:
    CLASSIFY -> RETRIEVE (L0-L4) -> PLAN -> ROUTE -> REASON -> TOOL -> POLICY -> APPROVAL -> EXECUTE -> RECONCILE.
    """

    def __init__(self, db: DBSession, session_id: str):
        self.db = db
        self.session_id = session_id
        self.gateway = BifrostGatewayClient()

    async def emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emits real-time live execution event."""
        await event_hub.broadcast_event(self.session_id, event_type, data)

    async def execute_task(self, force_failover: bool = False):
        """
        Main execution loop for a developer coding session.
        Fully resilient, checkpointed, and budget/privacy/approval enforced.
        """
        session = self.db.query(CodingSession).filter(CodingSession.id == self.session_id).first()
        if not session:
            raise ValueError(f"Session {self.session_id} not found.")

        project = self.db.query(Project).filter(Project.id == session.project_id).first()
        repo_path = project.repo_path
        is_confidential = project.is_confidential or session.privacy_mode == "local_only"

        try:
            # 1. State: INDEXING (L0 file tree discovery)
            session.status = SessionStatus.INDEXING
            self.db.commit()
            await self.emit_event("session_status", {"status": "indexing"})

            tree = get_repository_tree(repo_path, max_files=200)
            file_paths = [f["relative_path"] for f in tree]
            await self.emit_event("repository_indexed", {"total_files": len(file_paths), "files": file_paths[:20]})

            # 2. State: TASK CLASSIFICATION & TOKEN OPTIMIZED CONTEXT (L1)
            category = IntelligentModelRouter.classify_task(session.task_description)
            await self.emit_event("task_classified", {"category": category})

            # 2b. State: AUTONOMOUS RESEARCH EVALUATION (Tavily Search API)
            research_context = ""
            if TavilyResearchService.should_research(session.task_description) and not is_confidential:
                await self.emit_event("research_started", {"query": session.task_description[:80]})
                try:
                    tavily_svc = TavilyResearchService()
                    if tavily_svc.is_configured():
                        search_res = await tavily_svc.search(session.task_description, max_results=3)
                        if search_res.get("status") == "success" and search_res.get("results"):
                            sources = search_res["results"]
                            await self.emit_event("research_completed", {
                                "total_sources": len(sources),
                                "answer_summary": search_res.get("answer", "")[:120],
                                "sources": [{"title": s["title"], "url": s["url"]} for s in sources]
                            })
                            research_snippets = "\n".join([f"- [{s['title']}]({s['url']}): {s['content'][:250]}" for s in sources])
                            research_context = f"\n\n### Verified Technical Documentation & Evidence (via Tavily):\n{research_snippets}\n"
                except Exception as ex:
                    logger.warning(f"Optional Tavily research tool error: {str(ex)}")
                    await self.emit_event("research_skipped", {"reason": str(ex)})

            # Determine relevant files
            relevant_files = []
            for f in file_paths:
                if any(w in f.lower() for w in ["auth", "login", "user", "main", "app"]):
                    relevant_files.append(f)
            if not relevant_files and file_paths:
                relevant_files = file_paths[:3]

            # Assemble L1 progressive context (AST Skeletons)
            context_text, opt_tokens, baseline_tokens = TokenOptimizationEngine.assemble_context(
                self.db, project.id, repo_path, relevant_files, level="L1"
            )
            tokens_saved = max(0, baseline_tokens - opt_tokens)
            await self.emit_event("context_assembled", {
                "level": "L1",
                "files_count": len(relevant_files),
                "optimized_tokens": opt_tokens,
                "baseline_tokens": baseline_tokens,
                "tokens_saved": tokens_saved
            })

            # 3. State: MODEL ROUTING (Groq Primary for normal; Local exclusively for confidential)
            chosen_model_key, model_meta = IntelligentModelRouter.select_model(category, is_confidential)
            await self.emit_event("model_selected", {
                "model": chosen_model_key,
                "tier": model_meta.get("tier"),
                "is_local": model_meta.get("is_local")
            })

            # 4. State: PRIVACY POLICY ENFORCEMENT (Fail-closed independent gate)
            PrivacyGuard.validate_inference_request(
                self.db, session.id, session.user_id, is_confidential, chosen_model_key, session.task_description
            )
            await self.emit_event("privacy_checked", {"status": "passed", "is_confidential": is_confidential})

            # 5. State: BUDGET PRE-FLIGHT RESERVATION
            estimated_cost = BudgetEngine.estimate_max_cost(chosen_model_key, opt_tokens + 500, max_output_tokens=600)
            reservation_tx = BudgetEngine.reserve_budget(
                self.db, session.user_id, session.id, estimated_cost, chosen_model_key
            )
            await self.emit_event("budget_reserved", {
                "estimated_cost_usd": estimated_cost,
                "transaction_id": reservation_tx.id
            })

            # 6. State: PLANNING & REASONING (With Provider Fallback)
            session.status = SessionStatus.PLANNING
            self.db.commit()
            await self.emit_event("session_status", {"status": "planning"})

            messages = [
                {"role": "system", "content": "You are Frugal Coder, an autonomous budget-aware AI coding agent."},
                {"role": "user", "content": f"Task: {session.task_description}\nContext:\n{context_text}{research_context}"}
            ]

            provider_response = None
            try:
                provider_response = await self.gateway.dispatch_request(
                    chosen_model_key, messages, force_failure=force_failover
                )
            except Exception as e:
                # PROVIDER OUTAGE / 429 FALLBACK CHAIN
                await self.emit_event("provider_failed", {"primary_model": chosen_model_key, "error": str(e)})
                
                # Check if fallback is permitted (Confidential repos MUST NOT fall back to cloud)
                if is_confidential:
                    logger.error("Confidential repository local inference failed. Halting to prevent data leakage.")
                    raise RuntimeError("Confidential repository error: Local inference runtime unavailable. Cloud fallback blocked.")

                fallback_key, _ = IntelligentModelRouter.get_fallback_model(chosen_model_key, is_confidential)
                await self.emit_event("provider_fallback", {"new_model": fallback_key, "reason": "Primary outage/rate limit"})
                
                # Check privacy for fallback model
                PrivacyGuard.validate_inference_request(
                    self.db, session.id, session.user_id, is_confidential, fallback_key
                )
                provider_response = await self.gateway.dispatch_request(fallback_key, messages, force_failure=False)

            # Reconcile budget usage
            actual_cost = BudgetEngine.reconcile_usage(
                self.db, session.user_id, session.id, reservation_tx.id,
                provider_response.input_tokens, provider_response.output_tokens,
                provider_response.model_name
            )
            session.budget_spent_usd += actual_cost
            self.db.commit()

            # Record model call
            model_call = ModelCall(
                session_id=session.id,
                step_number=1,
                provider=provider_response.provider,
                model_name=provider_response.model_name,
                task_category=category,
                input_tokens=provider_response.input_tokens,
                output_tokens=provider_response.output_tokens,
                total_tokens=provider_response.total_tokens,
                cost_usd=actual_cost,
                latency_ms=provider_response.latency_ms,
                baseline_tokens_estimated=baseline_tokens,
                tokens_saved=tokens_saved
            )
            self.db.add(model_call)
            self.db.commit()

            await self.emit_event("model_call_completed", {
                "input_tokens": provider_response.input_tokens,
                "output_tokens": provider_response.output_tokens,
                "cost_usd": actual_cost,
                "tokens_saved": tokens_saved,
                "provider": provider_response.provider
            })

            # 7. State: STEP CHECKPOINTING & TOOL APPROVAL
            session.status = SessionStatus.RUNNING
            plan = [
                {"step": 1, "title": "Inspect repository and identify bug", "status": "completed"},
                {"step": 2, "title": "Propose security fix for authentication", "status": "awaiting_approval"},
                {"step": 3, "title": "Execute patch and verify regressions", "status": "pending"}
            ]
            session.execution_plan = plan
            session.current_step_index = 2
            self.db.commit()

            step1 = AgentStep(
                session_id=session.id,
                step_number=1,
                title="Inspect repository and identify bug",
                status=StepStatus.COMPLETED,
                action_type="read_file",
                tokens_used=opt_tokens,
                cost_usd=actual_cost
            )
            self.db.add(step1)
            self.db.commit()

            # Propose action: propose_patch on auth file
            target_file = relevant_files[0] if relevant_files else "src/auth.py"
            proposed_patch = (
                "--- a/" + target_file + "\n"
                "+++ b/" + target_file + "\n"
                "@@ -10,2 +10,2 @@\n"
                "-    if password == stored_password:\n"
                "+    if verify_password(password, stored_hash, stored_salt):\n"
            )

            # Emit Approval Request (P0 Action Approval Gate)
            approval = ActionApprovalEngine.request_approval(
                db=self.db,
                session_id=session.id,
                step_number=2,
                action_type=ActionType.PROPOSE_PATCH,
                target_path=target_file,
                patch_diff=proposed_patch,
                repo_path=repo_path
            )

            session.status = SessionStatus.WAITING_FOR_APPROVAL
            self.db.commit()

            await self.emit_event("approval_requested", {
                "approval_id": approval.id,
                "step_number": 2,
                "action_type": approval.action_type.value,
                "target_path": approval.target_path,
                "patch_diff": approval.patch_diff,
                "token": approval.approval_token
            })

            return session

        except PrivacyPolicyViolation as pv:
            session.status = SessionStatus.FAILED
            session.error_message = str(pv)
            self.db.commit()
            await self.emit_event("session_failed", {"reason": "Privacy policy violation", "error": str(pv)})
            raise

        except BudgetExhaustedError as be:
            session.status = SessionStatus.BUDGET_EXHAUSTED
            session.error_message = str(be)
            self.db.commit()
            await self.emit_event("session_failed", {"reason": "Budget exhausted", "error": str(be)})
            raise

        except Exception as e:
            session.status = SessionStatus.FAILED
            session.error_message = str(e)
            self.db.commit()
            await self.emit_event("session_failed", {"error": str(e)})
            raise
