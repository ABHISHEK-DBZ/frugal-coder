# KNOWN LIMITATIONS & ROADMAP
**Project:** Frugal Coder — The Budget-Aware, Privacy-First AI Coding Agent  
**Date:** November 13, 2026  
**Disclosure Standard:** Honest Engineering Disclosure (No Hand-waving)  

---

## 1. Operational Limitations in Current Prototype

### 1.1 Local Inference Runtime Availability
- **Current State**: On the current evaluation host, no background local runtime (e.g., Ollama or llama-server daemon) is actively running on port 11434.
- **Enforced Behavior**: Frugal Coder strictly **fails closed**. Confidential repositories halt execution with a clear, honest error message and refuse to fall back to Groq or any cloud provider.
- **Roadmap Resolution**: Support one-click embedded llama-cpp-python binaries packaged directly with the agent distribution.

### 1.2 Rate Limiting on Groq Free-Tier API
- **Current State**: Heavy sequential benchmarking against Groq endpoints triggers occasional HTTP 429 rate limit errors (8,000 token/min ceiling on free development keys).
- **Enforced Behavior**: Handled via exponential backoff in the benchmark runner and automated secondary cloud provider failover in production agent sessions.
- **Roadmap Resolution**: Integrate local batch queues and client-side token bucket rate limiters to smooth traffic spikes.

### 1.3 AST Language Support
- **Current State**: Comprehensive AST parsing for Python (`ast` standard library module) and regex/symbol extraction for JavaScript and TypeScript.
- **Roadmap Resolution**: Integrate Tree-sitter bindings for multi-language AST extraction (Rust, Go, C++, Java, Kotlin).

### 1.4 Single-User SQLite Default
- **Current State**: SQLite with WAL mode is used for simple zero-dependency local deployments.
- **Roadmap Resolution**: Support PostgreSQL for multi-tenant enterprise agent deployments.

