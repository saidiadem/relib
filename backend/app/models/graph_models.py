"""
Graph-specific data models
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any


class GraphNode(BaseModel):
    """Node in the knowledge graph"""

    id: str
    label: str
    content: Optional[str] = None
    group: int = Field(default=1, description="Node group/category")
    size: float = Field(default=5, description="Node size based on importance")
    color: Optional[str] = None
    shape: str = Field(default="box")
    x: Optional[float] = None
    y: Optional[float] = None
    draw_order: Optional[int] = Field(
        default=None, description="Order in which to draw this node"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    """Edge in the knowledge graph"""

    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    similarity: float = Field(..., ge=0, le=1, description="Similarity score")
    width: Optional[float] = None
    title: Optional[str] = None
    value: Optional[float] = None
    dashes: Optional[bool] = Field(
        default=None, description="Whether edge should be dashed"
    )
    arrows: Optional[str] = Field(
        default=None, description="Arrow direction: 'to', 'from', or 'to,from'"
    )
    draw_order: Optional[int] = Field(
        default=None, description="Order in which to draw this edge"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeGraphData(BaseModel):
    """Complete knowledge graph data structure"""

    nodes: List[GraphNode]
    edges: List[GraphEdge]
    metadata: Dict[str, Any] = Field(default_factory=dict)
