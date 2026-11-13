import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    ForeignKey, Text, Enum, Index, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def gen_uuid() -> str:
    return str(uuid.uuid4())

class UserRole(str, enum.Enum):
    DEVELOPER = "developer"
    ADMIN = "admin"

class SessionStatus(str, enum.Enum):
    CREATED = "created"
    INDEXING = "indexing"
    PLANNING = "planning"
    RUNNING = "running"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    BUDGET_EXHAUSTED = "budget_exhausted"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    CANCELLED = "cancelled"

class StepStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"
    SKIPPED = "skipped"

class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class ActionType(str, enum.Enum):
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    DELETE_FILE = "delete_file"
    PROPOSE_PATCH = "propose_patch"
    RUN_SHELL = "run_shell"
    GIT_COMMIT = "git_commit"
    GIT_PUSH = "git_push"

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    password_salt = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.DEVELOPER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    budget = relationship("Budget", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

class Budget(Base):
    __tablename__ = "budgets"
    
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    limit_usd = Column(Float, default=10.00, nullable=False)
    spent_usd = Column(Float, default=0.00, nullable=False)
    reserved_usd = Column(Float, default=0.00, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="budget")
    transactions = relationship("BudgetTransaction", back_populates="budget", cascade="all, delete-orphan")

class BudgetTransaction(Base):
    __tablename__ = "budget_transactions"
    
    id = Column(String, primary_key=True, default=gen_uuid)
    budget_id = Column(String, ForeignKey("budgets.id"), index=True, nullable=False)
    session_id = Column(String, ForeignKey("sessions.id"), index=True, nullable=True)
    amount_usd = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)  # "reserve", "settle", "release", "refund", "manual_adjustment"
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    budget = relationship("Budget", back_populates="transactions")
    session = relationship("Session", back_populates="budget_transactions")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=gen_uuid)
    owner_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    repo_path = Column(String, nullable=False)
    is_confidential = Column(Boolean, default=False, nullable=False)
    detected_framework = Column(String, nullable=True)
    detected_language = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    owner = relationship("User", back_populates="projects")
    sessions = relationship("Session", back_populates="project", cascade="all, delete-orphan")
    file_cache = relationship("FileCache", back_populates="project", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, default=gen_uuid)
    project_id = Column(String, ForeignKey("projects.id"), index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    task_description = Column(Text, nullable=False)
    status = Column(Enum(SessionStatus), default=SessionStatus.CREATED, index=True, nullable=False)
    privacy_mode = Column(String, default="standard", nullable=False)  # "standard" or "local_only"
    budget_limit_usd = Column(Float, default=2.00, nullable=False)
    budget_spent_usd = Column(Float, default=0.00, nullable=False)
    
    # Checkpointing / Memory
    execution_plan = Column(JSON, default=list, nullable=False)
    current_step_index = Column(Integer, default=0, nullable=False)
    summary = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    project = relationship("Project", back_populates="sessions")
    user = relationship("User", back_populates="sessions")
    steps = relationship("AgentStep", back_populates="session", cascade="all, delete-orphan")
    model_calls = relationship("ModelCall", back_populates="session", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="session", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="session", cascade="all, delete-orphan")
    budget_transactions = relationship("BudgetTransaction", back_populates="session")

class AgentStep(Base):
    __tablename__ = "agent_steps"
    
    id = Column(String, primary_key=True, default=gen_uuid)
    session_id = Column(String, ForeignKey("sessions.id"), index=True, nullable=False)
    step_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(StepStatus), default=StepStatus.PENDING, nullable=False)
    action_type = Column(String, nullable=True)
    action_input = Column(JSON, nullable=True)
    action_output = Column(JSON, nullable=True)
    tokens_used = Column(Integer, default=0, nullable=False)
    cost_usd = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    session = relationship("Session", back_populates="steps")

class ModelCall(Base):
    __tablename__ = "model_calls"
    
    id = Column(String, primary_key=True, default=gen_uuid)
    session_id = Column(String, ForeignKey("sessions.id"), index=True, nullable=False)
    step_number = Column(Integer, nullable=False)
    provider = Column(String, index=True, nullable=False)  # "bifrost", "ollama", "groq", "openai", "fallback_test"
    model_name = Column(String, nullable=False)
    task_category = Column(String, nullable=False)
    input_tokens = Column(Integer, default=0, nullable=False)
    output_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    cost_usd = Column(Float, default=0.0, nullable=False)
    latency_ms = Column(Integer, default=0, nullable=False)
    cache_hit = Column(Boolean, default=False, nullable=False)
    baseline_tokens_estimated = Column(Integer, default=0, nullable=False)
    tokens_saved = Column(Integer, default=0, nullable=False)
    status = Column(String, default="success", nullable=False)  # "success", "failed", "fallback"
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    session = relationship("Session", back_populates="model_calls")

class FileCache(Base):
    __tablename__ = "file_caches"
    
    id = Column(String, primary_key=True, default=gen_uuid)
    project_id = Column(String, ForeignKey("projects.id"), index=True, nullable=False)
    relative_path = Column(String, index=True, nullable=False)
    content_hash = Column(String, nullable=False)
    ast_skeleton = Column(Text, nullable=True)
    symbols = Column(JSON, nullable=True)
    token_count_full = Column(Integer, default=0, nullable=False)
    token_count_skeleton = Column(Integer, default=0, nullable=False)
    last_inspected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    project = relationship("Project", back_populates="file_cache")
    __table_args__ = (Index("ix_project_path", "project_id", "relative_path", unique=True),)

class Approval(Base):
    __tablename__ = "approvals"
    
    id = Column(String, primary_key=True, default=gen_uuid)
    session_id = Column(String, ForeignKey("sessions.id"), index=True, nullable=False)
    step_number = Column(Integer, nullable=False)
    action_type = Column(Enum(ActionType), nullable=False)
    target_path = Column(String, nullable=True)
    command = Column(String, nullable=True)
    patch_diff = Column(Text, nullable=True)
    target_content_hash = Column(String, nullable=True)  # Hash of file before modification
    proposed_content_hash = Column(String, nullable=True) # Hash of proposed new content
    approval_token = Column(String, unique=True, nullable=False)
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, index=True, nullable=False)
    decision_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    decided_at = Column(DateTime, nullable=True)
    
    session = relationship("Session", back_populates="approvals")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=gen_uuid)
    session_id = Column(String, ForeignKey("sessions.id"), index=True, nullable=True)
    user_id = Column(String, index=True, nullable=False)
    event_type = Column(String, index=True, nullable=False) 
    # e.g., "privacy_block", "approval_granted", "approval_rejected", "provider_failover", "budget_exhausted", "tool_executed"
    severity = Column(String, default="info", nullable=False) # "info", "warning", "critical"
    details = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    session = relationship("Session", back_populates="audit_logs")

class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"
    
    id = Column(String, primary_key=True, default=gen_uuid)
    task_name = Column(String, nullable=False)
    baseline_tokens = Column(Integer, nullable=False)
    optimized_tokens = Column(Integer, nullable=False)
    tokens_saved = Column(Integer, nullable=False)
    percentage_saved = Column(Float, nullable=False)
    baseline_cost_usd = Column(Float, nullable=False)
    optimized_cost_usd = Column(Float, nullable=False)
    cost_saved_usd = Column(Float, nullable=False)
    execution_time_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

