# FINAL SUBMISSION README — FRUGAL CODER
**"Build Smarter. Spend Less. Ship Securely."**  
**Hackathon Prototype Submission:** November 15, 2026  

---

## 1. What is Frugal Coder?

Frugal Coder is the budget-aware, privacy-first autonomous AI coding agent designed for engineering teams that cannot afford uncontrolled cloud LLM token expenses or privacy leaks of proprietary source code.

### Core Innovations:
1. **AST-Based Progressive Context Compression**: Slashes input tokens by **54% to 90%** by extracting AST signatures, classes, and function contracts before loading full implementation code.
2. **Central Bifrost AI Gateway Integration**: All cloud inference routes through Bifrost v2.5.1 with virtual keys, health monitoring, and provider resilience.
3. **Groq API as Primary Cloud Provider**: Fast, cost-efficient inference utilizing `openai/gpt-oss-120b` and `qwen/qwen3.8-27b`.
4. **Strict Fail-Closed Confidential Inference**: Confidential repositories are physically blocked from cloud egress. If local inference is offline, execution halts safely.
5. **Human-in-the-Loop Action Approval Engine**: Zero unapproved disk writes, command executions, or Git mutations. Binds cryptographic tokens to pre-mutation file SHA-256 hashes.
6. **Atomic Budget Enforcement**: Pre-call reservation and post-call reconciliation against per-user spending limits.

---

## 2. Quick Start & Execution Guide

### Prerequisites
- Python 3.10+ (Installed with virtualenv or system Python)
- Node.js 18+ & npm
- Bifrost v2.5.1 running at `http://localhost:8080`
- Groq API Key in `.env`

### Step 1: Start Bifrost Gateway
```bash
# In Bifrost installation directory or via npx
npx -y @maximhq/bifrost
```
Ensure port 8080 responds: `curl http://localhost:8080/health`

### Step 2: Start Backend Application
```bash
# Set PYTHONPATH and launch FastAPI
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Backend API docs available at: `http://localhost:8000/api/v1/docs`

### Step 3: Start Developer Frontend UI
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` to interact with Frugal Coder.

---

## 3. Running Automated Tests & Benchmarks

### Run Pytest Test Suite (14 Tests)
```bash
python -c "import sys, pytest; sys.path.insert(0, 'backend'); sys.exit(pytest.main(['backend/tests']))"
```

### Run Reproducible Benchmark Suite
```bash
python run_phase5_benchmarks.py
```
Outputs raw data to `BENCHMARK_RAW_RESULTS.json` and updates the frontend analytics tab.

---

## 4. Key Documentation Index

- [FINAL_ARCHITECTURE.md](file:///c:/Users/Abhishek/Downloads/loopos/FINAL_ARCHITECTURE.md): Complete system topology, component interactions, and data models.
- [DEMO_SCRIPT.md](file:///c:/Users/Abhishek/Downloads/loopos/DEMO_SCRIPT.md): Five-minute step-by-step hackathon presentation guide.
- [BENCHMARK_REPORT.md](file:///c:/Users/Abhishek/Downloads/loopos/BENCHMARK_REPORT.md): Statistical token and cost analysis holding Groq constant.
- [SECURITY_REPORT.md](file:///c:/Users/Abhishek/Downloads/loopos/SECURITY_REPORT.md): Threat modeling, prompt injection defenses, and audit logging.
- [KNOWN_LIMITATIONS.md](file:///c:/Users/Abhishek/Downloads/loopos/KNOWN_LIMITATIONS.md): Transparent disclosure of operational limits and roadmap items.
- [FINAL_SUBMISSION_CHECKLIST.md](file:///c:/Users/Abhishek/Downloads/loopos/FINAL_SUBMISSION_CHECKLIST.md): Verification matrix for prototype submission.

