# API SPECIFICATION — FRUGAL CODER

Base URL: `http://localhost:8000/api/v1`
Interactive Swagger Docs: `http://localhost:8000/api/v1/docs`

---

## Endpoints Summary

### Authentication (`/auth`)
- `POST /auth/register` — Register a developer account. Creates default user budget ($10.00).
- `POST /auth/login` — Authenticate with username and password, returns JWT bearer token.
- `GET /auth/me` — Get authenticated developer profile.

### Projects (`/projects`)
- `POST /projects` — Connect a local repository. Detects `.frugal-coder.yaml` confidentiality, language, and framework.
- `GET /projects` — List user repositories.
- `GET /projects/{project_id}/tree` — Retrieve safe repository file tree.

### Sessions & Agent (`/sessions`)
- `POST /sessions` — Create a coding session and launch the autonomous agent loop in the background.
- `GET /sessions/{session_id}` — Get session status, checkpoints, and execution plan.
- `GET /sessions/{session_id}/trace` — Retrieve execution trace and provider model call history.

### Action Approvals (`/approvals`)
- `GET /approvals` — List pending mutating actions requiring user confirmation.
- `POST /approvals/{approval_id}/decision` — Approve or reject proposed code patch / command.

### Budget & Analytics (`/budget`, `/analytics`)
- `GET /budget` — View user spending limit, spent amount, and active reservations.
- `PUT /budget` — Update individual spending limit.
- `GET /analytics/overview` — Get aggregated metrics (tokens processed, cost spent, savings %, cache hits).
- `GET /audit-logs` — Retrieve immutable security audit ledger.

### Real-Time WebSocket
- `ws://localhost:8000/ws/sessions/{session_id}` — Real-time live execution event stream.

