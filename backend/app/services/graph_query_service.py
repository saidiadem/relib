"""
Service for querying knowledge graph data
"""

import networkx as nx
from typing import List, Optional, Dict, Any

from app.models.graph_models import KnowledgeGraphData, GraphNode, GraphEdge
from app.models.schemas import GraphQueryRequest, GraphQueryResponse


class GraphQueryService:
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self._nodes_cache: Dict[str, GraphNode] = {}
        self._edges_cache: List[GraphEdge] = []
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """Initialize with sample vaccine sentiment data"""
        # Define sample nodes
        provax_nodes = [
            GraphNode(
                id="provax1",
                label="Vaccines save lives",
                content="Vaccines have been scientifically proven to save millions of lives worldwide",
                group=1,
                size=10,
                color="#34A853",
                shape="dot",
            ),
            GraphNode(
                id="provax2",
                label="Herd immunity protects everyone",
                content="High vaccination rates create herd immunity that protects vulnerable populations",
                group=1,
                size=8,
                color="#34A853",
                shape="dot",
            ),
            GraphNode(
                id="provax3",
                label="Vaccines undergo rigorous testing",
                content="All vaccines undergo extensive clinical trials to ensure safety and efficacy",
                group=1,
                size=9,
                color="#34A853",
                shape="dot",
            ),
        ]

        antivax_nodes = [
            GraphNode(
                id="antivax1",
                label="Vaccines contain toxins",
                content="Vaccines contain dangerous chemicals and toxins that harm the body",
                group=2,
                size=7,
                color="#EA4335",
                shape="dot",
            ),
            GraphNode(
                id="antivax2",
                label="Natural immunity is better",
                content="Natural immunity from getting sick is superior to vaccine-induced immunity",
                group=2,
                size=6,
                color="#EA4335",
                shape="dot",
            ),
        ]

        hesitancy_nodes = [
            GraphNode(
                id="hesitancy1",
                label="Need more research",
                content="We need more long-term studies on vaccine effects",
                group=3,
                size=8,
                color="#FBBC05",
                shape="dot",
            ),
            GraphNode(
                id="hesitancy2",
                label="Individual risk assessment",
                content="People should assess their personal risk before vaccination",
                group=3,
                size=7,
                color="#FBBC05",
                shape="dot",
            ),
        ]

        all_nodes = provax_nodes + antivax_nodes + hesitancy_nodes

        for node in all_nodes:
            self._nodes_cache[node.id] = node
            self.graph.add_node(node.id, **node.model_dump())

        # Define sample edges
        sample_edges = [
            GraphEdge(
                source="provax1",
                target="provax2",
                similarity=0.8,
                width=2.4,
                value=0.8,
                title="Similarity: 0.80",
            ),
            GraphEdge(
                source="provax1",
                target="provax3",
                similarity=0.7,
                width=2.1,
                value=0.7,
                title="Similarity: 0.70",
            ),
            GraphEdge(
                source="antivax1",
                target="antivax2",
                similarity=0.5,
                width=1.5,
                value=0.5,
                title="Similarity: 0.50",
            ),
            GraphEdge(
                source="hesitancy1",
                target="provax3",
                similarity=0.42,
                width=1.26,
                value=0.42,
                title="Similarity: 0.42",
            ),
            GraphEdge(
                source="hesitancy1",
                target="antivax2",
                similarity=0.48,
                width=1.44,
                value=0.48,
                title="Similarity: 0.48",
            ),
            GraphEdge(
                source="hesitancy2",
                target="antivax2",
                similarity=0.48,
                width=1.44,
                value=0.48,
                title="Similarity: 0.48",
            ),
        ]

        for edge in sample_edges:
            self._edges_cache.append(edge)
            self.graph.add_edge(edge.source, edge.target, **edge.model_dump())

    async def query(self, request: GraphQueryRequest) -> GraphQueryResponse:
        """Execute a graph query"""
        nodes = []
        edges = []

        if request.node_ids:
            # Filter by specific node IDs
            for node_id in request.node_ids:
                if node_id in self._nodes_cache:
                    nodes.append(self._nodes_cache[node_id])

            if request.include_neighbors:
                # Add neighbors
                for node_id in request.node_ids:
                    neighbors = await self.get_neighbors(node_id, request.max_depth)
                    nodes.extend(neighbors)

            # Get relevant edges
            node_id_set = {n.id for n in nodes}
            edges = [
                e
                for e in self._edges_cache
                if e.source in node_id_set and e.target in node_id_set
            ]
        else:
            # Return all nodes and edges
            nodes = list(self._nodes_cache.values())
            edges = self._edges_cache

        # Remove duplicates
        unique_nodes = {n.id: n for n in nodes}
        nodes = list(unique_nodes.values())

        graph_data = KnowledgeGraphData(
            nodes=nodes,
            edges=edges,
            metadata={
                "node_count": len(nodes),
                "edge_count": len(edges),
                "query_type": "filtered" if request.node_ids else "full",
            },
        )

        return GraphQueryResponse(
            graph=graph_data,
            query_metadata={
                "requested_nodes": request.node_ids or [],
                "include_neighbors": request.include_neighbors,
                "max_depth": request.max_depth,
            },
        )

    async def get_nodes(
        self, topic: Optional[str] = None, group: Optional[int] = None, limit: int = 100
    ) -> List[GraphNode]:
        """Get filtered list of nodes"""
        nodes = list(self._nodes_cache.values())

        if group is not None:
            nodes = [n for n in nodes if n.group == group]

        if topic:
            nodes = [
                n
                for n in nodes
                if topic.lower() in n.label.lower()
                or (n.content and topic.lower() in n.content.lower())
            ]

        return nodes[:limit]

    async def get_node_by_id(self, node_id: str) -> Optional[GraphNode]:
        """Get a specific node by ID"""
        return self._nodes_cache.get(node_id)

    async def get_neighbors(self, node_id: str, max_depth: int = 1) -> List[GraphNode]:
        """Get neighboring nodes up to max_depth"""
        if node_id not in self.graph:
            return []

        neighbors_ids = set()
        current_level = {node_id}

        for _ in range(max_depth):
            next_level = set()
            for node in current_level:
                # Get successors and predecessors
                next_level.update(self.graph.successors(node))
                next_level.update(self.graph.predecessors(node))

            neighbors_ids.update(next_level)
            current_level = next_level

        # Remove the original node
        neighbors_ids.discard(node_id)

        return [
            self._nodes_cache[nid] for nid in neighbors_ids if nid in self._nodes_cache
        ]

    async def get_edges(
        self,
        node_id: Optional[str] = None,
        min_similarity: float = 0.0,
        limit: int = 100,
    ) -> List[GraphEdge]:
        """Get filtered list of edges"""
        edges = self._edges_cache

        if node_id:
            edges = [e for e in edges if e.source == node_id or e.target == node_id]

        if min_similarity > 0:
            edges = [e for e in edges if e.similarity >= min_similarity]

        return edges[:limit]

    async def get_full_graph(
        self, topic: Optional[str] = None, include_metadata: bool = True
    ) -> KnowledgeGraphData:
        """Get complete graph"""
        nodes = await self.get_nodes(topic=topic, limit=1000)

        if topic:
            # Filter edges to only include nodes in result
            node_ids = {n.id for n in nodes}
            edges = [
                e
                for e in self._edges_cache
                if e.source in node_ids and e.target in node_ids
            ]
        else:
            edges = self._edges_cache

        metadata = {}
        if include_metadata:
            metadata = {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "groups": list({n.group for n in nodes}),
                "avg_similarity": sum(e.similarity for e in edges) / len(edges)
                if edges
                else 0,
            }

        return KnowledgeGraphData(nodes=nodes, edges=edges, metadata=metadata)
