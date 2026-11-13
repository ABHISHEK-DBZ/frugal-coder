# FRUGAL CODER — PITCH DECK OUTLINE

**Competition:** Global AI Hackathon 2026 (HackCulture / Geek Room)  
**Track:** Combined Bifrost (Maxim AI) + Tavily Search API Project  

---

### Slide 1: Title & Positioning
- **Header**: FRUGAL CODER
- **Tagline**: The Budget-Aware, Privacy-First, Research-Driven AI Coding Agent
- **Footer**: Powered by Bifrost AI Gateway & Tavily Search API

### Slide 2: The Core Problem
- 70% of tokens in autonomous AI agents are wasted on redundant context.
- High developer spend with uncontrolled recursive agent loops.
- Hallucinations caused by outdated training data on breaking library changes.
- Proprietary enterprise source code leaked to third-party model providers.

### Slide 3: Why Existing AI Tools Fall Short
- Full-file context stuffing creates quadratic token costs.
- Static prompt-based security breaks under prompt injection.
- Unmonitored direct cloud connections bypass company budget controls.

### Slide 4: The Frugal Coder Solution
- **AST Progressive Context Compression**: Extracts structural interfaces, reducing tokens by >50%.
- **Bifrost by Maxim AI**: Centralized drop-in gateway with Virtual Key security and budget reconciliation.
- **Tavily Technical Research**: Live documentation discovery and citation verification for breaking changes.
- **Fail-Closed Privacy Boundary**: Strict physical air-gap for confidential repositories.

### Slide 5: Product Demonstration
- Live IDE Walkthrough: 3-panel developer workspace (Explorer, Multi-Tab Editor, Autonomous Agent).
- Real-time WebSocket streaming of agent execution steps.
- Interactive side-by-side diff review with human-in-the-loop approval.

### Slide 6: Centralized AI Gateway — Bifrost Integration
- Local Bifrost daemon running on port 8080.
- Virtual Key isolation (`bf-vk-frugal-coder-dev`).
- Real-time latency tracking and automatic multi-tier provider fallbacks.
- Primary provider: Groq (Llama-3.3-70B).

### Slide 7: Technical Web Research — Tavily Search API
- Autonomous heuristic: decides when a task requires external documentation.
- Real-time search retrieval of verified citations and technical excerpts.
- Seamless context injection into the coding agent prior to LLM reasoning.

### Slide 8: Technical Architecture
- Architectural block diagram showcasing Next.js frontend, FastAPI backend, AST Engine, Bifrost Gateway, and Tavily Search.

### Slide 9: Measured Benchmark Results
- 15 reproducible trials across 5 representative development tasks.
- **54.10% Input Token Reduction**.
- **50.28% Direct API Cost Reduction**.
- **6.28% Latency Improvement**.
- 100% Task Correctness and Test Pass Rate.

### Slide 10: Security & Fail-Closed Privacy Policy
- Non-confidential repositories: Routed through Bifrost and Groq.
- Confidential repositories: Strictly routed to air-gapped local models.
- If local model is offline: execution halts safely; cloud fallback is physically blocked.

### Slide 11: Future Roadmap
- Local Ollama/vLLM auto-provisioning for one-click confidential inference.
- Multi-repo cross-service AST dependency graph resolution.
- Enterprise team budget quotas and shared team snippet cache.

### Slide 12: Conclusion & Call to Action
- "Build Smarter. Research Better. Spend Less. Ship Securely."
- Open-source GitHub release ready for developer evaluation.

