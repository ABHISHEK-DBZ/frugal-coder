# ARCHITECTURE — FRUGAL CODER

"The Budget-Aware, Privacy-First AI Coding Agent."
*Build smarter. Spend less. Ship securely.*

---

## 1. High-Level Architecture Diagram

```
                        +---------------------------------------------+
                        |           DEVELOPER INTERFACE               |
                        |      Next.js 15+ Web Dashboard & IDE        |
                        |   Monaco Editor | Live Timeline | Approvals |
                        +---------------------------------------------+
                                       |              ^
                            REST APIs  |              | WebSockets / SSE
                                       v              |
+-----------------------------------------------------------------------------------------+
|                                    FASTAPI BACKEND                                      |
|                                                                                         |
|  [ Module A: Auth & RBAC ]        [ Module B: Repo Explorer ]   [ Module L: Real-Time ] |
|  - JWT, PBKDF2 Password Hashing    - Path Traversal Guard        - WebSocket Event Hub  |
|  - User Spending Limits            - AST / Symbol Extraction     - State Change Streams |
|                                                                                         |
|  +-----------------------------------------------------------------------------------+  |
|  |                              POLICY & SECURITY CORE                               |  |
|  |                                                                                   |  |
|  |  [ Module H: Budget Engine ]     [ Module G: Privacy Guard ]   [ Module I: Approvals ]|
|  |  - Atomic Cost Reservation       - Confidential Flag Watcher   - Cryptographic Tokens|
|  |  - Usage Reconciliation          - Fail-Closed Cloud Block     - Patch & Command Hash|
|  |  - Pre-flight Call Check         - Audit Log Security Events   - Human-in-the-Loop   |
|  +-----------------------------------------------------------------------------------+  |
|                                          |                                              |
|  +-----------------------------------------------------------------------------------+  |
|  |                            AGENT EXECUTION RUNTIME                                |  |
|  |                                                                                   |  |
|  |  [ Module C: Agent Core ]       [ Module D: Token Engine ]    [ Module E: Router ]  |  |
|  |  - Multi-Step Reasoning Loop    - L0-L4 Progressive Context   - Task Complexity     |  |
|  |  - Plan & Step Checkpointing    - AST Skeletons (py/js/ts)    - Cost/Quality Rules  |  |
|  |  - Error Diagnosis & Retry      - File Hash Memory Cache      - Escalation Logic    |  |
|  |                                                                                   |  |
|  |  [ Module J: Tool Execution Engine ]                                              |  |
|  |  - Safe Read Tools (read, list, search, inspect) -> Auto-Approved                |  |
|  |  - Mutating Tools (write, patch, delete, shell, git) -> Approval Required         |  |
|  |  - Restricted OS Subprocess Runner (path bounded, forbidden patterns)            |  |
|  +-----------------------------------------------------------------------------------+  |
|                                          |                                              |
|  [ Module F: Gateway & Provider Layer ]                                                 |  |
|  - Unified OpenAI-compatible Bifrost / Local / Cloud Client                            |  |
|  - Virtual Keys per user & confidential local-only virtual key                          |  |
|  - Automatic Fallback Chain: Primary (Groq/Ollama) -> Secondary (OpenAI/Anthropic)      |  |
|  - Failover State Recovery (Retries without re-executing completed side-effects)        |  |
+-----------------------------------------------------------------------------------------+
       |                                                                  |
       v                                                                  v
+-------------------------------+                     +-----------------------------------+
|      STORAGE & PERSISTENCE    |                     |       AI MODEL PROVIDERS          |
|  - SQLite (async via SQLAlchemy)                    |  - Bifrost Gateway (Port 8080)    |
|  - Users, Projects, Sessions   |                     |  - Ollama Local (Port 11434)      |
|  - AgentSteps, ModelCalls      |                     |  - Cloud Providers (OpenAI, etc.) |
|  - Approvals, AuditLogs        |                     |  - Test Mock Provider (Fallback)  |
|  - BudgetTransactions, Cache   |                     +-----------------------------------+
+-------------------------------+
```

---

## 2. Key Architecture Guarantees

### 1. Zero Untrusted Execution (Approval Engine)
- All write, delete, shell, and git actions emit an `ApprovalRequest` with:
  - Exact target relative path
  - SHA-256 hash of target file content before modification
  - SHA-256 hash of proposed new content or diff
  - Exact shell command and working directory
- Cryptographic approval token generated server-side.
- Execution validates token and verifies disk content hasn't drifted.

### 2. Strict Privacy Guardrail (Confidential Repositories)
- Repositories marked with `confidential: true` or containing `.frugal-coder.yaml` with `privacy.inference: local_only`:
  - Only route to local inference providers (e.g., Ollama or local gateway virtual key).
  - Independent policy interceptor throws `PrivacyPolicyViolation` if any cloud provider is requested.
  - Fail-closed: if local inference is unavailable, the agent halts safely, notifies the user, and audits the event. Prompt injection ("ignore privacy rules") is rejected by external policy layer.

### 3. Atomic Budget Reservation
- Before any model call:
  - Estimated max cost = `input_tokens * rate_in + max_tokens * rate_out`
  - Atomically checked and reserved in `BudgetTransaction` table.
  - If `spent + reserved + estimated > limit`, call is blocked with `BudgetExhaustedError`.
  - Upon completion, actual token count is read from provider response, actual cost settled, and unused reservation released.

### 4. Progressive Context Engine (L0-L4)
- **L0:** File tree, paths, extensions, line counts.
- **L1:** AST skeletons (imports, class/function signatures, docstrings, no bodies).
- **L2:** Relevant function/method extracted via symbol indexing.
- **L3:** Full file content (only for files actively being modified).
- **L4:** Direct dependency files.
- Results in 60-85% token savings compared to naive whole-repo dumping.

### 5. Seamless Provider Failover & Session Recovery
- If primary provider fails (HTTP 429, 500, network timeout):
  - Gateway / router switches to next provider in fallback chain.
  - Emits real-time notification to user.
  - Session state persists after each step: already executed file writes or tests are NEVER duplicated.

