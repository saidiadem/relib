"""
Service for building knowledge graphs from article data using local sentence-transformers
"""

import networkx as nx
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging
import json
import hashlib
from pathlib import Path
from datetime import datetime

from app.models.graph_models import KnowledgeGraphData, GraphNode, GraphEdge
from app.services.wikipedia_service import WikipediaService
from app.core.config import settings

logger = logging.getLogger(__name__)


class KnowledgeGraphBuilder:
    def __init__(self, model_name: Optional[str] = None, cache_dir: Optional[str] = None):
        """
        Initialize Knowledge Graph Builder with local sentence-transformers embeddings
        
        Args:
            model_name: Sentence transformer model name (uses settings if not provided)
            cache_dir: Directory for caching graphs (defaults to 'data/graph_cache')
        """
        self.graph = nx.MultiDiGraph()
        self.node_counter = 0
        self.wiki_service = WikipediaService()
        
        # Initialize sentence-transformers model
        self.embedding_model = model_name or settings.EMBEDDING_MODEL
        print(f"🔧 Loading embedding model: {self.embedding_model}")
        logger.info(f"Loading embedding model: {self.embedding_model}")
        
        try:
            self.model = SentenceTransformer(self.embedding_model, trust_remote_code=True)
            print(f"✅ Embedding model loaded successfully!")
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load embedding model: {e}")
            print(f"   This might be due to missing dependencies or download issues.")
            print(f"   The model will download on first use if not cached.")
            logger.error(f"Failed to load embedding model: {e}")
            import traceback
            traceback.print_exc()
            self.model = None
        
        self.similarity_threshold = settings.SIMILARITY_THRESHOLD
        
        # Setup cache directory
        self.cache_dir = Path(cache_dir) if cache_dir else Path('data/graph_cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get sentence-transformer embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if failed
        """
        if not self.model:
            logger.error("Embedding model not initialized")
            return None
        
        try:
            # Truncate text if too long
            max_chars = 8000
            if len(text) > max_chars:
                text = text[:max_chars]
            
            # Get embedding using sentence-transformers
            embedding = self.model.encode(text, convert_to_numpy=True)
            print(embedding[:8])
            
            return embedding.tolist()
        
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
        include_summary: bool = True,
        use_cache: bool = True
    ) -> KnowledgeGraphData:
        """
        Build knowledge graph from Wikipedia article using embeddings and cosine similarity
        
        Args:
            article_title: Wikipedia article title
            languages: List of language codes for cross-language analysis
            include_summary: Whether to include article summary as a node
            use_cache: Whether to use cached graph if available
            
        Returns:
            KnowledgeGraphData with nodes (sections) and edges (similarity connections)
        """
        if languages is None:
            languages = ['en']
        
        # Check cache first
        if use_cache:
            cached_graph = self.load_from_cache(article_title, languages, include_summary)
            if cached_graph:
                logger.info(f"Loaded graph from cache for: {article_title}")
                return cached_graph
        
        logger.info(f"Building graph for article: {article_title}")
        
        # Fetch article data
        article_data = await self.wiki_service.fetch_article(article_title, languages)
        
        # Build graph from sections
        graph_data = await self.build_graph_from_sections(
            article_data, 
            include_summary=include_summary
        )
        
        # Save to cache
        if use_cache:
            self.save_to_cache(article_title, languages, include_summary, graph_data)
        
        return graph_data

    async def build_graph_from_sections(
        self, 
        article_data: Dict,
        include_summary: bool = True,
        min_text_length: int = 50,
        include_references: bool = True
    ) -> KnowledgeGraphData:
        """
        Build graph with sections as nodes and similarity-based edges
        
        Args:
            article_data: Article data from WikipediaService
            include_summary: Whether to include article summary as a node
            min_text_length: Minimum text length for a section to be included
            include_references: Whether to include reference nodes
            
        Returns:
            KnowledgeGraphData
        """
        nodes = []
        sections_data = []
        source_nodes = []
        section_to_sources = {}  # Maps section_id to list of source_ids
        
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
                    'type': 'summary',
                    'draw_order': 1
                })
                sections_data.append({
                    'id': node_id,
                    'text': summary_text,
                    'title': 'Summary'
                })
        
        # Add sections as nodes
        draw_order = 2
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
                'type': 'section',
                'draw_order': draw_order
            })
            
            sections_data.append({
                'id': node_id,
                'text': section_text,
                'title': title
            })
            
            draw_order += 1
        
        # Add reference/source nodes if requested
        if include_references:
            references = article_data.get('references', [])
            source_draw_order = 1000  # Start from high number for sources
            
            # Map reference indices to source IDs
            ref_index_to_source_id = {}
            
            for idx, ref in enumerate(references):
                source_id = self._create_node_id('source')
                ref_index_to_source_id[idx] = source_id
                
                # Create label from reference data
                if ref.get('title'):
                    label = ref['title'][:50]  # Truncate long titles
                elif ref.get('authors') and len(ref['authors']) > 0:
                    label = ref['authors'][0]
                else:
                    label = f"Reference {idx + 1}"
                
                # Create content from reference metadata
                content_parts = []
                if ref.get('authors'):
                    content_parts.append(f"Authors: {', '.join(ref['authors'][:3])}")
                if ref.get('year'):
                    content_parts.append(f"Year: {ref['year']}")
                if ref.get('publisher'):
                    content_parts.append(f"Publisher: {ref['publisher']}")
                
                content = ' | '.join(content_parts) if content_parts else "Reference source"
                
                source_nodes.append({
                    'id': source_id,
                    'label': label,
                    'content': content,
                    'type': 'source',
                    'draw_order': source_draw_order,
                    'reference_data': ref,
                    'reference_index': idx
                })
                
                source_draw_order += 1
            
            # Parse citation markers from section text to map sources to sections
            import re
            citation_pattern = re.compile(r'\[(\d+)\]')
            
            for section in sections_data:
                section_text = section['text']
                section_id = section['id']
                
                # Find all citation markers like [1], [279], etc.
                citations = citation_pattern.findall(section_text)
                
                for citation in citations:
                    try:
                        ref_idx = int(citation) - 1  # Convert to 0-based index
                        
                        # Check if this reference index exists
                        if 0 <= ref_idx < len(references):
                            source_id = ref_index_to_source_id.get(ref_idx)
                            if source_id:
                                section_to_sources.setdefault(section_id, []).append(source_id)
                    except (ValueError, KeyError):
                        continue
        
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
        
        # Create edges from sources to sections
        source_edges = []
        edge_draw_order = 1000
        
        for section_id, source_ids in section_to_sources.items():
            if section_id:
                for source_id in source_ids:
                    source_edges.append({
                        'source': source_id,
                        'target': section_id,
                        'similarity': 0.8,  # Default similarity for source citations
                        'draw_order': edge_draw_order,
                        'is_source_edge': True
                    })
                    edge_draw_order += 1
        
        logger.info(f"Created {len(source_edges)} source-to-section edges")
        
        # Convert to graph models
        graph_nodes = []
        
        # Add section/topic nodes
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
            
            # Assign color based on level (topic nodes use beige color)
            color = '#D4B896'  # Beige for topic/section nodes
            
            graph_nodes.append(GraphNode(
                id=node_data['id'],
                label=node_data['label'],
                content=node_data['content'],
                group=node_data.get('level', 1),
                size=min(size, 50),  # Cap at 50
                color=color,
                shape='box',
                draw_order=node_data.get('draw_order', 1),
                metadata={
                    'level': node_data.get('level', 1),
                    'type': node_data.get('type', 'section'),
                    'has_embedding': node_has_embedding,
                    'text_length': text_length
                }
            ))
        
        # Add source nodes (dots, dark color)
        for source_data in source_nodes:
            graph_nodes.append(GraphNode(
                id=source_data['id'],
                label=source_data['label'],
                content=source_data['content'],
                group=4,  # Group 4 for sources
                size=8,
                color='#0a1929',  # Dark color for source nodes
                shape='dot',
                draw_order=source_data['draw_order'],
                metadata={
                    'type': 'source',
                    'reference_data': source_data.get('reference_data', {})
                }
            ))
        
        # Create section-to-section edges (solid lines)
        graph_edges = []
        edge_draw_order_topic = 1
        
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
                draw_order=edge_draw_order_topic,
                metadata={
                    'source_title': edge_data['source_title'],
                    'target_title': edge_data['target_title'],
                    'edge_type': 'topic_similarity'
                }
            ))
            edge_draw_order_topic += 1
        
        # Create source-to-section edges (dashed lines with arrows)
        for edge_data in source_edges:
            graph_edges.append(GraphEdge(
                source=edge_data['source'],
                target=edge_data['target'],
                similarity=edge_data['similarity'],
                width=1,  # Thinner for source edges
                value=edge_data['similarity'],
                title=f"Source: {edge_data['similarity']:.2f}",
                dashes=True,  # Dashed line for source citations
                arrows='to',  # Arrow pointing to the section
                draw_order=edge_data['draw_order'],
                metadata={
                    'edge_type': 'source_citation'
                }
            ))
        
        return KnowledgeGraphData(
            nodes=graph_nodes,
            edges=graph_edges,
            metadata={
                "node_count": len(graph_nodes),
                "edge_count": len(graph_edges),
                "section_node_count": len(nodes),
                "source_node_count": len(source_nodes),
                "topic_edge_count": len(edges),
                "source_edge_count": len(source_edges),
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

    def _generate_cache_key(self, article_title: str, languages: List[str], include_summary: bool) -> str:
        """
        Generate unique cache key for article
        
        Args:
            article_title: Article title
            languages: Language codes
            include_summary: Whether summary is included
            
        Returns:
            Cache key string
        """
        key_data = f"{article_title}|{'|'.join(sorted(languages))}|{include_summary}|{self.similarity_threshold}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """
        Get cache file path for given key
        
        Args:
            cache_key: Cache key
            
        Returns:
            Path to cache file
        """
        return self.cache_dir / f"{cache_key}.json"

    def save_to_cache(self, article_title: str, languages: List[str], include_summary: bool, graph_data: KnowledgeGraphData) -> bool:
        """
        Save graph data to cache
        
        Args:
            article_title: Article title
            languages: Language codes
            include_summary: Whether summary is included
            graph_data: Graph data to cache
            
        Returns:
            True if saved successfully
        """
        try:
            cache_key = self._generate_cache_key(article_title, languages, include_summary)
            cache_path = self._get_cache_path(cache_key)
            
            # Convert to dict for JSON serialization
            cache_data = {
                'article_title': article_title,
                'languages': languages,
                'include_summary': include_summary,
                'cached_at': datetime.now().isoformat(),
                'graph': graph_data.model_dump()
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved graph to cache: {cache_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")
            return False

    def load_from_cache(self, article_title: str, languages: List[str], include_summary: bool) -> Optional[KnowledgeGraphData]:
        """
        Load graph data from cache
        
        Args:
            article_title: Article title
            languages: Language codes
            include_summary: Whether summary is included
            
        Returns:
            Cached graph data or None if not found
        """
        try:
            cache_key = self._generate_cache_key(article_title, languages, include_summary)
            cache_path = self._get_cache_path(cache_key)
            
            if not cache_path.exists():
                return None
            
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Deserialize graph data
            graph_data = KnowledgeGraphData(**cache_data['graph'])
            
            logger.info(f"Loaded graph from cache (cached at: {cache_data['cached_at']})")
            return graph_data
            
        except Exception as e:
            logger.error(f"Error loading from cache: {e}")
            return None

    def clear_cache(self, article_title: Optional[str] = None, languages: Optional[List[str]] = None) -> int:
        """
        Clear cached graphs
        
        Args:
            article_title: If provided, only clear cache for this article
            languages: If provided with article_title, clear specific language versions
            
        Returns:
            Number of cache files deleted
        """
        try:
            count = 0
            
            if article_title:
                # Clear specific article cache
                cache_key = self._generate_cache_key(article_title, languages or ['en'], True)
                cache_path = self._get_cache_path(cache_key)
                if cache_path.exists():
                    cache_path.unlink()
                    count = 1
            else:
                # Clear all cache
                for cache_file in self.cache_dir.glob('*.json'):
                    cache_file.unlink()
                    count += 1
            
            logger.info(f"Cleared {count} cache file(s)")
            return count
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return 0
