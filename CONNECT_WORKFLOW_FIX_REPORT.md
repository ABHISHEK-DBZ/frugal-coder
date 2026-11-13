# CONNECT WORKFLOW FIX REPORT: REPOSITORY CONNECTION & INSPECTION
**Project:** Frugal Coder — The Budget-Aware, Privacy-First AI Coding Agent  
**Date:** November 13, 2026  
**Status:** **ROOT CAUSE DIAGNOSED, FIXED & FULLY VERIFIED**  

---

## 1. Root Cause Diagnosis

### The Problem
Clicking the `+ Connect` button in the Repository Explorer failed to connect a repository or allow the developer to choose a local path.

### Technical Analysis & Identified Failure Points
1. **Missing Interactive Connection Modal**:
   - In `frontend/src/app/page.tsx`, `+ Connect` was hardwired to `handleCreateDefaultProject()`.
   - `handleCreateDefaultProject()` did not open a modal or form; instead, it silently submitted a hardcoded JSON payload with a fixed path (`c:\Users\Abhishek\Downloads\loopos`) and `name: "secure-auth-service"`.
   - If the project already existed or an error occurred, the user received an abrupt alert without any form to enter their desired repository path.
2. **Missing Real File Content Retrieval Endpoint**:
   - The frontend's `selectFile()` method was hardcoded to display a mock placeholder string (`// [PROGRESSIVE CONTEXT L1 SKELETON: ...]`).
   - The backend `projects.py` router had `GET /projects/{project_id}/tree` for file listing, but completely lacked an authenticated `GET /projects/{project_id}/file?path=<relative_path>` endpoint to fetch real file contents, file hashes, and AST skeleton representations for the center editor.
3. **No File Search or View Modes**:
   - Developers had no way to filter large file trees or toggle between the raw implementation source code and the L1 progressive AST skeleton.

---

## 2. Implementation of the Fix

### A. Backend Fixes (`backend/app/api/projects.py`)
Added the secure, authenticated file inspection endpoint:
- **Endpoint**: `GET /api/v1/projects/{project_id}/file?path=<relative_path>`
- **Security Protections**:
  - Requires valid JWT bearer token (`get_current_user`).
  - Verifies project ownership (`Project.owner_id == current_user.id`).
  - Resolves path using `resolve_safe_path()`, strictly blocking path traversal attempts (e.g. `../../etc/passwd`).
  - Computes exact SHA-256 file content hash.
  - Queries/creates entry in `file_caches` table using `TokenOptimizationEngine.get_or_create_cache()`, returning both full token counts and L1 AST skeleton tokens.

### B. Frontend Redesign & Modal (`frontend/src/app/page.tsx`)
1. **Interactive Connect Repository Modal**:
   - Replaced silent stub with a modal dialog opened by `+ Connect`.
   - Allows entering custom repository directory path, display name, and setting the **Confidential Repository** privacy flag.
   - Includes validation, directory path hints, loading states, and inline error feedback.
2. **Real File & AST Content Display**:
   - `selectFile()` now calls `GET /projects/{project_id}/file?path=...`.
   - Displays real line numbers, syntax-highlighted code, and full token metrics.
   - Added **Source** vs. **AST Skeleton (L1)** vs. **Proposed Diff** view switcher in the editor toolbar.
3. **File Tree Filtering**:
   - Added live search input filtering the repository file list in real time.

---

## 3. End-to-End Test Verification

### Step 1: Real Connection Request via API
```bash
POST http://localhost:8000/api/v1/projects
Headers:
  Authorization: Bearer <jwt>
  Content-Type: application/json
Body:
  {"name": "live-verified-repo", "repo_path": "C:/Users/Abhishek/Downloads/loopos", "is_confidential": false}
```
**Response**: `HTTP 200 OK`
```json
{
  "id": "c22e5c1d-3208-4c47-b9aa-45d3233c0ccc",
  "name": "live-verified-repo",
  "repo_path": "C:\\Users\\Abhishek\\Downloads\\loopos",
  "is_confidential": false,
  "detected_language": "Python",
  "detected_framework": "FastAPI / Flask"
}
```

### Step 2: Safe Repository Tree Indexing
```bash
GET http://localhost:8000/api/v1/projects/c22e5c1d-3208-4c47-b9aa-45d3233c0ccc/tree
```
**Response**: `HTTP 200 OK` (Indexed 92 repository files).

### Step 3: Real File Reading & AST Extraction
```bash
GET http://localhost:8000/api/v1/projects/c22e5c1d-3208-4c47-b9aa-45d3233c0ccc/file?path=backend/app/main.py
```
**Response**: `HTTP 200 OK`
- `token_count_full`: **455 tokens**
- `token_count_skeleton`: **115 tokens** (74.7% token reduction on AST skeleton)
- Real file content delivered and displayed in editor.

### Step 4: Regression & Suite Verification
- **Pytest**: `pytest backend/tests/` -> **14 / 14 Passed** (6.32s).
- **Frontend Build**: `npm run build` -> **Compiled successfully** without warnings.

