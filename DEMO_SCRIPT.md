# FIVE-MINUTE HACKATHON DEMONSTRATION SCRIPT

**Project:** FRUGAL CODER  
**Time Limit:** 5 Minutes  
**Presenters:** Hackathon Team  

---

### Phase 1: The Problem (0:00 – 0:30)
- **Visual**: Show traditional AI tools consuming massive prompt tokens, exceeding budgets, and hallucinating on outdated documentation.
- **Narrative**: "Modern AI coding agents burn through cloud budgets by stuffing entire codebases into prompts, hallucinate when libraries change, and leak proprietary IP. Meet **Frugal Coder**: The budget-aware, privacy-first, research-driven AI coding agent."

---

### Phase 2: Product Overview & UI (0:30 – 1:00)
- **Visual**: Show Frugal Coder IDE (`http://localhost:3000`) in dark mode.
- **Narrative**: "Notice the developer workspace: repository explorer on the left, multi-tab code editor with AST compression metrics in the center, and the autonomous agent on the right. Notice our live status badges: Bifrost Gateway Online and Tavily Research Ready."

---

### Phase 3: Centralized Bifrost AI Gateway (1:00 – 1:45)
- **Visual**: Show the top right `Bifrost Gateway: Online` indicator and model routing trace.
- **Narrative**: "Frugal Coder centralizes all cloud inference through **Bifrost by Maxim AI** running locally on port 8080. We use Virtual Keys for security, automate failover chains, and route high-throughput tasks to Groq with sub-millisecond overhead."

---

### Phase 4: Autonomous Research with Tavily (1:45 – 2:30)
- **Visual**: Click on **Research Center** tab. Type `"FastAPI lifespan events vs on_event"`. Show real-time synthesized answer and verified documentation source links. Click `"Use in Agent →"`.
- **Narrative**: "When dealing with breaking changes, the agent shouldn't guess. We integrated **Tavily Search API**. The agent autonomously evaluates whether technical documentation or CVE advisories are needed, retrieves verified sources, and incorporates citations into its reasoning."

---

### Phase 5: AST Context Compression & Token Analytics (2:30 – 3:15)
- **Visual**: Switch to **Token Analytics** tab. Show the 4 KPI cards and 15 reproducible benchmark trials.
- **Narrative**: "Rather than sending raw files, Frugal Coder uses AST skeletons to extract interface contracts. Across 15 benchmark trials, we achieved a **54.10% input token reduction** and **50.28% API cost reduction** holding model and provider constant."

---

### Phase 6: Autonomous Coding & Developer Approval (3:15 – 4:15)
- **Visual**: In Workspace, click **Launch Agent**. Watch the real-time execution timeline stream events via WebSockets. Review the proposed diff, click **Reject** (verify file unchanged), click **Approve** (verify patch applied).
- **Narrative**: "Frugal Coder generates clean, minimal patches. It enforces human approval before any disk modification and validates SHA-256 integrity."

---

### Phase 7: Strict Privacy Boundary & Closing (4:15 – 5:00)
- **Visual**: Click repository privacy badge to switch to **Confidential / Local-Only**. Show fail-closed boundary preventing cloud egress.
- **Narrative**: "For proprietary code, Frugal Coder has a strict fail-closed boundary: zero data leaves for cloud providers or search engines. Combined with Bifrost and Tavily, Frugal Coder lets developers build smarter, research better, spend less, and ship securely."
