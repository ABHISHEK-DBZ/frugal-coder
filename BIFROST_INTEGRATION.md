# BIFROST GATEWAY INTEGRATION

**Frugal Coder** integrates **Bifrost by Maxim AI** as its primary centralized AI gateway.

---

## 1. Bifrost Gateway Role & Architecture

All inference for public and standard repositories is governed and routed through the local Bifrost daemon running on `http://localhost:8080`.

- **Gateway URL**: `http://localhost:8080`
- **Virtual Key**: `bf-vk-frugal-coder-dev`
- **Primary Cloud Provider**: Groq (`openai/gpt-oss-120b`, `openai/gpt-oss-20b`)
- **Secondary Failover**: Configured through Bifrost fallback routing

```
                     ┌───────────────────────────┐
                     │   Frugal Coder Backend    │
                     └─────────────┬─────────────┘
                                   │ (HTTP/REST Virtual Key)
                                   ▼
                     ┌───────────────────────────┐
                     │   Bifrost Gateway v2.5.1  │
                     │      localhost:8080       │
                     └─────────────┬─────────────┘
                                   │ (High-throughput API)
                                   ▼
                     ┌───────────────────────────┐
                     │       Groq Provider       │
                     │      Llama-3.3-70B        │
                     └───────────────────────────┘
```

---

## 2. Key Capabilities Verified

1. **Virtual Key Authentication**: Frugal Coder uses virtual key tokens rather than exposing raw provider secrets directly.
2. **Provider Failover Chains**: Outages or 429 rate limit triggers are intercepted and routed through fallbacks.
3. **Usage & Cost Tracking**: Provider-reported token counts and latency metrics are reconciled into the database for transparent developer billing.
4. **Physical Boundary for Confidential Repositories**: Bifrost cloud inference is strictly blocked for confidential repositories; only air-gapped local runtimes are permitted.

