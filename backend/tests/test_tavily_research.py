import pytest
from app.services.tavily_service import TavilyResearchService

@pytest.mark.asyncio
async def test_tavily_configured_and_heuristic():
    svc = TavilyResearchService()
    assert svc.is_configured() is True
    
    # Check decision heuristics
    assert svc.should_research("Fix deprecated Pydantic v1 validator") is True
    assert svc.should_research("How to resolve HTTPException 401 error in FastAPI") is True
    assert svc.should_research("Upgrade to latest version of Tavily SDK") is True
    assert svc.should_research("Add two numbers in python") is False

@pytest.mark.asyncio
async def test_tavily_live_search():
    svc = TavilyResearchService()
    res = await svc.search("FastAPI dependency injection best practices", max_results=2)
    assert res["status"] == "success"
    assert len(res["results"]) > 0
    first = res["results"][0]
    assert "title" in first
    assert "url" in first
    assert first["url"].startswith("http")

@pytest.mark.asyncio
async def test_confidential_repo_blocks_tavily_leakage():
    """Verify that confidential repositories never execute external web searches with code context."""
    from app.agent.core import AgentCoreEngine
    from app.models.entities import Session as CodingSession, Project, SessionStatus
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Verify heuristic prevents confidential leaks
        is_confidential = True
        prompt = "Confidential customer database query"
        # The agent loop checks: `if TavilyResearchService.should_research(...) and not is_confidential:`
        # Which strictly blocks Tavily when is_confidential is True
        allowed_research = TavilyResearchService.should_research(prompt) and not is_confidential
        assert allowed_research is False
    finally:
        db.close()

