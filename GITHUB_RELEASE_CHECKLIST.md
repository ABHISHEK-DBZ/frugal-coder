# GITHUB RELEASE CHECKLIST: FRUGAL CODER
**Project:** Frugal Coder — The Budget-Aware, Privacy-First AI Coding Agent  
**Date:** November 13, 2026  
**Status:** **AUDITED & READY FOR PUBLIC STAGING**  

---

## 1. Pre-Publishing Audit Matrix

| Verification Area | Check Description | Status | Evidence / Notes |
| :--- | :--- | :---: | :--- |
| **Secret Scanning** | `.env` and `bifrost_token.txt` excluded from Git | **PASS** | Verified via `git check-ignore -v .env bifrost_token.txt`. |
| **Template Sanitization** | `.env.example` has placeholder keys only | **PASS** | Verified: contains only `your-groq-api-key-here` and placeholders. |
| **Database Isolation** | `*.db`, `*.db-wal`, `*.db-shm` excluded from Git | **PASS** | Verified via `git check-ignore -v frugal_coder.db`. |
| **Repository Hygiene** | Scratch scripts and temp database files deleted | **PASS** | Removed all `test_*.db`, `check_*.py`, and debug scripts. |
| **Directory Structure** | Clean hierarchy (`frontend/`, `backend/`, `docs/`, `benchmarks/`, `examples/`) | **PASS** | Verified organized and accessible. |
| **Backend Test Suite** | 14 / 14 Pytest tests passing | **PASS** | Passed in 6.42s with zero failures. |
| **Frontend Build** | Next.js 14 production build succeeds | **PASS** | `npm run build` compiled all routes without warnings. |
| **Gateway Routing** | Bifrost v2.5.1 on port 8080 routing to Groq | **PASS** | Live HTTP 200 OK responses with usage captured. |
| **Confidential Boundary** | Fail-closed behavior preserved | **PASS** | Cloud fallback strictly prohibited; halts safely. |
| **Benchmark Dashboard** | Reads persisted raw trial results | **PASS** | `GET /api/v1/benchmarks/results` serves `BENCHMARK_RAW_RESULTS.json`. |

---

## 2. Secrets Rotation Guidance (If Previously Leaked)

If any credential was ever exposed in public commits or external logs:
1. **Groq API Key**: Go to [console.groq.com/keys](https://console.groq.com/keys) -> Revoke existing key -> Generate new API key -> Update local `.env`.
2. **Bifrost Setup Token**: Update `BIFROST_SETUP_TOKEN` environment variable and restart Bifrost.
3. **Bifrost Virtual Keys**: Navigate to `http://localhost:8080` (Bifrost Dashboard) -> Virtual Keys -> Revoke compromised key -> Re-issue new Virtual Key.
4. **JWT Secret Key**: Update `SECRET_KEY` in `.env` to invalidate existing sessions.

