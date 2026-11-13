from typing import Dict, Any, Tuple
from app.core.config import settings

def build_model_registry() -> Dict[str, Dict[str, Any]]:
    return {
        # Local Inference (Exclusively for confidential repositories or offline development)
        f"local/{settings.LOCAL_MODEL}": {
            "provider": settings.LOCAL_INFERENCE_RUNTIME,
            "tier": "local",
            "cost_per_1k_input": 0.0,
            "cost_per_1k_output": 0.0,
            "context_window": 32768,
            "is_local": True
        },
        # Primary Cloud Provider: Groq (Fast, highly cost-efficient Llama-3.3-70b)
        f"groq/{settings.GROQ_MODEL}": {
            "provider": "groq",
            "tier": "primary_cloud",
            "cost_per_1k_input": 0.00059,
            "cost_per_1k_output": 0.00079,
            "context_window": 128000,
            "is_local": False
        },
        # Secondary Cloud Failover Provider: OpenAI gpt-4o-mini
        f"openai/{settings.OPENAI_MODEL}": {
            "provider": "openai",
            "tier": "secondary_cloud",
            "cost_per_1k_input": 0.00015,
            "cost_per_1k_output": 0.00060,
            "context_window": 128000,
            "is_local": False
        },
        # Frontier Cloud Provider: OpenAI gpt-4o (Reserved for high-complexity architectural tasks)
        "openai/gpt-4o": {
            "provider": "openai",
            "tier": "frontier_cloud",
            "cost_per_1k_input": 0.0025,
            "cost_per_1k_output": 0.0100,
            "context_window": 128000,
            "is_local": False
        },
        # Deterministic Test Providers for testing failover and boundary conditions
        "test/mock-groq-primary": {
            "provider": "test_mock",
            "tier": "primary_cloud",
            "cost_per_1k_input": 0.0005,
            "cost_per_1k_output": 0.0008,
            "context_window": 32000,
            "is_local": False
        },
        "test/mock-secondary-cloud": {
            "provider": "test_mock",
            "tier": "secondary_cloud",
            "cost_per_1k_input": 0.0002,
            "cost_per_1k_output": 0.0006,
            "context_window": 32000,
            "is_local": False
        },
        "test/mock-local-model": {
            "provider": "test_mock",
            "tier": "local",
            "cost_per_1k_input": 0.0,
            "cost_per_1k_output": 0.0,
            "context_window": 32000,
            "is_local": True
        }
    }

MODEL_REGISTRY = build_model_registry()

class IntelligentModelRouter:
    """
    Intelligent Model Router adhering to Phase 2 Directives:
    - Groq = Primary inference provider for normal repositories.
    - Secondary Cloud = Fallover for normal repositories only.
    - Local inference = Exclusively for confidential repositories.
    - Confidential repositories NEVER fall back to cloud.
    """

    @staticmethod
    def classify_task(task_description: str) -> str:
        """Classifies developer task into complexity categories."""
        desc = task_description.lower()
        if any(w in desc for w in ["architecture", "redesign", "system design", "refactor architecture"]):
            return "architecture"
        elif any(w in desc for w in ["multi-file", "across modules", "full refactor", "migrate"]):
            return "multi_file_change"
        elif any(w in desc for w in ["bug", "fix", "error", "exception", "broken", "traceback"]):
            return "simple_bug"
        elif any(w in desc for w in ["summarize", "explain", "overview", "describe", "readme"]):
            return "summarization"
        else:
            return "classification"

    @classmethod
    def select_model(cls, task_category: str, is_confidential: bool) -> Tuple[str, Dict[str, Any]]:
        """
        Selects model based on confidentiality and task category.
        If is_confidential is True, STRICTLY routes to configured local inference runtime.
        If not confidential, DEFAULT PRIMARY is Groq.
        """
        registry = build_model_registry()
        
        if is_confidential:
            local_key = f"local/{settings.LOCAL_MODEL}"
            return local_key, registry.get(local_key, registry["test/mock-local-model"])

        # For normal repositories: Groq is the default primary provider
        groq_key = f"groq/{settings.GROQ_MODEL}"
        
        # Only complex architecture tasks optionally escalate to frontier cloud
        if task_category == "architecture" and settings.OPENAI_API_KEY:
            frontier_key = "openai/gpt-4o"
            return frontier_key, registry.get(frontier_key, registry[groq_key])
            
        return groq_key, registry.get(groq_key, registry["test/mock-groq-primary"])

    @classmethod
    def get_fallback_model(cls, current_model: str, is_confidential: bool) -> Tuple[str, Dict[str, Any]]:
        """
        Provides fallback model when primary provider fails (e.g. Rate Limit 429).
        STRICT GUARANTEE:
        Confidential repositories NEVER fallback to Groq or any cloud provider.
        """
        registry = build_model_registry()

        if is_confidential:
            # Confidential repos have NO cloud fallback. Must fail closed or try backup local model.
            raise RuntimeError(
                "Confidential repository policy: Local inference unavailable and cloud fallback is strictly forbidden."
            )
            
        # Normal repository fallback: Groq -> Secondary Cloud (e.g. OpenAI)
        if "groq" in current_model:
            secondary_key = f"openai/{settings.OPENAI_MODEL}"
            return secondary_key, registry.get(secondary_key, registry["test/mock-secondary-cloud"])
        else:
            fallback_key = "test/mock-secondary-cloud"
            return fallback_key, registry[fallback_key]
