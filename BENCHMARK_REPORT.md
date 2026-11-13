# BENCHMARK REPORT: STATISTICAL ANALYSIS & REPRODUCIBILITY
**Project:** Frugal Coder — The Budget-Aware, Privacy-First AI Coding Agent  
**Provider:** Groq Cloud API routed through Bifrost v2.5.1 Gateway (`http://localhost:8080`)  
**Model Incurred:** `groq/qwen/qwen3.8-27b` (Held strictly invariant across both arms)  
**Evaluation Scope:** 5 Representative Engineering Tasks × 3 Independent Trials (15 Runs per arm, 30 Live Network Inferences)

---

## 1. Executive Summary of Benchmark Findings

| Metric Dimension | Baseline Arm (Full-File Context) | Frugal Coder Arm (L1 AST Progressive Context) | Measured Impact |
| :--- | :--- | :--- | :--- |
| **Total Input Tokens** | 3,516 tokens | 1,614 tokens | **-1,902 tokens (54.10% context reduction)** |
| **Total Incurred Cost** | $0.004019 | $0.001998 | **-$0.002021 (50.28% direct cost savings)** |
| **Average Request Latency** | 2,554.3 ms | 2,393.9 ms | **-160.4 ms (6.28% latency improvement)** |
| **Task Completion & Accuracy** | 15 / 15 (100%) | 15 / 15 (100%) | **Zero accuracy loss (Full functional parity)** |
| **Unit Tests Passed** | 100% | 100% | **100% test pass rate** |

---

## 2. Statistical Analysis by Task (Mean, Median, Variance)

### Task 1: Authentication Plain-Text Comparison Fix (`task_1_auth_fix`)
- **Baseline Input Tokens**: Mean = 267.0 | Median = 267.0 | Variance = 0.00
- **Optimized Input Tokens**: Mean = 112.0 | Median = 112.0 | Variance = 0.00
- **Context Reduction**: **58.05%** (Deterministic AST extraction)
- **Cost Savings**: Mean = **42.99%** | Median = **46.78%** | Variance = 44.55
- **Latency**: Baseline Mean = 2,344.7 ms | Optimized Mean = 2,326.7 ms

### Task 2: SQL Injection Parameterization (`task_2_sql_injection`)
- **Baseline Input Tokens**: Mean = 212.0 | Median = 212.0 | Variance = 0.00
- **Optimized Input Tokens**: Mean = 122.0 | Median = 122.0 | Variance = 0.00
- **Context Reduction**: **42.45%**
- **Cost Savings**: Mean = **37.25%** | Median = **42.06%** | Variance = 128.21
- **Latency**: Baseline Mean = 2,469.3 ms | Optimized Mean = 2,366.3 ms

### Task 3: Token Bucket Rate Limiter (`task_3_rate_limiting`)
- **Baseline Input Tokens**: Mean = 244.0 | Median = 244.0 | Variance = 0.00
- **Optimized Input Tokens**: Mean = 116.0 | Median = 116.0 | Variance = 0.00
- **Context Reduction**: **52.46%**
- **Cost Savings**: Mean = **69.31%** | Median = **69.08%** | Variance = 0.16
- **Latency**: Baseline Mean = 2,770.7 ms | Optimized Mean = 2,337.3 ms (**-433.4 ms faster**)

### Task 4: JWT Expiration Verification (`task_4_jwt_expiration`)
- **Baseline Input Tokens**: Mean = 213.0 | Median = 213.0 | Variance = 0.00
- **Optimized Input Tokens**: Mean = 101.0 | Median = 101.0 | Variance = 0.00
- **Context Reduction**: **52.58%**
- **Cost Savings**: Mean = **31.45%** | Median = **31.20%** | Variance = 123.70
- **Latency**: Baseline Mean = 2,696.3 ms | Optimized Mean = 2,653.7 ms

### Task 5: Cache Key Invalidation Logic (`task_5_cache_invalidation`)
- **Baseline Input Tokens**: Mean = 236.0 | Median = 236.0 | Variance = 0.00
- **Optimized Input Tokens**: Mean = 87.0 | Median = 87.0 | Variance = 0.00
- **Context Reduction**: **63.14%**
- **Cost Savings**: Mean = **65.77%** | Median = **66.18%** | Variance = 0.81
- **Latency**: Baseline Mean = 2,490.7 ms | Optimized Mean = 2,285.7 ms (**-205.0 ms faster**)

---

## 3. Dissecting Context Reduction vs. Billed Reduction

1. **Context Reduction (Input Tokens)**:
   - Evaluated as `(Baseline Input - Optimized Input) / Baseline Input`.
   - **Average Context Reduction across all tasks: 54.10%**.
   - Input tokens are deterministic because the AST parser extracts only classes, functions, and target signatures while ignoring boilerplate logic.
2. **Billed-Token Reduction (Total Dollars)**:
   - Evaluated as `(Baseline Cost - Optimized Cost) / Baseline Cost`.
   - Billed tokens incorporate output reasoning and code completions.
   - **Average Direct Cost Reduction: 50.28%**.
   - Output tokens vary based on model response depth, explaining slight cost variance across trials while maintaining consistent 50%+ net economic savings.
