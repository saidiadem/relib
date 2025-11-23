"""
Graph endpoints for knowledge graph queries
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.models.schemas import GraphQueryRequest, GraphQueryResponse
from app.models.graph_models import KnowledgeGraphData, GraphNode, GraphEdge
from app.services.knowledge_graph_builder import KnowledgeGraphBuilder
from app.services.graph_query_service import GraphQueryService

router = APIRouter()

graph_builder = KnowledgeGraphBuilder()
graph_query_service = GraphQueryService()


@router.post("/query", response_model=KnowledgeGraphData)
async def query_graph(request: GraphQueryRequest):
    """
    Query knowledge graph with various filters
    """
    try:
        result = await graph_query_service.query(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nodes", response_model=List[GraphNode])
async def get_nodes(
    topic: Optional[str] = None,
    group: Optional[int] = None,
    limit: int = Query(default=100, le=1000),
):
    """
    Get nodes with optional filtering
    """
    try:
        nodes = await graph_query_service.get_nodes(
            topic=topic, group=group, limit=limit
        )
        return nodes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nodes/{node_id}", response_model=GraphNode)
async def get_node(node_id: str):
    """
    Get a specific node by ID
    """
    try:
        node = await graph_query_service.get_node_by_id(node_id)
        if not node:
            raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
        return node
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nodes/{node_id}/neighbors", response_model=List[GraphNode])
async def get_node_neighbors(
    node_id: str, max_depth: int = Query(default=1, ge=1, le=3)
):
    """
    Get neighboring nodes for a specific node
    """
    try:
        neighbors = await graph_query_service.get_neighbors(node_id, max_depth)
        return neighbors
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/edges", response_model=List[GraphEdge])
async def get_edges(
    node_id: Optional[str] = None,
    min_similarity: float = Query(default=0.0, ge=0, le=1),
    limit: int = Query(default=100, le=1000),
):
    """
    Get edges with optional filtering
    """
    try:
        edges = await graph_query_service.get_edges(
            node_id=node_id, min_similarity=min_similarity, limit=limit
        )
        return edges
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/full", response_model=KnowledgeGraphData)
async def get_full_graph(topic: Optional[str] = None, include_metadata: bool = True):
    """
    Get complete graph data (nodes and edges)
    """
    try:
        graph = await graph_query_service.get_full_graph(
            topic=topic, include_metadata=include_metadata
        )
        return graph
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/build")
async def build_graph(article_title: str, languages: List[str] = Query(default=["en"])):
    """
    Build knowledge graph from Wikipedia article
    """
    try:
        # This would fetch article data and build graph
        # For now, return sample data
        result = await graph_builder.build_from_article(article_title, languages)
        return {
            "status": "success",
            "article": article_title,
            "node_count": len(result.nodes),
            "edge_count": len(result.edges),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
