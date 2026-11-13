import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db, SessionLocal
from app.auth.security import get_current_user
from app.models.entities import User, Session as CodingSession, Project, SessionStatus, ModelCall
from app.schemas.api_models import SessionCreate, SessionOut, SessionMessageIn
from app.agent.core import AgentCoreEngine

router = APIRouter(prefix="/sessions", tags=["Sessions"])

async def run_agent_background(session_id: str):
    """Background runner for autonomous agent task execution."""
    db = SessionLocal()
    try:
        agent = AgentCoreEngine(db, session_id)
        await agent.execute_task()
    finally:
        db.close()

@router.post("", response_model=SessionOut)
async def create_session(
    session_in: SessionCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creates a persistent coding session and triggers agent planning & execution."""
    project = db.query(Project).filter(Project.id == session_in.project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    privacy_mode = session_in.privacy_mode or ("local_only" if project.is_confidential else "standard")
    budget_limit = session_in.budget_limit_usd or 2.00

    new_session = CodingSession(
        project_id=project.id,
        user_id=current_user.id,
        task_description=session_in.task_description,
        status=SessionStatus.CREATED,
        privacy_mode=privacy_mode,
        budget_limit_usd=budget_limit,
        budget_spent_usd=0.0
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # Launch agent task
    background_tasks.add_task(run_agent_background, new_session.id)
    return new_session

@router.get("/{session_id}", response_model=SessionOut)
def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves session status and checkpoints."""
    session = db.query(CodingSession).filter(CodingSession.id == session_id, CodingSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.get("/{session_id}/trace")
def get_session_trace(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns step-by-step execution trace and model call history."""
    session = db.query(CodingSession).filter(CodingSession.id == session_id, CodingSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    calls = db.query(ModelCall).filter(ModelCall.session_id == session_id).all()
    return {
        "session_id": session_id,
        "status": session.status.value,
        "execution_plan": session.execution_plan,
        "model_calls": [
            {
                "step": c.step_number,
                "provider": c.provider,
                "model": c.model_name,
                "input_tokens": c.input_tokens,
                "output_tokens": c.output_tokens,
                "cost_usd": c.cost_usd,
                "latency_ms": c.latency_ms,
                "tokens_saved": c.tokens_saved
            }
            for c in calls
        ]
    }

