"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class AnalysisRequest(BaseModel):
    """Request for article analysis"""

    article_title: str = Field(..., description="Wikipedia article title")
    languages: List[str] = Field(default=["en"], description="Languages to analyze")
    include_graph: bool = Field(
        default=True, description="Include knowledge graph in response"
    )


class DimensionScore(BaseModel):
    """Score for a specific bias dimension"""

    dimension: str
    score: float = Field(..., ge=0, le=1, description="Score between 0 and 1")
    details: Dict[str, Any] = Field(default_factory=dict)
    flags: List[str] = Field(default_factory=list)


class ArticleInfo(BaseModel):
    """Basic article information"""

    title: str
    url: str
    language: str
    last_modified: Optional[datetime] = None
    word_count: Optional[int] = None
    summary: Optional[str] = None


class KnowledgeGraphSummary(BaseModel):
    """Summary of knowledge graph structure"""

    node_count: int
    edge_count: int
    clusters: int
    central_nodes: List[str] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    """Response for article analysis"""

    article_title: str
    analysis_timestamp: datetime
    overall_score: float = Field(..., ge=0, le=1)
    dimensions: Dict[str, DimensionScore]
    flags: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    knowledge_graph_summary: Dict[str, Any] = Field(default_factory=dict)


class GraphNode(BaseModel):
    """Node in the knowledge graph"""

    id: str
    label: str
    content: Optional[str] = None
    group: int = Field(default=1, description="Node group/category")
    size: float = Field(default=5, description="Node size based on importance")
    color: Optional[str] = None
    shape: str = Field(default="dot")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    """Edge in the knowledge graph"""

    from_node: str = Field(..., alias="from")
    to_node: str = Field(..., alias="to")
    similarity: float = Field(..., ge=0, le=1, description="Similarity score")
    width: Optional[float] = None
    title: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        populate_by_name = True


class GraphData(BaseModel):
    """Complete graph data structure"""

    nodes: List[GraphNode]
    edges: List[GraphEdge]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphQueryRequest(BaseModel):
    """Request for querying graph data"""

    article_title: Optional[str] = None
    topic: Optional[str] = None
    node_ids: Optional[List[str]] = None
    include_neighbors: bool = Field(
        default=False, description="Include neighboring nodes"
    )
    max_depth: int = Field(
        default=1, ge=1, le=3, description="Maximum depth for neighbor traversal"
    )


class GraphQueryResponse(BaseModel):
    """Response for graph query"""

    graph: GraphData
    query_metadata: Dict[str, Any] = Field(default_factory=dict)
