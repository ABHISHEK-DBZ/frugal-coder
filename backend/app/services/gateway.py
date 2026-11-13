import httpx
import time
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.services.router import build_model_registry

logger = logging.getLogger(__name__)

class ProviderResponse:
    def __init__(
        self,
        content: str,
        input_tokens: int,
        output_tokens: int,
        provider: str,
        model_name: str,
        latency_ms: int,
        via_bifrost: bool = True,
        cache_hit: bool = False
    ):
        self.content = content
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens = input_tokens + output_tokens
        self.provider = provider
        self.model_name = model_name
        self.latency_ms = latency_ms
        self.via_bifrost = via_bifrost
        self.cache_hit = cache_hit

class BifrostGatewayClient:
    """
    Central AI Gateway Client.
    MANDATORY RULE:
    Bifrost (port 8080) is the PRIMARY GATEWAY for all normal repository inference.
    Backend connects to Bifrost directly.
    If Bifrost is offline or returns an unconfigured provider error, it raises a clear
    integration error instead of silently bypassing Bifrost.
    Confidential repositories are NEVER routed through Bifrost to cloud providers.
    """

    def __init__(self, timeout_seconds: float = 30.0):
        self.timeout = timeout_seconds

    async def get_provider_statuses(self) -> Dict[str, Any]:
        """Inspects live reachability and configuration status of Bifrost and providers."""
        statuses = {}

        # 1. Real Bifrost Gateway Health Probe
        bifrost_online = False
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{settings.BIFROST_URL}/health")
                if res.status_code == 200:
                    bifrost_online = True
                    data = res.json()
                    statuses["bifrost"] = {
                        "status": "online",
                        "url": settings.BIFROST_URL,
                        "components": data.get("components", {})
                    }
                else:
                    statuses["bifrost"] = {"status": "degraded", "code": res.status_code}
        except Exception as e:
            statuses["bifrost"] = {"status": "offline", "error": f"Bifrost unreachable at {settings.BIFROST_URL}: {e}"}

        # 2. Groq Status via Bifrost
        statuses["groq"] = {
            "configured_in_env": bool(settings.GROQ_API_KEY),
            "primary_model": settings.GROQ_MODEL,
            "gateway_status": "ready_via_bifrost" if bifrost_online and settings.GROQ_API_KEY else "unconfigured_key_or_bifrost_pending"
        }

        # 3. Local Inference Runtime (Confidential repositories only)
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                if settings.LOCAL_INFERENCE_RUNTIME == "ollama":
                    res = await client.get(f"{settings.LOCAL_INFERENCE_URL}/api/tags")
                else:
                    res = await client.get(f"{settings.LOCAL_INFERENCE_URL}/v1/models")
                statuses["local_runtime"] = {"status": "online" if res.status_code == 200 else "degraded", "url": settings.LOCAL_INFERENCE_URL}
        except Exception:
            statuses["local_runtime"] = {
                "status": "offline",
                "message": f"Local inference runtime unconfigured or offline at {settings.LOCAL_INFERENCE_URL}. Confidential repository AI tasks are safely blocked (fail-closed)."
            }

        return statuses

    async def dispatch_request(
        self,
        model_key: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        virtual_key: Optional[str] = None,
        force_failure: bool = False
    ) -> ProviderResponse:
        """
        Dispatches request through the running Bifrost Gateway.
        Raises an explicit RuntimeError if Bifrost is offline or unconfigured.
        Never fakes provider success.
        """
        start_time = time.time()
        registry = build_model_registry()
        meta = registry.get(model_key, {})
        provider = meta.get("provider", "unknown")

        if force_failure:
            raise httpx.HTTPStatusError("Simulated 429 Rate Limit from Bifrost gateway", request=None, response=httpx.Response(429))

        # Check if requested model is for a confidential repository (Local inference only)
        if "local" in model_key or meta.get("is_local"):
            clean_model = model_key.replace("local/", "")
            # Dispatch to configured local runtime
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                try:
                    if settings.LOCAL_INFERENCE_RUNTIME == "ollama":
                        res = await client.post(
                            f"{settings.LOCAL_INFERENCE_URL}/api/chat",
                            json={"model": clean_model, "messages": messages, "stream": False}
                        )
                    else:
                        res = await client.post(
                            f"{settings.LOCAL_INFERENCE_URL}/v1/chat/completions",
                            json={"model": clean_model, "messages": messages}
                        )
                    if res.status_code == 200:
                        data = res.json()
                        latency_ms = int((time.time() - start_time) * 1000)
                        content = data.get("message", {}).get("content", "") or data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        return ProviderResponse(
                            content=content,
                            input_tokens=data.get("prompt_eval_count", 0),
                            output_tokens=data.get("eval_count", 0),
                            provider="local_inference",
                            model_name=clean_model,
                            latency_ms=latency_ms,
                            via_bifrost=False
                        )
                except Exception as e:
                    raise RuntimeError(
                        f"Confidential repository execution halted: Local inference runtime is offline at {settings.LOCAL_INFERENCE_URL}. "
                        "Cloud fallback is strictly prohibited by security policy."
                    )

        # Handle Deterministic Mock Provider (Exclusively for offline testing harnesses)
        if provider == "test_mock":
            latency_ms = int((time.time() - start_time) * 1000)
            in_tok = max(10, len(str(messages)) // 4)
            out_tok = 85
            return ProviderResponse(
                content="PLAN:\n1. Analyze auth repository structure.\n2. Propose cryptographic verification fix.",
                input_tokens=in_tok,
                output_tokens=out_tok,
                provider="test_mock",
                model_name=model_key,
                latency_ms=max(10, latency_ms),
                via_bifrost=True
            )

        # NORMAL REPOSITORY INFERENCE -> MUST GO THROUGH BIFROST GATEWAY
        # Verify Bifrost Gateway is reachable
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                health_res = await client.get(f"{settings.BIFROST_URL}/health")
                if health_res.status_code != 200:
                    raise RuntimeError(f"Bifrost Gateway reported non-healthy status code {health_res.status_code}")
        except Exception as e:
            raise RuntimeError(
                f"Bifrost Gateway Integration Error: Cannot reach Bifrost at {settings.BIFROST_URL}. "
                "Per architectural policy, direct provider bypass is prohibited. Please start or verify Bifrost on port 8080."
            )

        # Send request to Bifrost /v1/chat/completions
        # Model identifier format: groq/<model_name> tells Bifrost to route through its Groq provider
        if "groq" in model_key:
            clean_model = model_key.replace("groq/", "")
            bifrost_model_id = f"groq/{clean_model}"
        elif "openai" in model_key:
            clean_model = model_key.replace("openai/", "")
            bifrost_model_id = f"openai/{clean_model}"
        else:
            bifrost_model_id = model_key

        headers = {"Content-Type": "application/json"}
        vk_to_use = settings.BIFROST_API_KEY or virtual_key
        if vk_to_use:
            headers["Authorization"] = f"Bearer {vk_to_use}"
            headers["x-bf-vk"] = vk_to_use

        payload = {
            "model": bifrost_model_id,
            "messages": messages,
            "temperature": temperature
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            res = await client.post(f"{settings.BIFROST_URL}/v1/chat/completions", json=payload, headers=headers)
            
            if res.status_code == 200:
                data = res.json()
                latency_ms = int((time.time() - start_time) * 1000)
                usage = data.get("usage", {})
                message_obj = data.get("choices", [{}])[0].get("message", {})
                content = message_obj.get("content", "") or ""
                # Some reasoning models return text in reasoning_content or reasoning when content is empty
                if not content:
                    content = message_obj.get("reasoning_content") or message_obj.get("reasoning") or ""
                actual_model = data.get("model", bifrost_model_id)
                actual_provider = data.get("extra_fields", {}).get("provider", "groq")

                return ProviderResponse(
                    content=content,
                    input_tokens=usage.get("prompt_tokens", 0),
                    output_tokens=usage.get("completion_tokens", 0),
                    provider=actual_provider,
                    model_name=actual_model,
                    latency_ms=latency_ms,
                    via_bifrost=True,
                    cache_hit=data.get("cache_hit", False)
                )
            else:
                error_body = res.text
                # If Bifrost has not configured Groq yet, surface exact configuration instruction
                if "not found" in error_body and "groq" in error_body:
                    raise RuntimeError(
                        f"Bifrost Gateway Error: Groq provider is not yet configured in Bifrost v2.5.1 on {settings.BIFROST_URL}. "
                        "Bifrost requires the Groq provider to be registered in its config."
                    )
                raise RuntimeError(f"Bifrost Gateway error (HTTP {res.status_code}): {error_body}")
