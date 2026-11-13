# IMPLEMENTATION PLAN — FRUGAL CODER

## Phase 1: Workspace Inspection & Architecture (Completed)
- [x] Extract and read entire `Hackathon Strategy Analysis.pdf`.
- [x] Inspect Python, Node, Git, system libraries.
- [x] Create `PROJECT_STATUS.md`, `ARCHITECTURE.md`, `IMPLEMENTATION_PLAN.md`, `TASK_TRACKER.md`.

## Phase 2: Database Models & Backend Foundation
- [ ] Initialize Python backend package structure under `backend/`.
- [ ] Configure `SQLAlchemy` async engine with SQLite `frugal_coder.db`.
- [ ] Implement database models:
  - `User`, `Project`, `Session`, `AgentStep`, `ModelCall`
  - `Budget`, `BudgetTransaction`, `FileCache`, `Approval`, `AuditLog`, `BenchmarkRun`
- [ ] Implement Authentication & User Management (JWT, secure PBKDF2 hashing, user registration/login, user spending limits).
- [ ] Implement Project & Repository Management (Safe file tree scanner, path-traversal guard, symbol extractor, `.frugal-coder.yaml` reader).

## Phase 3: Token Optimization Engine & Model Router
- [ ] Implement AST parser & context compressor (Python AST visitor + JS/TS regex grammar for L1 skeletons).
- [ ] Implement L0-L4 progressive context resolver.
- [ ] Implement content hashing (SHA-256) & cache invalidation engine.
- [ ] Implement Intelligent Model Router with task classification (classification, summarization, simple_bug, multi_file, architecture) and model tiering.

## Phase 4: Bifrost Gateway & AI Provider Integration
- [ ] Implement Bifrost client / OpenAI-compatible unified provider client with fallback chain.
- [ ] Implement provider registry: Ollama (local), Groq (fast), OpenAI (reasoning), Anthropic, and Fallback Test Provider.
- [ ] Implement Virtual Key simulator & gateway health check.
- [ ] Implement provider failover handler with notification events and zero duplicated operations.

## Phase 5: Security Core (Privacy, Budget, Approvals)
- [ ] Implement Confidential Repository Guard (`PrivacyPolicyEngine`) with hard fail-closed enforcement.
- [ ] Implement Individual Budget Enforcement (`BudgetEngine`) with atomic reservation and actual usage reconciliation.
- [ ] Implement Action Approval Engine (`ApprovalEngine`) with cryptographic approval tokens, content-hash verification, and rejection handling.
- [ ] Implement OS-level command sandbox with disallowed command filters and restricted working directory.

## Phase 6: Agent Core & Tool Execution Engine
- [ ] Implement real tools:
  - `read_file`, `list_files`, `search_code`, `inspect_repository`, `get_file_metadata`
  - `propose_patch`, `write_file`, `delete_file`, `run_shell`, `git_status`, `git_diff`, `git_commit`, `git_push`
- [ ] Implement Controlled Agent Loop:
  - User Request -> Classification -> Context Retrieval -> Plan Generation -> Model Selection -> Reasoning -> Tool Request -> Policy Validation -> Approval (if required) -> Execution -> Result Validation -> Next Step -> Final Report.
- [ ] Implement Session Checkpointing, Pause, Resume, Recovery after backend restart.

## Phase 7: REST API & Real-Time Event Hub
- [ ] Build FastAPI routers for Auth, Projects, Sessions, Approvals, Budget, Analytics, Benchmarking, Audit Logs.
- [ ] Build WebSocket / SSE event hub for real-time live execution events.

## Phase 8: Frontend Dashboard & IDE
- [ ] Build modern Next.js 15+ / React application with Tailwind CSS, dark developer UI.
- [ ] Implement Main Dashboard, Projects Page, Multi-Panel Coding Workspace (Repo Explorer, Monaco/Code Viewer, Agent Chat, Terminal/Live Events, Approval Bar).
- [ ] Implement Token Analytics, Budget Management, Provider Status, Security & Audit Center.

## Phase 9: Automated Testing Suite & Benchmarking
- [ ] Implement all 10 mandatory test scenarios in `pytest`:
  1. Provider Outage / HTTP 429 Fallback
  2. Budget Exhaustion
  3. Confidential Repository Cloud Block
  4. File Write Approval
  5. Shell Security & Command Injection
  6. Git Mutation Approval
  7. Cache Invalidation on File Drift
  8. Session Recovery After Backend Interruption
  9. Real-Time Event Streaming
  10. Token & Cost Accounting Accuracy
- [ ] Implement automated benchmark runner (Baseline vs Optimized token savings).

## Phase 10: Docker Setup, Documentation & Final Delivery
- [ ] Create `Dockerfile`, `docker-compose.yml`, `.env.example`.
- [ ] Write comprehensive `README.md`, `SECURITY.md`, `API.md`.
- [ ] Final end-to-end verification and delivery report.

