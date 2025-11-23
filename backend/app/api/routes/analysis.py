"""
Analysis endpoints for Wikipedia article evaluation
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional

from app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    ArticleInfo
)
from app.services.wikipedia_service import WikipediaService
from app.services.analysis_orchestrator import AnalysisOrchestrator

router = APIRouter()

wikipedia_service = WikipediaService()
analysis_orchestrator = AnalysisOrchestrator()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_article(request: AnalysisRequest):
    """
    Analyze a Wikipedia article for colonial bias
    """
    try:
        # Fetch article data
        article_data = await wikipedia_service.fetch_article(
            title=request.article_title,
            languages=request.languages
        )
        
        # Run comprehensive analysis
        analysis_result = await analysis_orchestrator.analyze(article_data)
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/article-info/{title}", response_model=ArticleInfo)
async def get_article_info(title: str):
    """
    Get basic information about a Wikipedia article
    """
    try:
        info = await wikipedia_service.get_article_info(title)
        return info
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Article not found: {str(e)}")


@router.get("/available-languages/{title}")
async def get_available_languages(title: str):
    """
    Get list of available language versions for an article
    """
    try:
        languages = await wikipedia_service.get_available_languages(title)
        return {"languages": languages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
