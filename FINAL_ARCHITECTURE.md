# FINAL ARCHITECTURE SPECIFICATION: FRUGAL CODER

**Product:** FRUGAL CODER  
**Tagline:** The Budget-Aware, Privacy-First, Research-Driven AI Coding Agent  
**Hackathon Submission:** Global AI Hackathon 2026 (HackCulture / Geek Room)  
**Primary AI Gateway:** Bifrost by Maxim AI  
**Research Engine:** Tavily Search API  

---

## 1. System Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          NEXT.JS FRONTEND (Port 3000)                       │
│  - Cursor IDE × Linear Dark UI Theme                                        │
│  - Repository Explorer & Breadcrumbs                                        │
│  - Multi-Tab Monaco-Style Editor (Source, AST Skeleton, Diff)                │
│  - Dedicated Research Center with Tavily Live Search                        │
│  - Autonomous Agent Live Execution Timeline (WebSockets)                    │
│  - Reproducible Benchmark Suite & Sparkline KPIs                             │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ REST / WebSockets
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FASTAPI BACKEND (Port 8000)                        │
│  ┌────────────────────────┐  ┌────────────────────────┐  ┌────────────────┐ │
│  │ AST Token Engine (L1)  │  │ Privacy Policy Guard   │  │ Budget Engine  │ │
│  │ - 54.10% Token Savings │  │ - Fail-closed boundary │  │ - Pre-flight   │ │
│  │ - Tree-sitter & AST    │  │ - Physical air-gap     │  │   reservation  │ │
│  └───────────┬────────────┘  └───────────┬────────────┘  └────────┬───────┘ │
│              │                           │                        │         │
│              └───────────────────────────┼────────────────────────┘         │
│                                          ▼                                  │
│                          ┌───────────────────────────────┐                  │
│                          │      Agent Core Loop          │                  │
│                          └───────┬───────────────┬───────┘                  │
└──────────────────────────────────┼───────────────┼──────────────────────────┘
                                   │               │
        Technical Web Research     │               │   Primary Cloud Routing
                   │               │               │
                   ▼               ▼               ▼
        ┌──────────────────┐               ┌─────────────────────────────────┐
        │ Tavily Search API│               │      Bifrost Gateway v2.5.1     │
        │ - Docs discovery │               │       (localhost:8080)          │
        │ - AI summary     │               │ - Virtual Key Isolation         │
        │ - Citations      │               │ - Multi-tier Failover           │
        └──────────────────┘               └────────────────┬────────────────┘
                                                            │
                                                            ▼
                                                   ┌─────────────────┐
                                                   │  Groq Provider  │
                                                   │  Llama-3.3-70B  │
                                                   └─────────────────┘
```

---

## 2. Security & Policy Invariants

1. **Confidential Isolation**: Any repository flagged as `is_confidential = True` is physically prohibited from contacting external clouds. Tavily and Bifrost are disabled; requests require an air-gapped local model.
2. **Pre-flight Budget Caps**: Model requests require pre-flight balance reservations. If cost exceeds balance, execution halts immediately with zero spend overrun.
3. **Approval Gate Before Filesystem Mutation**: The agent cannot modify code on disk without developer approval. Proposes side-by-side diffs and verifies SHA-256 hashes prior to patch application.
