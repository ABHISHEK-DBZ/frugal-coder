# SECURITY & AUDIT REPORT
**Project:** Frugal Coder — The Budget-Aware, Privacy-First AI Coding Agent  
**Date:** November 13, 2026  
**Auditor:** Principal Security & AI Safety Architect  

---

## 1. Threat Modeling & Security Perimeter

Frugal Coder is designed to defend against common attack vectors in AI agent systems:

| Threat Vector | Potential Impact | Frugal Coder Countermeasure |
| :--- | :--- | :--- |
| **Data Exfiltration via Prompt Injection** | Leaking confidential proprietary source code to cloud LLMs | **Independent Privacy Guard**: Architectural gate outside LLM context. Validates confidentiality flag before network calls. |
| **Silent Provider Bypass** | Subverting enterprise gateway monitoring | **Enforced Bifrost Gateway**: Direct provider bypass disabled. Gateway downtime raises explicit `RuntimeError`. |
| **Unauthorized Disk / Git Mutation** | Malicious or buggy file overwrites | **Cryptographic Action Approval Engine**: Every mutating tool requires explicit developer approval bound to pre-mutation SHA-256 hashes. |
| **Race Condition File Tampering** | Changing a file after approval request to apply unauthorized diff | **Content Hash Verification**: If the target file hash changes prior to execution, the action is blocked with `ActionTamperedError`. |
| **Runaway Token Exhaustion** | Incurring massive unbudgeted API charges | **Atomic Budget Reservation**: Pre-call reservation locks funds before dispatch; reconciles usage post-response. |
| **Dangerous Shell Execution** | OS-level destructive commands (`rm -rf /`, `format`) | **Command Pattern Blacklist**: Forbidden patterns blocked immediately before approval generation. |

---

## 2. Authentication & Credential Storage

1. **Password Security**:
   - Implemented using PBKDF2-HMAC-SHA256 with **100,000 iterations** and random 16-byte hex salts.
   - Verified pure Python implementation (`hashlib.pbkdf2_hmac`) with constant-time equality comparisons (`secrets.compare_digest`).
2. **Session Authentication**:
   - Signed JSON Web Tokens (JWT) using HS256 algorithm with configurable expiration.
3. **Secret Hygiene**:
   - API keys and tokens stored in `.env` and environment variables. Never logged in plain text or rendered in frontend responses.

---

## 3. Immutable Security Audit Trail

All security events are captured in the SQLite `audit_logs` table:
- `privacy_block`: Critical alert when a cloud call is attempted on a confidential project.
- `approval_decision`: Warning on rejection, info on approval.
- `provider_failover`: Info when secondary cloud provider is engaged due to 429 rate limit.
- `budget_exhausted`: Warning when a session reaches its user spending cap.

All 14 security and policy unit tests pass with zero failures.

