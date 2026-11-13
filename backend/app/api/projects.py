from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.security import get_current_user
from app.models.entities import User, Project
from app.schemas.api_models import ProjectCreate, ProjectUpdate, ProjectOut
from app.services.repository import detect_confidentiality, detect_language_and_framework, get_repository_tree

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("", response_model=ProjectOut)
def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Registers a local repository, inspects confidentiality, language, and framework."""
    resolved_path = Path(project_in.repo_path).resolve()
    if not resolved_path.exists() or not resolved_path.is_dir():
        raise HTTPException(status_code=400, detail=f"Local path does not exist: {project_in.repo_path}")

    # Detect confidentiality from .frugal-coder.yaml
    conf_meta = detect_confidentiality(str(resolved_path))
    is_confidential = project_in.is_confidential or conf_meta.get("is_confidential", False)

    # Detect language and framework
    lang_info = detect_language_and_framework(str(resolved_path))

    project = Project(
        owner_id=current_user.id,
        name=project_in.name,
        description=project_in.description,
        repo_path=str(resolved_path),
        is_confidential=is_confidential,
        detected_language=lang_info.get("language"),
        detected_framework=lang_info.get("framework")
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.get("", response_model=List[ProjectOut])
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists projects owned by current user."""
    return db.query(Project).filter(Project.owner_id == current_user.id).order_by(Project.created_at.desc()).all()

@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates project properties including privacy classification with audit trail."""
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project_update.name is not None:
        project.name = project_update.name
    if project_update.description is not None:
        project.description = project_update.description
    if project_update.is_confidential is not None:
        from app.models.entities import AuditLog
        old_val = "Confidential (Local-only)" if project.is_confidential else "Public/Standard (Bifrost/Groq)"
        new_val = "Confidential (Local-only)" if project_update.is_confidential else "Public/Standard (Bifrost/Groq)"
        
        project.is_confidential = project_update.is_confidential
        
        audit_entry = AuditLog(
            user_id=current_user.id,
            event_type="project_privacy_changed",
            severity="warning" if not project_update.is_confidential else "info",
            details={
                "project_id": project.id,
                "project_name": project.name,
                "previous_classification": old_val,
                "new_classification": new_val,
                "reason": "Explicit user update from UI confirmation"
            }
        )
        db.add(audit_entry)

    db.commit()
    db.refresh(project)
    return project

@router.get("/{project_id}/tree")
def get_project_tree(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves safe file tree of the project repository."""
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    return get_repository_tree(project.repo_path)

@router.get("/{project_id}/file")
def get_project_file_content(
    project_id: str,
    path: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Safely retrieves file content and AST metadata for the code editor."""
    from app.services.repository import resolve_safe_path, compute_file_hash
    from app.services.token_engine import TokenOptimizationEngine
    
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        target = resolve_safe_path(project.repo_path, path)
        if not target.exists() or not target.is_file():
            raise HTTPException(status_code=404, detail=f"File not found: {path}")

        with open(target, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        file_hash = compute_file_hash(target)
        cache = TokenOptimizationEngine.get_or_create_cache(db, project.id, project.repo_path, path)

        return {
            "relative_path": path,
            "content": content,
            "hash": file_hash,
            "ast_skeleton": cache.ast_skeleton,
            "token_count_full": cache.token_count_full,
            "token_count_skeleton": cache.token_count_skeleton,
            "symbols": cache.symbols or []
        }
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

