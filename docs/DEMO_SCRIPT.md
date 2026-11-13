# 5-MINUTE LIVE DEMONSTRATION SCRIPT
**Project:** Frugal Coder — The Budget-Aware, Privacy-First AI Coding Agent  
**Presenter Target Time:** 5 Minutes 00 Seconds  

---

## [0:00 - 0:45] Minute 1: The Problem & The Frugal Coder Vision
- **Speaker**:
  > *"Every software engineering team wants autonomous coding agents, but reality hits with two massive roadblocks: runaway token bills that bankrupt projects, and the terrifying risk of proprietary source code leaking into public cloud LLMs.*
  > *Meet Frugal Coder: The Budget-Aware, Privacy-First AI Coding Agent. Tagline: Build Smarter. Spend Less. Ship Securely."*
- **Visual**:
  - Show the dark IDE-style interface at `http://localhost:3000`.
  - Highlight the top navigation: Real-time Budget Cap, Bifrost Ready indicator, and the four clean tabs (Workspace, Token Analytics, Security & Audit, Budget Control).

---

## [0:45 - 1:45] Minute 2: Repository Connection & AST Progressive Compression
- **Speaker**:
  > *"Instead of dumping entire repositories into context windows like naive chatbots, Frugal Coder uses AST Progressive Compression. Let's connect our repository and enter a coding task: 'Find the authentication bug in this repository. Propose a cryptographic fix and explain before applying.'*
  > *Notice the execution timeline on the right: The agent first scans L0 directory trees, then extracts L1 AST skeletons—capturing only class signatures and function interfaces without bulky bodies. We've just cut our prompt context by over 60% before touching the network."*
- **Visual**:
  - Click **Launch Frugal Agent**.
  - Show live WebSocket timeline events: `repository_indexed`, `task_classified`, `context_assembled (L1 Skeleton: tokens saved)`, and `model_selected`.

---

## [1:45 - 2:45] Minute 3: Central Bifrost Gateway & Live Groq Inference
- **Speaker**:
  > *"Notice where the request goes: It routes strictly through Bifrost, our central AI gateway on port 8080, authenticating with a secure Virtual Key. Bifrost forwards the compressed context to the Groq API running OpenAI's open-source weights. In less than two seconds, we receive our response without bypassing gateway security or logging secrets."*
- **Visual**:
  - Point to timeline: `model_call_completed` with real latency, input/output tokens, and cost.
  - Show the Approval Bar popping up in the center editor with a clear unified diff.

---

## [2:45 - 3:45] Minute 4: The Action Approval Gate (Rejection & Execution)
- **Speaker**:
  > *"Frugal Coder enforces human-in-the-loop authorization. An AI agent should never mutate code or execute commands without explicit consent. Notice our generated patch diff. Let's first test what happens if a developer REJECTS the patch.*
  > *Clicking 'Reject Action': The file hash is immediately re-verified. Exactly zero mutations occurred. The repository is untouched.*
  > *Now, the developer reviews the cryptographic fix and clicks 'Approve & Execute'. The patch is applied, file hashes are updated, and the test suite is executed in the background—all unit tests pass!"*
- **Visual**:
  - Click **Reject Action** -> Show alert and unchanged file.
  - Show approved patch applied with green diff and passing test output in timeline.

---

## [3:45 - 4:30] Minute 5: Token & Cost Benchmark Analytics
- **Speaker**:
  > *"Let's switch to the Token Analytics tab. Here is our live reproducible benchmark suite: 5 representative coding tasks, 3 trials each, 30 live network inferences through Bifrost holding the model constant.*
  > *The result? A measured 54.10% reduction in input tokens, a 50.28% direct cost reduction, and faster latencies across the board with 100% test pass rate."*
- **Visual**:
  - Switch to **Token Analytics** tab.
  - Show high-level savings cards and the benchmark table with per-task numbers.

---

## [4:30 - 5:00] Wrap-up & Privacy Invariant
- **Speaker**:
  > *"Finally, if this repository were marked confidential, Frugal Coder's independent Privacy Guard would physically block all cloud egress. If local inference is offline, it fails closed—never leaking a single token to cloud providers.*
  > *Frugal Coder delivers the power of autonomous AI coding with the safety, budget controls, and privacy that enterprise engineering demands. Thank you!"*

