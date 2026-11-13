# BENCHMARK METHODOLOGY: REPRODUCIBLE TOKEN & COST MEASUREMENT
**Project:** Frugal Coder — The Budget-Aware, Privacy-First AI Coding Agent  
**Date:** November 13, 2026  
**Provider & Gateway:** Groq API routed through Bifrost v2.5.1 Gateway  

---

## 1. Methodology & Experimental Controls

To eliminate confounding variables (e.g. comparing smaller models against larger models), this benchmark suite strictly adheres to the following scientific controls:

1. **Model & Provider Invariance**:
   - The identical model (`groq/qwen/qwen3.8-27b`) is used for both the **Baseline** and **Frugal Coder (Optimized)** arms.
   - Both requests travel through the exact same **Bifrost AI Gateway** (`http://localhost:8080`) using identical Virtual Key authentication (`bf-vk-frugal-coder-dev`).
2. **Repetition & Statistical Rigor**:
   - Five distinct, representative software engineering coding tasks are evaluated.
   - Each task is executed over **3 separate trials** (15 total runs per arm, 30 live network inferences).
3. **Hardware & Environment Consistency**:
   - Single machine execution (Windows 11, AMD Ryzen 5 6600H, 16 GB RAM).
   - Network calls to Groq API monitored with exponential backoff on HTTP 429 rate limits.
4. **Separation of Context Reduction from Billed Reduction**:
   - **Context Reduction**: Input token delta between full-file baseline and AST skeleton prompt.
   - **Billed Reduction**: Total billed tokens (input + output) multiplied by official Groq pricing rates ($0.00059 / 1k input, $0.00079 / 1k output).

---

## 2. Representative Coding Tasks Evaluated

| Task ID | Task Domain | Description |
| :--- | :--- | :--- |
| `task_1_auth_fix` | **Authentication Security** | Insecure plain-text password comparison in `authenticate()` requiring cryptographic verification. |
| `task_2_sql_injection` | **Database Security** | String formatted query in `get_user_by_email()` requiring parameterized query conversion. |
| `task_3_rate_limiting` | **Systems Engineering** | Token bucket algorithm logic analyzing elapsed time and token capacity checks. |
| `task_4_jwt_expiration` | **API Token Security** | Token decode routine omitting expiration (`exp`) claim verification. |
| `task_5_cache_invalidation` | **Performance Engineering** | Content hash comparison against cached AST skeleton for cache hits. |

---

## 3. Data Collection Protocol

For every trial, the response payload from Bifrost is inspected directly:
- `usage.prompt_tokens` -> Recorded as **Input Tokens**.
- `usage.completion_tokens` -> Recorded as **Output Tokens**.
- `usage.total_tokens` -> Recorded as **Total Tokens**.
- High-resolution wall-clock timer -> Recorded as **Latency (ms)**.
- Response text inspected -> Verified for **Task Correctness & Code Accuracy**.

All raw trial records are saved immediately to `BENCHMARK_RAW_RESULTS.json`.

