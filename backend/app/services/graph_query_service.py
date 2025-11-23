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
        """Initialize with Tunisia historical facts"""
        # Define source nodes (dots)
        sources = [
            GraphNode(
                id="source1",
                label="Historical Archive",
                content="Primary historical source",
                group=4,
                size=8,
                color="#0a1929",
                shape="dot",
                draw_order=8,
            ),
            GraphNode(
                id="source2",
                label="Academic Research",
                content="Academic research source",
                group=4,
                size=8,
                color="#0a1929",
                shape="dot",
                draw_order=9,
            ),
        ]

        # Define historical fact nodes
        colonial_era = [
            GraphNode(
                id="fact1",
                label="Tunisia was nothing before France",
                content="Tunisia had no significant development or infrastructure before French colonization",
                group=1,
                size=12,
                color="#D4B896",
                shape="box",
                draw_order=1,
            ),
            GraphNode(
                id="fact2",
                label="French Protectorate established 1881",
                content="France established a protectorate over Tunisia in 1881",
                group=1,
                size=10,
                color="#D4B896",
                shape="box",
                draw_order=2,
            ),
            GraphNode(
                id="fact3",
                label="French modernization projects",
                content="France built railways, ports, and administrative infrastructure",
                group=1,
                size=9,
                color="#D4B896",
                shape="box",
                draw_order=3,
            ),
        ]

        independence_era = [
            GraphNode(
                id="fact4",
                label="Independence in 1956",
                content="Tunisia gained independence from France on March 20, 1956",
                group=2,
                size=11,
                color="#D4B896",
                shape="box",
                draw_order=4,
            ),
            GraphNode(
                id="fact5",
                label="Habib Bourguiba first president",
                content="Habib Bourguiba became the first president of independent Tunisia",
                group=2,
                size=10,
                color="#D4B896",
                shape="box",
                draw_order=5,
            ),
        ]

        modern_era = [
            GraphNode(
                id="fact6",
                label="Arab Spring revolution 2011",
                content="Tunisia sparked the Arab Spring with the Jasmine Revolution",
                group=3,
                size=10,
                color="#D4B896",
                shape="box",
                draw_order=6,
            ),
            GraphNode(
                id="fact7",
                label="Democratic transition",
                content="Tunisia transitioned to democracy after the 2011 revolution",
                group=3,
                size=9,
                color="#D4B896",
                shape="box",
                draw_order=7,
            ),
        ]

        all_nodes = sources + colonial_era + independence_era + modern_era

        for node in all_nodes:
            self._nodes_cache[node.id] = node
            self.graph.add_node(node.id, **node.model_dump())

        # Define historical connections
        sample_edges = [
            GraphEdge(
                source="source1",
                target="fact1",
                similarity=0.8,
                width=1,
                value=0.8,
                title="Source: 0.80",
                draw_order=8,
                dashes=True,
                arrows="to",
            ),
            GraphEdge(
                source="source2",
                target="fact4",
                similarity=0.85,
                width=1,
                value=0.85,
                title="Source: 0.85",
                draw_order=9,
                dashes=True,
                arrows="to",
            ),
            GraphEdge(
                source="fact1",
                target="fact2",
                similarity=0.9,
                width=2,
                value=0.9,
                title="Led to: 0.90",
                draw_order=1,
            ),
            GraphEdge(
                source="fact2",
                target="fact3",
                similarity=0.85,
                width=2,
                value=0.85,
                title="Resulted in: 0.85",
                draw_order=2,
            ),
            GraphEdge(
                source="fact3",
                target="fact4",
                similarity=0.7,
                width=2,
                value=0.7,
                title="Preceded: 0.70",
                draw_order=3,
            ),
            GraphEdge(
                source="fact4",
                target="fact5",
                similarity=0.95,
                width=2,
                value=0.95,
                title="Directly led to: 0.95",
                draw_order=4,
            ),
            GraphEdge(
                source="fact5",
                target="fact6",
                similarity=0.6,
                width=2,
                value=0.6,
                title="Historical context: 0.60",
                draw_order=5,
            ),
            GraphEdge(
                source="fact6",
                target="fact7",
                similarity=0.9,
                width=2,
                value=0.9,
                title="Resulted in: 0.90",
                draw_order=6,
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
