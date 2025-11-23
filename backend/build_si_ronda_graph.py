"""
Build knowledge graph for Si Ronda Wikipedia article
"""
import asyncio
import os
from dotenv import load_dotenv

from app.services.knowledge_graph_builder import KnowledgeGraphBuilder

# Load environment variables
load_dotenv()


async def main():
    """
    Build knowledge graph for Si Ronda article
    """
    print("=" * 70)
    print("Building Knowledge Graph: Si Ronda")
    print("=" * 70)
    print()
    print("📦 Using local embedding model: Alibaba-NLP/gte-multilingual-base")
    print("🌍 This model supports multilingual text!")
    print()
    
    # Initialize graph builder with cache (no API key needed)
    builder = KnowledgeGraphBuilder(cache_dir='data/graph_cache')
    
    # Article title from Wikipedia URL
    article_title = "Si Ronda"
    
    print(f"📄 Article: {article_title}")
    print(f"🌐 URL: https://en.wikipedia.org/wiki/Si_Ronda")
    print()
    
    # Build graph with caching enabled
    try:
        print("🔨 Building graph (checking cache first)...")
        graph_data = await builder.build_from_article(
            article_title=article_title,
            languages=['en'],
            include_summary=True,
            use_cache=True
        )
        
        print("✅ Graph built successfully!")
        print()
        
        # Display statistics
        print("📊 Graph Statistics:")
        print(f"   Total Nodes: {graph_data.metadata['node_count']}")
        print(f"   - Section/Topic Nodes: {graph_data.metadata['section_node_count']}")
        print(f"   - Source/Reference Nodes: {graph_data.metadata['source_node_count']}")
        print()
        print(f"   Total Edges: {graph_data.metadata['edge_count']}")
        print(f"   - Topic Similarity Edges: {graph_data.metadata['topic_edge_count']}")
        print(f"   - Source Citation Edges: {graph_data.metadata['source_edge_count']}")
        print()
        print(f"   Similarity Threshold: {graph_data.metadata['similarity_threshold']}")
        print(f"   Embedding Model: {graph_data.metadata['embedding_model']}")
        print()
        
        # Similarity metrics
        if graph_data.metadata['topic_edge_count'] > 0:
            print(f"🔗 Topic Similarity Metrics:")
            print(f"   Average: {graph_data.metadata['avg_similarity']:.3f}")
            print(f"   Max: {graph_data.metadata['max_similarity']:.3f}")
            print(f"   Min: {graph_data.metadata['min_similarity']:.3f}")
            print()
        
        # Display section nodes
        print(f"📝 Section/Topic Nodes (beige boxes):")
        section_nodes = [n for n in graph_data.nodes if n.metadata.get('type') in ['summary', 'section']]
        for i, node in enumerate(section_nodes[:8]):
            print(f"   {i+1}. {node.label}")
            if node.content:
                print(f"   Content preview: {node.content[:80]}...")
            
            # Count citations for this section
            citation_count = sum(1 for e in graph_data.edges 
                               if e.target == node.id and e.metadata.get('edge_type') == 'source_citation')
            if citation_count > 0:
                print(f"      Citations: {citation_count} references")
        
        if len(section_nodes) > 8:
            print(f"   ... and {len(section_nodes) - 8} more sections")
        
        print()
        
        # Display source nodes
        print(f"📚 Source/Reference Nodes (dark dots):")
        source_nodes = [n for n in graph_data.nodes if n.metadata.get('type') == 'source']
        for i, node in enumerate(source_nodes[:8]):
            print(f"   {i+1}. {node.label}")
            if node.content:
                print(f"      {node.content}")
        
        if len(source_nodes) > 8:
            print(f"   ... and {len(source_nodes) - 8} more sources")
        
        print()
        
        # Display high-similarity connections
        if graph_data.metadata['topic_edge_count'] > 0:
            print(f"🔗 Top Section Similarities (solid edges):")
            topic_edges = [e for e in graph_data.edges if e.metadata.get('edge_type') == 'topic_similarity']
            sorted_edges = sorted(topic_edges, key=lambda e: e.similarity, reverse=True)
            
            for i, edge in enumerate(sorted_edges[:5]):
                source_title = edge.metadata.get('source_title', 'Unknown')
                target_title = edge.metadata.get('target_title', 'Unknown')
                print(f"   {i+1}. {source_title} ↔ {target_title}")
                print(f"      Similarity: {edge.similarity:.3f}")
            
            if len(sorted_edges) > 5:
                print(f"   ... and {len(sorted_edges) - 5} more connections")
        
        print()
        
        # Citation analysis
        citation_edges = [e for e in graph_data.edges if e.metadata.get('edge_type') == 'source_citation']
        if citation_edges:
            print(f"📎 Citation Analysis (dashed arrows):")
            print(f"   Total citation edges: {len(citation_edges)}")
            
            # Find sections with most citations
            section_citation_counts = {}
            for edge in citation_edges:
                section_citation_counts[edge.target] = section_citation_counts.get(edge.target, 0) + 1
            
            top_cited_sections = sorted(section_citation_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            
            print(f"   Most cited sections:")
            for section_id, count in top_cited_sections:
                section_node = next((n for n in graph_data.nodes if n.id == section_id), None)
                if section_node:
                    print(f"      - {section_node.label}: {count} citations")
            
            # Find uncited sections
            uncited_sections = [n for n in section_nodes 
                              if not any(e.target == n.id and e.metadata.get('edge_type') == 'source_citation' 
                                        for e in graph_data.edges)]
            
            if uncited_sections:
                print(f"   ⚠️  Sections without citations: {len(uncited_sections)}")
                for node in uncited_sections[:3]:
                    print(f"      - {node.label}")
        
        print()
        print("=" * 70)
        print("✅ Graph generation completed!")
        print(f"💾 Cached at: data/graph_cache/")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error building graph: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
