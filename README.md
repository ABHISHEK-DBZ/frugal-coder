<div align="center">

# ⚡ FRUGAL CODER

### The Budget-Aware, Privacy-First, Research-Driven AI Coding Agent

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-black.svg?style=flat&logo=next.js)](https://nextjs.org/)
[![Bifrost](https://img.shields.io/badge/Gateway-Bifrost%20v2.5.1-4F46E5.svg?style=flat)](https://www.getmaxim.ai/bifrost)
[![Tavily](https://img.shields.io/badge/Research-Tavily%20Search%20API-0284C7.svg?style=flat)](https://tavily.com/)
[![Groq](https://img.shields.io/badge/Inference-Groq%20Llama--3.3--70B-F55036.svg?style=flat)](https://groq.com/)
[![Tests](https://img.shields.io/badge/Tests-17%2F17%20Passed-10B981.svg?style=flat)](#testing)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat)](LICENSE)

**Build Smarter. Research Better. Spend Less. Ship Securely.**

*Submitted to the Global AI Hackathon 2026 (HackCulture / Geek Room)*  
*Combined Project: Bifrost by Maxim AI + Tavily Search API*

---

</div>

## 📌 Executive Summary

Modern AI coding agents burn through cloud budgets by stuffing entire repositories into LLM context, hallucinate when APIs change, and risk exposing proprietary code. 

**Frugal Coder** solves this with a multi-layered, budget-aware architecture:
1. **AST Progressive Context Optimization**: Reduces prompt input tokens by **54.10%** without losing architectural understanding.
2. **Centralized AI Gateway (Bifrost)**: Routes all cloud inference through a local Bifrost daemon on port `8080` with Virtual Key isolation, latency tracking, and automatic provider failover.
3. **Autonomous Web Research (Tavily)**: Heuristically detects deprecated APIs and SDK breaking changes, fetching verified technical citations directly into the agent's context.
4. **Strict Fail-Closed Privacy Boundary**: Confidential repositories are physically blocked from cloud models and external search engines.
5. **Human-in-the-Loop Mutation Gate**: The agent cannot mutate disk files without explicit developer diff approval and SHA-256 integrity validation.

---

## 🌟 Key Features

| Capability | Description |
| :--- | :--- |
| 🛡️ **Bifrost AI Gateway** | Drop-in centralized gateway running on `localhost:8080`. Manages virtual keys (`bf-vk-frugal-coder-dev`), handles rate limits, and reconciles usage. |
| 🔍 **Tavily Technical Research** | Live web search engine for agents. Synthesizes documentation answers and injects cited excerpts prior to code synthesis. |
| ⚡ **54.10% Token Savings** | AST skeleton extraction preserves class/function signatures while stripping private implementation bloat. |
| 💰 **Atomic Budget Guardrails** | Hard spending caps ($10 user cap, $2 session cap) with pre-flight cost reservations to prevent runaway agent loops. |
| 🔒 **Confidential Repository Isolation** | Strict fail-closed air-gap policy: confidential code never leaves the local machine. Zero cloud fallback. |
| 🖥️ **Cursor × Linear IDE UI** | Desktop-first developer workspace featuring a repository explorer, multi-tab code editor, live WebSocket timeline, and diff reviewer. |

---

## 🏗️ Architecture & Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          NEXT.JS FRONTEND (Port 3000)                       │
│  - Cursor IDE × Linear Dark Theme                                           │
│  - Repository Explorer & Breadcrumbs                                        │
│  - Multi-Tab Monaco-Style Editor (Source, AST Skeleton, Diff)                │
│  - Dedicated Tavily Research Center                                         │
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
│  │ - Interface contracts  │  │ - Physical air-gap     │  │   reservation  │ │
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

## 📊 Measured Benchmark Results

Holding the underlying LLM provider (**Groq Llama-3.3-70B**) constant, Frugal Coder was evaluated across **15 reproducible trials** (5 representative tasks, 3 trials each):

| Task Category | Baseline Tokens (Avg) | Optimized Tokens (Avg) | Token Reduction | Cost Reduction | Latency Reduction | Pass Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Simple Bug Fix** | 582 | 248 | **57.4%** | **52.6%** | +8.4% | 100% |
| **API Deprecation Migration** | 714 | 312 | **56.3%** | **51.8%** | +6.9% | 100% |
| **Multi-File Architecture** | 940 | 446 | **52.5%** | **49.1%** | +5.1% | 100% |
| **Codebase Summarization** | 620 | 290 | **53.2%** | **48.7%** | +6.0% | 100% |
| **Security Vulnerability Patch**| 660 | 318 | **51.8%** | **49.2%** | +5.0% | 100% |
| **SUITE AVERAGE** | **703 in** | **323 in** | **54.10%** | **50.28%** | **+6.28%** | **100%** |

*All raw provider usage payloads and trial statistics are persisted in [`benchmarks/BENCHMARK_RAW_RESULTS.json`](benchmarks/BENCHMARK_RAW_RESULTS.json).*

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API Key
- Tavily Search API Key

### 1. Clone the Repository
```bash
git clone https://github.com/ABHISHEK-DBZ/frugal-coder.git
cd frugal-coder
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your keys:
```bash
cp .env.example .env
```

```env
# Central AI Gateway (Bifrost)
BIFROST_URL="http://localhost:8080"
BIFROST_API_KEY="bf-vk-frugal-coder-dev"

# Primary Provider (Groq)
GROQ_API_KEY="your-groq-api-key"
GROQ_MODEL="openai/gpt-oss-120b"

# Research Engine (Tavily)
TAVILY_API_KEY="your-tavily-api-key"
TAVILY_BASE_URL="https://api.tavily.com"
```

### 3. Launch Services

#### A. Start Bifrost Gateway (Terminal 1)
```powershell
# Set your Bifrost setup token and start the gateway
$env:BIFROST_SETUP_TOKEN = "your-setup-token"
npx -y @maximhq/bifrost
```

#### B. Start FastAPI Backend (Terminal 2)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### C. Start Next.js Frontend (Terminal 3)
```bash
cd frontend
npm install
npm run dev
```

Visit **`http://localhost:3000`** in your browser.

---

## 🧪 Testing

Frugal Coder includes automated unit, integration, and security test suites:

```bash
cd backend
python -m pytest tests/
```

**Test Coverage Highlights:**
- `test_mandatory_scenarios.py`: AST skeleton extraction, atomic budget reservations, SHA-256 pre-mutation verification, and patch approval/rejection workflows.
- `test_priority3_security.py`: Confidential repository isolation, provider routing, and prompt injection defense.
- `test_tavily_research.py`: Tavily search execution, decision heuristics, citation extraction, and confidential data leak prevention.

*Result:* **17 passed in 10.64s**

---


---

## 👥 Hackathon Team & Acknowledgements

- **Team**: HackCulture / Geek Room Participant
- **Competition**: Global AI Hackathon 2026
- **Gateway Partner**: [Bifrost by Maxim AI](https://www.getmaxim.ai/bifrost)
- **Research Partner**: [Tavily Search API](https://tavily.com/)
- **Inference Partner**: [Groq](https://groq.com/)

---

<div align="center">
  <sub>Built with ❤️ for developers who value performance, budget, and privacy.</sub>
</div>
