from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.entities import UserRole, SessionStatus, StepStatus, ApprovalStatus, ActionType

# User Schemas
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: str
    email: str
    username: str
    role: UserRole
    is_active: bool
    created_at: datetime
    class Config:
        orm_mode = True

class TokenOut(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

# Budget Schemas
class BudgetOut(BaseModel):
    id: str
    user_id: str
    limit_usd: float
    spent_usd: float
    reserved_usd: float
    remaining_usd: float
    created_at: datetime
    class Config:
        orm_mode = True

class BudgetUpdate(BaseModel):
    limit_usd: float

# Project Schemas
class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_confidential: Optional[bool] = None

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    repo_path: str
    is_confidential: bool = False

class ProjectOut(BaseModel):
    id: str
    owner_id: str
    name: str
    description: Optional[str]
    repo_path: str
    is_confidential: bool
    detected_framework: Optional[str]
    detected_language: Optional[str]
    created_at: datetime
    class Config:
        orm_mode = True

# Session Schemas
class SessionCreate(BaseModel):
    project_id: str
    task_description: str
    budget_limit_usd: Optional[float] = None
    privacy_mode: Optional[str] = None

class SessionOut(BaseModel):
    id: str
    project_id: str
    user_id: str
    task_description: str
    status: SessionStatus
    privacy_mode: str
    budget_limit_usd: float
    budget_spent_usd: float
    execution_plan: list
    current_step_index: int
    summary: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    class Config:
        orm_mode = True

class SessionMessageIn(BaseModel):
    instruction: str

# Approval Schemas
class ApprovalOut(BaseModel):
    id: str
    session_id: str
    step_number: int
    action_type: ActionType
    target_path: Optional[str]
    command: Optional[str]
    patch_diff: Optional[str]
    approval_token: str
    status: ApprovalStatus
    created_at: datetime
    class Config:
        orm_mode = True

class ApprovalDecisionIn(BaseModel):
    decision: str  # "approve" or "reject"
    reason: Optional[str] = None

# Analytics Schemas
class AnalyticsOverview(BaseModel):
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    actual_cost_usd: float
    estimated_cost_savings_usd: float
    baseline_tokens: int
    optimized_tokens: int
    token_savings_pct: float
    cache_hits: int
    total_tool_calls: int
    completed_tasks: int
    failed_tasks: int
    task_success_rate: float

