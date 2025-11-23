"""
Example: Building a knowledge graph with OpenAI embeddings and cosine similarity
"""
import asyncio
import os
from dotenv import load_dotenv

from app.services.knowledge_graph_builder import KnowledgeGraphBuilder

# Load environment variables
load_dotenv()


async def main():
    """
    Build and display a knowledge graph using embeddings
    """
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please set it in your .env file or export it:")
        print("  export OPENAI_API_KEY='your-key-here'")
        return
    
    print("=" * 60)
    print("Knowledge Graph with OpenAI Embeddings")
    print("=" * 60)
    print()
    
    # Initialize graph builder
    builder = KnowledgeGraphBuilder(openai_api_key=api_key)
    
    # Example article
    article_title = "Maji Maji Rebellion"
    print(f"📄 Building graph for: {article_title}")
    print()
    
    # Build graph
    try:
        graph_data = await builder.build_from_article(
            article_title=article_title,
            languages=['en', 'sw'],  # English and Swahili
            include_summary=True
        )
        
        print("✅ Graph built successfully!")
        print()
        print(f"📊 Graph Statistics:")
        print(f"   Nodes: {graph_data.metadata['node_count']}")
        print(f"   Edges: {graph_data.metadata['edge_count']}")
        print(f"   Similarity Threshold: {graph_data.metadata['similarity_threshold']}")
        print(f"   Embedding Model: {graph_data.metadata['embedding_model']}")
        print()
        
        if graph_data.edges:
            print(f"🔗 Similarity Metrics:")
            print(f"   Average: {graph_data.metadata['avg_similarity']:.3f}")
            print(f"   Max: {graph_data.metadata['max_similarity']:.3f}")
            print(f"   Min: {graph_data.metadata['min_similarity']:.3f}")
            print()
        
        print(f"📝 Sample Nodes:")
        for i, node in enumerate(graph_data.nodes[:5]):
            print(f"   {i+1}. {node.label} (Level {node.metadata.get('level', '?')})")
        
        if len(graph_data.nodes) > 5:
            print(f"   ... and {len(graph_data.nodes) - 5} more")
        
        print()
        
        if graph_data.edges:
            print(f"🔗 Sample Edges (Top 5 by similarity):")
            sorted_edges = sorted(
                graph_data.edges, 
                key=lambda e: e.similarity, 
                reverse=True
            )
            
            for i, edge in enumerate(sorted_edges[:5]):
                source_title = edge.metadata.get('source_title', edge.source)
                target_title = edge.metadata.get('target_title', edge.target)
                print(f"   {i+1}. {source_title} ↔ {target_title}")
                print(f"      Similarity: {edge.similarity:.3f}")
            
            if len(sorted_edges) > 5:
                print(f"   ... and {len(sorted_edges) - 5} more")
        
        print()
        print("=" * 60)
        print("✅ Example completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error building graph: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
