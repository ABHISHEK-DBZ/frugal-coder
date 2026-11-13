# FINAL ARCHITECTURE SPECIFICATION
**Project:** Frugal Coder — The Budget-Aware, Privacy-First AI Coding Agent  
**Version:** Production 1.0 (Hackathon Submission Release)  
**Date:** November 13, 2026  

---

## 1. System Topology Overview

Frugal Coder is structured as a decoupled, multi-tiered architecture that separates the developer interface, policy enforcement, gateway orchestration, and sandbox execution:

```
[ Developer UI (Next.js 14 App Router) ]
         │ (HTTP REST / WebSocket Events)
         ▼
[ FastAPI Core Application (:8000) ]
   ├── Authentication & RBAC (PBKDF2-HMAC-SHA256, JWT)
   ├── SQLite Persistent Ledger (11 Tables: users, budgets, sessions, etc.)
   ├── Token Optimization Engine (L0-L4 AST Skeletons + SHA-256 Invalidation)
   ├── Action Approval Engine (Cryptographic Single-Use Tokens)
   └── Independent Privacy Guard (Architectural Gate)
         │
         ├── Non-Confidential Project?
         │         │
         │         ▼
         │   [ Bifrost AI Gateway (:8080) ]
         │         │ (Virtual Key: bf-vk-frugal-coder-dev)
         │         ├── Primary: Groq Cloud API (openai/gpt-oss-120b, qwen/qwen3.8-27b)
         │         └── Failover: Secondary Cloud (OpenAI gpt-4o-mini)
         │
         └── Confidential Project?
                   │
                   ▼
             [ Privacy Guard Boundary ]
                   ├── Cloud Fallback Attempted? ──► HALT (Fail Closed)
                   └── Local Inference Runtime (:11434) (llama.cpp / Ollama / vLLM)
```

---

## 2. Core Subsystems & Components

### 2.1 AST Progressive Context Engine (`backend/app/services/token_engine.py`)
- **L0 (File Tree)**: Discover repository hierarchy without reading file bodies.
- **L1 (AST Skeleton)**: Extracts class hierarchies, function signatures, and docstrings using Python's native `ast` module and JS/TS AST regex grammar. Body blocks are replaced with `...`.
- **L2 (Imports & Exports)**: Extracts dependency relationships between files.
- **L3 (Target Implementation)**: Loads full implementation only for files actively selected for modification.
- **L4 (Full Context)**: Fallback emergency level, used only when explicitly requested.
- **SHA-256 Cache Invalidation**: Files are hashed; if the content hash matches the database cache (`file_caches` table), skeleton extraction is skipped (0.01 ms cache hit).

### 2.2 Bifrost Central Gateway (`backend/app/services/gateway.py`)
- Communicates directly with Bifrost v2.5.1 on port 8080.
- All requests authenticate via `x-bf-vk` and `Authorization: Bearer <virtual_key>`.
- Preserves usage metrics: captures input tokens, output tokens, upstream latency, and provider routing details.
- Raises explicit `RuntimeError` if Bifrost is offline, eliminating silent provider bypass.

### 2.3 Independent Privacy Gate (`backend/app/policy/privacy.py`)
- Independent policy check executed outside LLM influence.
- Prevents prompt injection attacks from exfiltrating confidential repository data to the cloud.
- If a project is confidential and the local runtime is offline, the gateway **fails closed**. Cloud fallback is strictly prohibited.

### 2.4 Action Approval & Sandboxed Execution (`backend/app/policy/approval.py` & `execution.py`)
- Every mutating filesystem, shell, or Git operation creates an `Approval` record with a single-use token.
- Binds to the target file's pre-mutation SHA-256 hash. If the file is altered prior to user approval, execution aborts with `ActionTamperedError`.
- Rejections leave the target repository 100% unaltered.

### 2.5 Budget Reservation & Reconciliation (`backend/app/policy/budget.py`)
- Atomic pre-flight reservation reserves the maximum estimated cost prior to dispatching model calls.
- Following response receipt, exact usage is calculated and reconciled against the user's hard spending limit.

