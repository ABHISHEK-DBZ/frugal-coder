# LIVE CODING DEMO: END-TO-END AUTONOMOUS WORKFLOW
**Project:** Frugal Coder — The Budget-Aware, Privacy-First AI Coding Agent  
**Environment:** Windows 11, Next.js 14, FastAPI Backend, Bifrost v2.5.1 Gateway, Groq API  

---

## 1. Overview of the Live Demo Run

This demo reproduces the complete developer journey from authentication to automated patch application and test verification.

```
+---------------------------------------------------------------------------------------+
|                                FRUGAL CODER WORKFLOW                                  |
|                                                                                       |
|  [Developer UI] ---> [FastAPI / WS] ---> [AST Token Engine] ---> [Bifrost Gateway]   |
|         ^                   |                    |                        |           |
|         |                   v                    v                        v           |
|    (Approval Gate)     (Git Sandbox)       (L0-L4 Context)           (Groq Cloud)     |
+---------------------------------------------------------------------------------------+
```

---

## 2. Step-by-Step Execution Log

### Step 1: Initialize Git Test Repository
A repository with an intentional authentication flaw was initialized:
```bash
git init C:\Users\Abhishek\AppData\Local\Temp\frugal_phase4_repo_dbkoe0fa
```
**Original `auth_service.py`**:
```python
import hashlib

class AuthService:
    def __init__(self):
        self.users = {'alice': 'password123'}

    def authenticate(self, username, password):
        if username not in self.users:
            return False
        # INSECURE PLAIN TEXT COMPARISON BUG
        stored_password = self.users[username]
        if password == stored_password:
            return True
        return False
```
- Pre-mutation File Hash: `40d4901241fe...`

---

### Step 2: User Login & Session Creation
- **User**: `phase4_developer`
- **Budget Allocated**: $25.00
- **Session ID**: `6e1cfaa7-b31b-42ae-8828-ef65a4f62b2f`
- **Task Description**: `"Inspect auth_service.py, detect plain text password comparison, and propose a secure hash verification fix."`

---

### Step 3: Progressive Context Optimization & Model Dispatch
- **L0 Indexing**: Discovered `auth_service.py` and `test_auth.py`.
- **L1 AST Context**: Extracted class signature and method definitions.
- **Model Routing**: Routed to Primary Cloud Provider `openai/gpt-oss-120b` via Bifrost.
- **Bifrost Request**:
  - Endpoint: `http://localhost:8080/v1/chat/completions`
  - Virtual Key: `bf-vk-frugal-coder-dev`
  - Input Tokens: 185
  - Output Tokens: 1,866
  - Latency: 5,950 ms
  - Provider: `groq`

---

### Step 4: Action Proposal & User Rejection Test
The agent generated an approval proposal for `propose_patch`:
```diff
--- a/auth_service.py
+++ b/auth_service.py
@@ -10,2 +10,2 @@
-    if password == stored_password:
+    if verify_password(password, stored_hash, stored_salt):
```
- **Developer Decision**: `REJECT` (Reason: `"Developer rejected for security review"`)
- **Verification**: `auth_service.py` file hash checked after rejection:
  - Expected: `40d4901241fe...`
  - Actual: `40d4901241fe...` (Exact match: zero unauthorized file mutations).

---

### Step 5: Proposal Approval & Patch Execution
A second proposal with cryptographic SHA-256 password hashing was submitted:
```diff
--- a/auth_service.py
+++ b/auth_service.py
@@ -10,2 +10,2 @@
-        if password == stored_password:
+        if hashlib.sha256(password.encode()).hexdigest() == stored_password:
```
- **Developer Decision**: `APPROVE`
- **Execution Engine**: `ToolExecutionEngine.apply_patch()`
- **Result**:
  ```json
  {"status": "success", "file": "auth_service.py", "hash": "146b7b2a933776345e130d65109fab8294708038bf8e785298ce22148c5015e4"}
  ```
- **File Update Verified**: New SHA-256 is `146b7b2a9337...`.

---

### Step 6: Test Suite Verification
The project unit test suite was executed:
```bash
python -m unittest test_auth.py
```
**Output**:
```
.
----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```
**Result**: All unit tests passed without errors.

---

### Step 7: Completed Task & Audit Trail

| Timestamp | Event Type | Details |
| :--- | :--- | :--- |
| `16:19:42` | `session_created` | Session initialized for project `phase4-auth-secure` |
| `16:19:43` | `context_assembled` | L1 AST context assembled; tokens saved: 153 |
| `16:19:44` | `model_call` | `openai/gpt-oss-120b` via Bifrost (5,950 ms) |
| `16:19:45` | `approval_decision` | Status: `REJECTED` |
| `16:19:46` | `approval_decision` | Status: `APPROVED` |
| `16:19:46` | `action_executed` | Patch applied to `auth_service.py` |
| `16:19:47` | `tests_executed` | `test_auth.py` PASSED |

