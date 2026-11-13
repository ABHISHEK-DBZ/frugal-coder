# PROJECT AUDIT: FRUGAL CODER

**Date:** November 13, 2026  
**Auditor:** Principal Software Architect & AI Infrastructure Engineer  
**Hackathon Target:** Global AI Hackathon 2026 — HackCulture / Geek Room  
**Positioning:** The Budget-Aware, Privacy-First, Research-Driven AI Coding Agent  
**Primary AI Gateway:** Bifrost by Maxim AI (Port 8080)  
**Research Engine:** Tavily Search API  

---

## 1. Executive Summary & Existing Features

Frugal Coder is a complete, working budget-aware developer IDE and autonomous agent that combines AST token compression with atomic budget enforcement and a strict fail-closed privacy boundary.

### Existing Verified Assets:
1. **Bifrost Gateway Integration**:
   - Running locally on port `8080` (Process PID daemon active).
   - Authenticated with Virtual Key `bf-vk-frugal-coder-dev`.
   - Routes cloud requests to Groq (`openai/gpt-oss-120b` and `openai/gpt-oss-20b`).
2. **Context Compression (AST Skeletons)**:
   - Progressive retrieval hierarchy (L0 repo tree, L1 AST skeletons, L2 interface contracts, L3 target bodies).
   - Tested across 15 reproducible trials with an average 54.10% input token reduction and 50.28% cost savings.
3. **Strict Privacy Policy Gate**:
   - `PrivacyGuard` physically isolates confidential repositories.
   - Fail-closed: Cloud fallback is strictly prohibited when local runtime is offline.
4. **Approval & Mutation Gate**:
   - SHA-256 pre-mutation verification before applying diffs.
   - Rejection leaves filesystem strictly untouched.
5. **Backend Test Suite**:
   - 14/14 Pytest tests passing covering security, budget reconciliation, approval validation, and failover.

---

## 2. Missing Integrations & Critical Gaps

| Area | Current State | Required State for Submission |
| :--- | :--- | :--- |
| **Tavily Search API** | Not yet integrated in backend or frontend. | Complete Tavily research service (`tavily_service.py`), agent research tool step, dedicated Research Center UI with live web searches, source citations, and timestamps. |
| **Combined Bifrost + Tavily Flow** | Agent routes to Bifrost without external research. | Agent autonomously evaluates when external research is required, executes Tavily search, incorporates citation context into prompt, and routes through Bifrost. |
| **Frontend Page Architecture** | All views condensed into single page tabs. | Full multi-page subviews (Workspace, Research Center, Token Analytics, Security & Audit, Budget Control, Settings) with live event links. |
| **Research Center View** | Missing. | Search query input, live search status, source URLs, excerpts, timestamps, and history. |
| **Environment Variable Management** | `TAVILY_API_KEY` missing from `.env` and `config.py`. | Added securely to `.env`, `Settings` schema, and `.env.example` placeholder. |

---

## 3. Working APIs & Routes

- `POST /api/v1/auth/login`, `POST /api/v1/auth/register`
- `GET /api/v1/projects`, `POST /api/v1/projects`, `PATCH /api/v1/projects/{id}`
- `GET /api/v1/projects/{id}/tree`, `GET /api/v1/projects/{id}/file`
- `POST /api/v1/sessions`, `GET /api/v1/sessions/{id}`, `GET /api/v1/sessions/{id}/trace`
- `GET /api/v1/approvals/pending`, `POST /api/v1/approvals/{id}/decision`
- `GET /api/v1/budget`, `PUT /api/v1/budget`
- `GET /api/v1/analytics/overview`
- `GET /api/v1/benchmarks/results`
- `GET /api/v1/audit-logs`
- `GET /api/v1/providers/status`
- `WS /api/v1/events/{session_id}`

---

## 4. Security Audit & Protection

1. **No Committed Secrets**: `.env`, `bifrost_token.txt`, and `frugal_coder.db` are strictly excluded in `.gitignore`.
2. **Confidentiality Invariant**: Tavily web queries for confidential repositories must be sanitized and strictly prohibited from leaking proprietary file contents or confidential context.
3. **SSL Verification**: Implemented standard fallback and SSL context handling for Tavily in Windows/PowerShell environments.

---

## 5. Files Requiring Modification / Creation

1. `backend/app/core/config.py` (Add `TAVILY_API_KEY`, `TAVILY_BASE_URL`)
2. `backend/app/services/tavily_service.py` (New dedicated research service)
3. `backend/app/api/research.py` (New research API endpoints)
4. `backend/app/agent/core.py` (Integrate Tavily research step prior to reasoning)
5. `backend/app/main.py` (Mount research router)
6. `backend/tests/test_tavily_research.py` (Automated tests for Tavily research)
7. `frontend/src/app/page.tsx` (Add Research Center view, research subtabs, live research events)
8. Documentation: `FINAL_README.md`, `TAVILY_INTEGRATION.md`, `FINAL_ARCHITECTURE.md`, `FINAL_SUBMISSION_CHECKLIST.md`, etc.

