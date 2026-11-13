# FRUGAL CODER

<div align="center">

**The Budget-Aware, Privacy-First AI Coding Agent**  
*Build Smarter. Spend Less. Ship Securely.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg?logo=next.js&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Bifrost Gateway](https://img.shields.io/badge/Bifrost-v2.5.1-7928CA.svg)](https://github.com/maximhq/bifrost)
[![Tests Passing](https://img.shields.io/badge/Tests-14%20Passed-emerald.svg)]()

</div>

---

## 1. Problem Statement

Autonomous AI coding agents are transforming software engineering, but two critical barriers prevent widespread enterprise and developer adoption:

1. **Uncontrolled Token Consumption & Runaway Costs**: Existing coding agents blindly pass whole files, entire dependency subtrees, and redundant file dumps into LLM prompts. A single multi-file coding task frequently consumes 50,000 to 200,000+ tokens, leading to exorbitant operational bills and rapid quota exhaustion.
2. **Proprietary Code Privacy Leakage**: Enterprise organizations strictly prohibit uploading confidential or proprietary source code to public cloud AI providers. Typical agent frameworks either lack confidentiality controls altogether or allow silent fallback to cloud models when local models experience outages or rate limits.

---

## 2. The Solution: Frugal Coder

**Frugal Coder** solves both problems from the architectural foundation:

- **AST Progressive Context Compression**: Slashes prompt context by **54% to 90%** by extracting abstract syntax tree (AST) skeletons, class contracts, function signatures, and docstrings before loading complete implementation bodies.
- **Central AI Gateway (Bifrost v2.5.1)**: Routes all non-confidential inference through a single, governed AI gateway on port 8080 with Virtual Key authorization, upstream latency tracking, and provider failover.
- **Groq API Cloud Provider**: High-speed, cost-efficient cloud inference (`openai/gpt-oss-120b` and `qwen/qwen3.8-27b`).
- **Strict Fail-Closed Confidential Inference**: Confidential repositories are physically prohibited from cloud egress at the architectural gate level. If local inference is offline, execution halts safely rather than leaking code to cloud providers.
- **Human-in-the-Loop Action Approval Engine**: Zero unapproved disk writes, command executions, or Git mutations. Binds single-use cryptographic tokens to pre-mutation file SHA-256 hashes.
- **Atomic Pre-Call Budget Enforcement**: Locks maximum estimated funds before dispatch and reconciles exact usage post-response against hard per-user spending limits.

---

## 3. System Architecture

```
[ Developer UI (Next.js 14 App Router :3000) ]
                      │ (HTTP REST / WebSocket Events)
                      ▼
[ FastAPI Backend Application (:8000) ]
   ├── Authentication & RBAC (PBKDF2-HMAC-SHA256, JWT)
   ├── Persistent SQLite Ledger (11 Relational Tables)
   ├── Token Optimization Engine (L0-L4 AST Skeletons + SHA-256 Cache)
   ├── Action Approval Engine (Cryptographic Single-Use Tokens)
   └── Independent Privacy Guard (Architectural Boundary)
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
                   └── Local Inference Runtime (:11434) (Ollama / llama.cpp / vLLM)
```

---

## 4. Key Features

- **L0–L4 Progressive Retrieval**:
  - `L0`: File tree and metadata discovery (zero file reads).
  - `L1`: AST Skeletons (classes, functions, signatures; bodies replaced with `...`).
  - `L2`: Imports, exports, and inter-module dependencies.
  - `L3`: Targeted file implementation (loaded only upon approval).
  - `L4`: Full context fallback.
- **SHA-256 Invalidation Cache**: Re-verifies content hashes before parsing; sub-millisecond cache hits for unchanged files.
- **Unified Diff Proposals & Rejection Safety**: Agent generates unified diffs; user rejection leaves files 100% unaltered.
- **Live WebSocket Feed**: Real-time event timeline streaming agent state, token savings, and diff proposals to the frontend.
- **Interactive Benchmark Dashboard**: Live comparison of baseline vs. optimized token usage, costs, and latencies across tasks.

---

## 5. Technology Stack

- **Backend**: Python 3.10+, FastAPI, Pydantic, SQLAlchemy, SQLite (WAL mode).
- **Frontend**: Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, Lucide Icons.
- **AI Gateway**: Bifrost v2.5.1 (`http://localhost:8080`).
- **Cloud Inference**: Groq Cloud API (`openai/gpt-oss-120b`, `qwen/qwen3.8-27b`).
- **Security**: PBKDF2-HMAC-SHA256, python-jose (JWT), secrets module.

---

## 6. Benchmark Methodology & Results

> **Experimental Control**: Model held strictly constant to **Groq (`qwen/qwen3.8-27b`)** routed through **Bifrost Gateway** across all trials. Evaluated over 5 distinct tasks × 3 trials each (30 live network requests).

| Metric | Baseline Arm (Full File) | Frugal Coder Arm (AST Skeleton) | Measured Impact |
| :--- | :--- | :--- | :--- |
| **Total Input Tokens** | 3,516 tokens | 1,614 tokens | **-54.10% context reduction** |
| **Total Incurred Cost** | $0.004019 | $0.001998 | **-50.28% direct cost savings** |
| **Average Latency** | 2,554.3 ms | 2,393.9 ms | **-6.28% faster latency** |
| **Task Correctness** | 100% | 100% | **Full functional parity** |
| **Unit Tests Passed** | 100% | 100% | **100% pass rate** |

*Raw trial data available in [benchmarks/BENCHMARK_RAW_RESULTS.json](benchmarks/BENCHMARK_RAW_RESULTS.json).*

---

## 7. Installation & Quickstart

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- Bifrost Gateway installed locally or runnable via npx

### 1. Clone & Configure
```bash
git clone https://github.com/your-username/frugal-coder.git
cd frugal-coder

# Copy environment template
cp .env.example .env
```
Edit `.env` and set your `GROQ_API_KEY` and `BIFROST_API_KEY`.

### 2. Start Bifrost AI Gateway
```bash
npx -y @maximhq/bifrost
```
Verify gateway health:
```bash
curl http://localhost:8080/health
# Returns: {"components":{"db_pings":"ok"},"status":"ok"}
```

### 3. Start Backend Application
```bash
# In project root
# Windows PowerShell:
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Linux / macOS:
PYTHONPATH=backend python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Interactive API documentation: `http://localhost:8000/api/v1/docs`.

### 4. Start Developer Frontend UI
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 8. Running Automated Tests & Benchmarks

### Backend Test Suite (14 Tests)
```bash
python -c "import sys, pytest; sys.path.insert(0, 'backend'); sys.exit(pytest.main(['backend/tests']))"
```

### Reproducible Benchmark Suite
```bash
python benchmarks/runner.py
```

### Frontend Production Build
```bash
cd frontend
npm run build
```

---

## 9. Security & Confidentiality Disclosure

- **Fail-Closed Boundary**: When local inference is offline, confidential repository AI requests halt execution immediately with a clear error message. Cloud fallback is strictly prohibited.
- **Hardware Sizing**: For local inference, we recommend `Qwen2.5-Coder-3B-Instruct` (Q4_K_M quantization, ~2.2 GB VRAM) on machines with 6 GB dedicated VRAM (e.g., RTX 3050).
- **Secret Hygiene**: All API keys, tokens, and database files are excluded from Git via `.gitignore`. Never commit `.env` or `bifrost_token.txt`.

---

## 10. Future Roadmap

- [ ] Multi-language AST parsing using Tree-sitter (Rust, Go, C++, Java).
- [ ] Embedded local llama-cpp runtime distribution for one-click confidential inference.
- [ ] Multi-tenant PostgreSQL support for enterprise deployments.
- [ ] IDE extensions for VS Code and JetBrains.

---

## 11. License

MIT License. See [LICENSE](LICENSE) for details.
