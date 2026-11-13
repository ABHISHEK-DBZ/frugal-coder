# TAVILY SEARCH API INTEGRATION

**Frugal Coder** integrates the official **Tavily Search API** alongside the **Bifrost AI Gateway** to deliver authoritative web research and documentation retrieval directly to the autonomous coding loop.

---

## 1. Why Tavily?

Traditional AI coding agents either hallucinate when APIs change or force developers to manually paste documentation URLs into chat windows. Frugal Coder solves this by autonomously deciding when a coding task warrants external technical discovery (e.g., deprecated APIs, framework migration guides, SDK breaking changes, CVE security advisories).

### Core Capabilities
- **Technical Search Ranking**: Focuses on developer documentation, GitHub issues, and official changelogs.
- **AI Synthesized Answer**: Compact answers summarizing technical solutions.
- **Strict Citation Tracing**: Every code recommendation references authoritative source URLs.
- **Strict Privacy Isolation**: Confidential repositories are physically blocked from sending code queries to Tavily.

---

## 2. Combined Architecture: Tavily + Bifrost

```
Developer Task
     │
     ▼
Task Classification & Heuristics
     │
     ├─── Needs External Research? (Keywords: deprecation, migrate, error, latest docs)
     │         │
     │         ├── Yes (Public/Standard Repo) ──> [Tavily Search API]
     │         │                                        │
     │         │                                        ▼
     │         │                               Verified Sources & Excerpts
     │         │                                        │
     │         └── No / Confidential Repo ──────────────┤
     ▼                                                  │
AST Progressive Context Optimizer (L1 Skeletons)        │
     │                                                  │
     ▼                                                  │
Enriched Context + Source Citations <───────────────────┘
     │
     ▼
Pre-flight Budget Reservation & Privacy Policy Gate
     │
     ▼
[Bifrost Gateway (Port 8080)]
     │
     ▼
[Groq Provider (Llama-3.3-70B)]
     │
     ▼
Proposed Code Changes (Diff)
     │
     ▼
Developer Approval Gate (Approve / Reject)
     │
     ▼
Verified Safe Filesystem Mutation
```

---

## 3. Implementation Details

1. **Dedicated Service** (`backend/app/services/tavily_service.py`):
   - Implements `TavilyResearchService.search(query, max_results=4)`.
   - Incorporates `should_research(task_description)` decision heuristics.
   - Enforces SSL context resilience across operating systems.
2. **Dedicated REST Router** (`backend/app/api/research.py`):
   - `POST /api/v1/research/search`: Real-time query endpoint returning ranked sources and excerpts.
   - `GET /api/v1/research/status`: Operational health endpoint.
3. **Agent Integration** (`backend/app/agent/core.py`):
   - During session planning, the agent evaluates if research is needed.
   - Emits `research_started` and `research_completed` live events over WebSockets.
   - Appends verified citations into the LLM system/user context.
4. **Interactive Research Center UI** (`frontend/src/app/page.tsx`):
   - Dedicated navigation tab with live search input, suggested chips, synthesized answers, and relevance scores.
   - One-click `"Use in Agent →"` button that transfers retrieved documentation directly into the prompt box.

