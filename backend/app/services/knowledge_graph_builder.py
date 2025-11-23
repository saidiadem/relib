"""
Service for building knowledge graphs from article data using OpenAI embeddings
"""

import networkx as nx
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
import logging

from app.models.graph_models import KnowledgeGraphData, GraphNode, GraphEdge
from app.services.wikipedia_service import WikipediaService
from app.core.config import settings

logger = logging.getLogger(__name__)


class KnowledgeGraphBuilder:
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize Knowledge Graph Builder with OpenAI embeddings
        
        Args:
            openai_api_key: OpenAI API key (uses settings if not provided)
        """
        self.graph = nx.MultiDiGraph()
        self.node_counter = 0
        self.wiki_service = WikipediaService()
        
        # Initialize OpenAI client
        api_key = openai_api_key or settings.OPENAI_API_KEY
        if not api_key:
            logger.warning("OpenAI API key not provided. Embeddings will not work.")
        
        self.openai_client = OpenAI(api_key=api_key) if api_key else None
        self.embedding_model = settings.OPENAI_EMBEDDING_MODEL
        self.similarity_threshold = settings.SIMILARITY_THRESHOLD

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get OpenAI embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if failed
        """
        if not self.openai_client:
            logger.error("OpenAI client not initialized")
            return None
        
        try:
            # Truncate text if too long (OpenAI has token limits)
            max_chars = 5000
            if len(text) > max_chars:
                text = text[:max_chars]
            
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            return response.data[0].embedding
        
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return None

    def calculate_similarity_matrix(self, embeddings: List[List[float]]) -> np.ndarray:
        """
        Calculate cosine similarity matrix between embeddings
        
        Args:
            embeddings: List of embedding vectors
            
        Returns:
            Similarity matrix (n x n numpy array)
        """
        embeddings_array = np.array(embeddings)
        return cosine_similarity(embeddings_array)

    async def build_from_article(
        self, 
        article_title: str, 
        languages: Optional[List[str]] = None,
        include_summary: bool = True
    ) -> KnowledgeGraphData:
        """
        Build knowledge graph from Wikipedia article using embeddings and cosine similarity
        
        Args:
            article_title: Wikipedia article title
            languages: List of language codes for cross-language analysis
            include_summary: Whether to include article summary as a node
            
        Returns:
            KnowledgeGraphData with nodes (sections) and edges (similarity connections)
        """
        if languages is None:
            languages = ['en']
        
        logger.info(f"Building graph for article: {article_title}")
        
        # Fetch article data
        article_data = await self.wiki_service.fetch_article(article_title, languages)
        
        # Build graph from sections
        graph_data = await self.build_graph_from_sections(
            article_data, 
            include_summary=include_summary
        )
        
        return graph_data

    async def build_graph_from_sections(
        self, 
        article_data: Dict,
        include_summary: bool = True,
        min_text_length: int = 50
    ) -> KnowledgeGraphData:
        """
        Build graph with sections as nodes and similarity-based edges
        
        Args:
            article_data: Article data from WikipediaService
            include_summary: Whether to include article summary as a node
            min_text_length: Minimum text length for a section to be included
            
        Returns:
            KnowledgeGraphData
        """
        nodes = []
        sections_data = []
        
        # Add article summary as root node if requested
        if include_summary and article_data.get('summary'):
            summary_text = article_data['summary']
            if len(summary_text) >= min_text_length:
                node_id = self._create_node_id('summary')
                nodes.append({
                    'id': node_id,
                    'label': 'Summary',
                    'content': summary_text[:200] + '...' if len(summary_text) > 200 else summary_text,
                    'full_text': summary_text,
                    'level': 0,
                    'type': 'summary'
                })
                sections_data.append({
                    'id': node_id,
                    'text': summary_text,
                    'title': 'Summary'
                })
        
        # Add sections as nodes
        for section in article_data.get('sections', []):
            section_text = section.get('text', '')
            
            # Skip sections with too little text
            if len(section_text.strip()) < min_text_length:
                continue
            
            node_id = self._create_node_id('section')
            level = section.get('level', 1)
            title = section.get('title', 'Untitled')
            
            nodes.append({
                'id': node_id,
                'label': title,
                'content': section_text[:200] + '...' if len(section_text) > 200 else section_text,
                'full_text': section_text,
                'level': level,
                'type': 'section'
            })
            
            sections_data.append({
                'id': node_id,
                'text': section_text,
                'title': title
            })
        
        logger.info(f"Created {len(nodes)} nodes from sections")
        
        # Get embeddings for all sections
        embeddings = []
        valid_sections = []
        
        for section in sections_data:
            embedding = self.get_embedding(section['text'])
            if embedding:
                embeddings.append(embedding)
                valid_sections.append(section)
        
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # Calculate similarity matrix
        if len(embeddings) > 1:
            similarity_matrix = self.calculate_similarity_matrix(embeddings)
            logger.info(f"Calculated similarity matrix: {similarity_matrix.shape}")
        else:
            similarity_matrix = np.array([[1.0]]) if embeddings else np.array([])
        
        # Create edges based on similarity
        edges = []
        
        for i in range(len(valid_sections)):
            for j in range(i + 1, len(valid_sections)):
                similarity = similarity_matrix[i][j]
                
                # Only create edge if similarity is above threshold
                if similarity >= self.similarity_threshold:
                    source_id = valid_sections[i]['id']
                    target_id = valid_sections[j]['id']
                    
                    edges.append({
                        'source': source_id,
                        'target': target_id,
                        'similarity': float(similarity),
                        'source_title': valid_sections[i]['title'],
                        'target_title': valid_sections[j]['title']
                    })
        
        logger.info(f"Created {len(edges)} edges (threshold: {self.similarity_threshold})")
        
        # Convert to graph models
        graph_nodes = []
        for node_data in nodes:
            # Find if this node has embeddings
            node_has_embedding = any(s['id'] == node_data['id'] for s in valid_sections)
            
            # Calculate node size based on text length and connections
            text_length = len(node_data.get('full_text', ''))
            base_size = 10 + (text_length / 1000) * 5  # Larger for longer sections
            
            # Count connections
            connection_count = sum(
                1 for e in edges 
                if e['source'] == node_data['id'] or e['target'] == node_data['id']
            )
            size = base_size + connection_count * 2
            
            # Assign color based on level
            color = self._get_color_for_level(node_data.get('level', 1))
            
            graph_nodes.append(GraphNode(
                id=node_data['id'],
                label=node_data['label'],
                content=node_data['content'],
                group=node_data.get('level', 1),
                size=min(size, 50),  # Cap at 50
                color=color,
                shape='box',
                metadata={
                    'level': node_data.get('level', 1),
                    'type': node_data.get('type', 'section'),
                    'has_embedding': node_has_embedding,
                    'text_length': text_length
                }
            ))
        
        graph_edges = []
        for edge_data in edges:
            # Calculate edge width based on similarity
            width = edge_data['similarity'] * 5  # Scale for visibility
            
            graph_edges.append(GraphEdge(
                source=edge_data['source'],
                target=edge_data['target'],
                similarity=edge_data['similarity'],
                width=width,
                value=edge_data['similarity'],
                title=f"{edge_data['source_title']} ↔ {edge_data['target_title']}\nSimilarity: {edge_data['similarity']:.3f}",
                metadata={
                    'source_title': edge_data['source_title'],
                    'target_title': edge_data['target_title']
                }
            ))
        
        return KnowledgeGraphData(
            nodes=graph_nodes,
            edges=graph_edges,
            metadata={
                "node_count": len(graph_nodes),
                "edge_count": len(graph_edges),
                "article_title": article_data.get('title'),
                "languages": article_data.get('metadata', {}).get('available_languages', []),
                "similarity_threshold": self.similarity_threshold,
                "embedding_model": self.embedding_model,
                "avg_similarity": float(np.mean([e['similarity'] for e in edges])) if edges else 0.0,
                "max_similarity": float(np.max([e['similarity'] for e in edges])) if edges else 0.0,
                "min_similarity": float(np.min([e['similarity'] for e in edges])) if edges else 0.0
            }
        )

    def _create_node_id(self, node_type: str) -> str:
        """
        Create unique node ID
        
        Args:
            node_type: Type of node (summary, section, etc.)
            
        Returns:
            Unique node ID
        """
        node_id = f"{node_type}_{self.node_counter}"
        self.node_counter += 1
        return node_id

    def _get_color_for_level(self, level: int) -> str:
        """
        Get color based on section level
        
        Args:
            level: Section level (0 for summary, 1+ for sections)
            
        Returns:
            Hex color code
        """
        colors = {
            0: '#4285F4',  # Blue - Summary
            1: '#EA4335',  # Red - Top level sections
            2: '#FBBC04',  # Yellow - Subsections
            3: '#34A853',  # Green - Sub-subsections
            4: '#9C27B0',  # Purple - Deeper sections
        }
        
        return colors.get(level, '#757575')  # Gray for very deep sections
