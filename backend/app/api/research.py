from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from app.auth.security import get_current_user
from app.models.entities import User
from app.services.tavily_service import TavilyResearchService

router = APIRouter(prefix="/research", tags=["Research & Tavily"])

class ResearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 4
    search_depth: Optional[str] = "basic"
    include_domains: Optional[List[str]] = None

class ResearchResultItem(BaseModel):
    title: str
    url: str
    content: str
    score: float

class ResearchResponse(BaseModel):
    query: str
    status: str
    answer: Optional[str] = ""
    results: List[ResearchResultItem]
    timestamp: Optional[str] = None
    total_results: int

@router.post("/search", response_model=ResearchResponse)
async def perform_research(
    req: ResearchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Executes a real-time technical search via Tavily Search API.
    Returns documentation citations, authoritative excerpts, and search answers.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")

    service = TavilyResearchService()
    res = await service.search(
        query=req.query,
        max_results=req.max_results or 4,
        search_depth=req.search_depth or "basic",
        include_domains=req.include_domains
    )

    if res.get("status") == "unconfigured":
        raise HTTPException(
            status_code=503,
            detail="Tavily Search API key is not configured in backend environment."
        )

    return res

@router.get("/status")
def get_tavily_status(current_user: User = Depends(get_current_user)):
    """Returns whether Tavily is configured and operational."""
    service = TavilyResearchService()
    return {
        "provider": "tavily",
        "configured": service.is_configured(),
        "endpoint": service.base_url,
        "features": ["ai_answer", "technical_documentation", "score_ranking", "citation_links"]
    }

