"""
Service for querying knowledge graph data
"""

import networkx as nx
from typing import List, Optional, Dict, Any

from app.models.graph_models import KnowledgeGraphData, GraphNode, GraphEdge
from app.models.schemas import GraphQueryRequest


class GraphQueryService:
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self._nodes_cache: Dict[str, GraphNode] = {}
        self._edges_cache: List[GraphEdge] = []
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """Initialize with French Protectorate of Tunisia article and its sections"""
        # Define source nodes (dots) - matching Wikipedia references
        sources = [
            GraphNode(
                id="source1",
                label="Perkins (1986)",
                content="Kenneth J. Perkins - Tunisia: Crossroads of the Islamic and European World",
                group=4,
                size=8,
                color="#DC143C",
                shape="dot",
                draw_order=8,
            ),
            GraphNode(
                id="source2",
                label="Wesseling (1996)",
                content="Henk Wesseling - Divide and Rule: The Partition of Africa, 1880-1914",
                group=4,
                size=8,
                color="#DC143C",
                shape="dot",
                draw_order=9,
            ),
            GraphNode(
                id="source3",
                label="Ling (1960)",
                content="Dwight L. Ling - The French Invasion of Tunisia, 1881",
                group=4,
                size=8,
                color="#DC143C",
                shape="dot",
                draw_order=10,
            ),
            GraphNode(
                id="source4",
                label="Aldrich (1996)",
                content="Robert Aldrich - Greater France: A History of French Expansion",
                group=4,
                size=8,
                color="#DC143C",
                shape="dot",
                draw_order=11,
            ),
            GraphNode(
                id="source5",
                label="Ganiage (1985)",
                content="Jean Ganiage - The Cambridge History of Africa",
                group=4,
                size=8,
                color="#DC143C",
                shape="dot",
                draw_order=12,
            ),
            GraphNode(
                id="source6",
                label="US Dept of State (1949)",
                content="Territories Within the Area of Responsibility - Office of Near Eastern and African Affairs",
                group=4,
                size=8,
                color="#DC143C",
                shape="dot",
                draw_order=13,
            ),
            GraphNode(
                id="source7",
                label="Wade (1927)",
                content="Herbert Treadwell Wade - The New International Year Book: Tunis under French foreign office",
                group=4,
                size=8,
                color="#DC143C",
                shape="dot",
                draw_order=14,
            ),
            GraphNode(
                id="source8",
                label="UN Territories (1950)",
                content="Non-self-governing Territories - United Nations General Assembly Committee",
                group=4,
                size=8,
                color="#DC143C",
                shape="dot",
                draw_order=15,
            ),
            GraphNode(
                id="source9",
                label="Holt & Chilton (1918)",
                content="Lucius Hudson Holt & Alexander Wheeler Chilton - A History of Europe",
                group=4,
                size=8,
                color="#DC143C",
                shape="dot",
                draw_order=16,
            ),
            GraphNode(
                id="source10",
                label="Balch (1909)",
                content="Thomas William Balch - French Colonization in North Africa",
                group=4,
                size=8,
                color="#DC143C",
                shape="dot",
                draw_order=17,
            ),
            GraphNode(
                id="source11",
                label="Commercial Treaties (1931)",
                content="Handbook of Commercial Treaties with Foreign Powers - His Majesty's Stationery Office",
                group=4,
                size=8,
                color="#DC143C",
                shape="dot",
                draw_order=18,
            ),
            GraphNode(
                id="source12",
                label="Arfaoui Khémais",
                content="Arfaoui Khémais - Les élections politiques en Tunisie de 1881 à 1956, pp.45-51",
                group=5,
                size=8,
                color="#28A745",
                shape="dot",
                draw_order=19,
            ),
        ]

        # Main article node
        article_node = GraphNode(
            id="article1",
            label="French protectorate of Tunisia",
            content="The French protectorate of Tunisia was established by the Treaty of Bardo in 1881",
            group=1,
            size=15,
            color={"background": "#D4B896", "border": "#8B0000"},
            shape="box",
            borderWidth=3,
            draw_order=1,
        )

        # Section nodes within the French Protectorate of Tunisia article
        section_nodes = [
            GraphNode(
                id="section1",
                label="Context",
                content="Background of Tunisia before the protectorate and the Congress of Berlin",
                group=1,
                size=12,
                color={"background": "#D4B896", "border": "#B22222"},
                shape="box",
                borderWidth=3,
                draw_order=2,
            ),
            GraphNode(
                id="section2",
                label="Conquest",
                content="French military campaigns and the Treaty of Bardo in 1881",
                group=1,
                size=11,
                color={"background": "#D4B896", "border": "#CD5C5C"},
                shape="box",
                borderWidth=3,
                draw_order=3,
            ),
            GraphNode(
                id="section3",
                label="Occupation",
                content="French troops invasion and establishment of control over Tunisia",
                group=1,
                size=10,
                color={"background": "#D4B896", "border": "#DC143C"},
                shape="box",
                borderWidth=3,
                draw_order=4,
            ),
            GraphNode(
                id="section4",
                label="Organisation and administration",
                content="French administrative structure, local government, and judicial system under the protectorate",
                group=1,
                size=10,
                color={"background": "#D4B896", "border": "#E9967A"},
                shape="box",
                borderWidth=3,
                draw_order=5,
            ),
            GraphNode(
                id="section5",
                label="World War II",
                content="Tunisia during WWII, Vichy government, and deposing of Moncef Bey",
                group=1,
                size=9,
                color={"background": "#D4B896", "border": "#F08080"},
                shape="box",
                borderWidth=3,
                draw_order=6,
            ),
            GraphNode(
                id="section6",
                label="Independence",
                content="Nationalist movement, Habib Bourguiba, and independence in 1956",
                group=1,
                size=9,
                color={"background": "#D4B896", "border": "#FF6347"},
                shape="box",
                borderWidth=3,
                draw_order=7,
            ),
        ]

        all_nodes = sources + [article_node] + section_nodes

        for node in all_nodes:
            self._nodes_cache[node.id] = node
            self.graph.add_node(node.id, **node.model_dump())

        # Define connections between article, sections, and sources
        sample_edges = [
            # Sources pointing to the main article and sections
            GraphEdge(
                source="source1",
                target="article1",
                similarity=0.95,
                width=1,
                value=0.95,
                title="Source: 0.95",
                draw_order=8,
                dashes=True,
                arrows="to",
            ),
            GraphEdge(
                source="source2",
                target="section1",
                similarity=0.9,
                width=1,
                value=0.9,
                title="Source: 0.90",
                draw_order=9,
                dashes=True,
                arrows="to",
            ),
            GraphEdge(
                source="source3",
                target="section2",
                similarity=0.92,
                width=1,
                value=0.92,
                title="Source: 0.92",
                draw_order=10,
                dashes=True,
                arrows="to",
            ),
            GraphEdge(
                source="source4",
                target="section6",
                similarity=0.88,
                width=1,
                value=0.88,
                title="Source: 0.88",
                draw_order=11,
                dashes=True,
                arrows="to",
            ),
            GraphEdge(
                source="source5",
                target="section3",
                similarity=0.87,
                width=1,
                value=0.87,
                title="Source: 0.87",
                draw_order=12,
                dashes=True,
                arrows="to",
            ),
            GraphEdge(
                source="source6",
                target="article1",
                similarity=0.91,
                width=1,
                value=0.91,
                title="Source: 0.91",
                draw_order=13,
                dashes=True,
                arrows="to",
            ),
            GraphEdge(
                source="source7",
                target="article1",
                similarity=0.89,
                width=1,
                value=0.89,
                title="Source: 0.89",
                draw_order=14,
                dashes=True,
                arrows="to",
            ),
            GraphEdge(
                source="source8",
                target="article1",
                similarity=0.90,
                width=1,
                value=0.90,
                title="Source: 0.90",
                draw_order=15,
                dashes=True,
                arrows="to",
            ),
            GraphEdge(
                source="source9",
                target="section1",
                similarity=0.86,
                width=1,
                value=0.86,
                title="Source: 0.86",
                draw_order=16,
                dashes=True,
                arrows="to",
            ),
            GraphEdge(
                source="source10",
                target="section4",
                similarity=0.84,
                width=1,
                value=0.84,
                title="Source: 0.84",
                draw_order=17,
                dashes=True,
                arrows="to",
            ),
            GraphEdge(
                source="source11",
                target="article1",
                similarity=0.85,
                width=1,
                value=0.85,
                title="Source: 0.85",
                draw_order=18,
                dashes=True,
                arrows="to",
            ),
            GraphEdge(
                source="source12",
                target="section4",
                similarity=0.93,
                width=1,
                value=0.93,
                title="Source: 0.93",
                draw_order=19,
                dashes=True,
                arrows="to",
            ),
            # Article to sections
            GraphEdge(
                source="article1",
                target="section1",
                similarity=0.95,
                width=2,
                value=0.95,
                title="Contains section: 0.95",
                draw_order=1,
            ),
            GraphEdge(
                source="article1",
                target="section2",
                similarity=0.9,
                width=2,
                value=0.9,
                title="Contains section: 0.90",
                draw_order=2,
            ),
            GraphEdge(
                source="article1",
                target="section3",
                similarity=0.88,
                width=2,
                value=0.88,
                title="Contains section: 0.88",
                draw_order=3,
            ),
            GraphEdge(
                source="article1",
                target="section4",
                similarity=0.85,
                width=2,
                value=0.85,
                title="Contains section: 0.85",
                draw_order=4,
            ),
            GraphEdge(
                source="article1",
                target="section5",
                similarity=0.82,
                width=2,
                value=0.82,
                title="Contains section: 0.82",
                draw_order=5,
            ),
            GraphEdge(
                source="article1",
                target="section6",
                similarity=0.8,
                width=2,
                value=0.8,
                title="Contains section: 0.80",
                draw_order=6,
            ),
            # Related sections - chronological flow
            GraphEdge(
                source="section1",
                target="section2",
                similarity=0.85,
                width=1,
                value=0.85,
                title="Led to: 0.85",
                draw_order=13,
            ),
            GraphEdge(
                source="section2",
                target="section3",
                similarity=0.8,
                width=1,
                value=0.8,
                title="Established: 0.80",
                draw_order=14,
            ),
            GraphEdge(
                source="section3",
                target="section4",
                similarity=0.75,
                width=1,
                value=0.75,
                title="Organized: 0.75",
                draw_order=15,
            ),
            GraphEdge(
                source="section5",
                target="section6",
                similarity=0.9,
                width=1,
                value=0.9,
                title="Resulted in: 0.90",
                draw_order=16,
            ),
        ]

        for edge in sample_edges:
            self._edges_cache.append(edge)
            self.graph.add_edge(edge.source, edge.target, **edge.model_dump())

    async def query(self, request: GraphQueryRequest) -> KnowledgeGraphData:
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

        return KnowledgeGraphData(
            nodes=nodes,
            edges=edges,
            metadata={
                "node_count": len(nodes),
                "edge_count": len(edges),
                "query_type": "filtered" if request.node_ids else "full",
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
