# OpenAI Embeddings-Based Knowledge Graph

## Overview

This implementation uses **OpenAI embeddings** to build knowledge graphs where sections and subsections of Wikipedia articles are connected based on their **semantic similarity** (cosine similarity metric).

## How It Works

### 1. **Section Extraction**

- Fetches Wikipedia article with all sections and subsections
- Each section becomes a node in the graph
- Optional: Article summary can be included as root node

### 2. **Embedding Generation**

- Uses OpenAI's `text-embedding-3-small` model (configurable)
- Generates embeddings for each section's text
- Captures semantic meaning in vector space

### 3. **Similarity Calculation**

- Computes **cosine similarity** between all section pairs
- Creates similarity matrix (n × n) for all sections
- Values range from 0 (no similarity) to 1 (identical)

### 4. **Edge Creation**

- Edges connect sections above similarity threshold (default: 0.3)
- Edge width proportional to similarity score
- Only semantically related sections are connected

## Usage

### Basic Example

```python
from app.services.knowledge_graph_builder import KnowledgeGraphBuilder

# Initialize with OpenAI API key
builder = KnowledgeGraphBuilder(openai_api_key="your-key-here")

# Build graph from Wikipedia article
graph_data = await builder.build_from_article(
    article_title="Maji Maji Rebellion",
    languages=['en', 'sw'],
    include_summary=True
)

# Access nodes and edges
print(f"Nodes: {len(graph_data.nodes)}")
print(f"Edges: {len(graph_data.edges)}")
```

### Run Example Script

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Or add to .env file
echo "OPENAI_API_KEY=your-key-here" >> .env

# Run example
cd backend
python example_embedding_graph.py
```

## Configuration

### Environment Variables

```env
# Required
OPENAI_API_KEY=your-openai-api-key-here

# Optional
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
SIMILARITY_THRESHOLD=0.3
```

### Settings in `config.py`

```python
OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
SIMILARITY_THRESHOLD: float = 0.3  # Minimum similarity for edge
```

## Graph Structure

### Nodes (Sections)

Each node represents a section/subsection with:

```python
GraphNode(
    id="section_0",
    label="History",
    content="Preview of section text...",
    group=1,              # Section level (1, 2, 3...)
    size=15.5,            # Based on text length + connections
    color="#EA4335",      # Color-coded by level
    metadata={
        'level': 1,
        'type': 'section',
        'has_embedding': True,
        'text_length': 2500
    }
)
```

### Edges (Similarity)

Each edge represents semantic similarity:

```python
GraphEdge(
    source="section_0",
    target="section_3",
    similarity=0.72,      # Cosine similarity (0-1)
    width=3.6,            # Visual width (similarity * 5)
    title="History ↔ Colonial Period\nSimilarity: 0.720",
    metadata={
        'source_title': 'History',
        'target_title': 'Colonial Period'
    }
)
```

## Color Coding by Level

Sections are color-coded by hierarchy:

- 🔵 **Blue** (#4285F4) - Summary (level 0)
- 🔴 **Red** (#EA4335) - Top-level sections (level 1)
- 🟡 **Yellow** (#FBBC04) - Subsections (level 2)
- 🟢 **Green** (#34A853) - Sub-subsections (level 3)
- 🟣 **Purple** (#9C27B0) - Deeper sections (level 4+)
- ⚫ **Gray** (#757575) - Very deep sections

## Features

### ✨ Semantic Understanding

- Captures meaning beyond keywords
- Connects conceptually related sections
- Identifies thematic relationships

### 📊 Configurable Threshold

- Adjust `SIMILARITY_THRESHOLD` to control edge density
- Higher threshold = fewer, stronger connections
- Lower threshold = more connections, including weaker ones

### 📏 Size & Width Scaling

- **Node size**: Based on text length + connection count
- **Edge width**: Proportional to similarity score
- Visual representation of importance

### 🎯 Smart Filtering

- Minimum text length filter (default: 50 chars)
- Skips empty or stub sections
- Only creates edges above threshold

## Graph Metadata

The returned graph includes comprehensive statistics:

```python
{
    "node_count": 12,
    "edge_count": 28,
    "article_title": "Maji Maji Rebellion",
    "similarity_threshold": 0.3,
    "embedding_model": "text-embedding-3-small",
    "avg_similarity": 0.452,
    "max_similarity": 0.856,
    "min_similarity": 0.301
}
```

## Methods

### `build_from_article()`

Main method to build graph from Wikipedia article.

**Parameters:**

- `article_title` (str): Wikipedia article title
- `languages` (List[str]): Language codes for analysis
- `include_summary` (bool): Include article summary as root node

**Returns:** `KnowledgeGraphData`

### `build_graph_from_sections()`

Build graph from pre-fetched article data.

**Parameters:**

- `article_data` (Dict): Article data from WikipediaService
- `include_summary` (bool): Include summary node
- `min_text_length` (int): Minimum section length

**Returns:** `KnowledgeGraphData`

### `get_embedding()`

Get OpenAI embedding for text.

**Parameters:**

- `text` (str): Text to embed

**Returns:** `List[float]` - Embedding vector

### `calculate_similarity_matrix()`

Calculate cosine similarity between embeddings.

**Parameters:**

- `embeddings` (List[List[float]]): List of embedding vectors

**Returns:** `np.ndarray` - Similarity matrix

## Cost Considerations

### OpenAI API Costs

The `text-embedding-3-small` model pricing (as of 2024):

- **$0.02 per 1M tokens**

Example article with 10 sections (avg 500 words each):

- ~5,000 words total
- ~6,667 tokens (1.33 tokens per word)
- **Cost: ~$0.0001** (practically free)

### Optimization Tips

1. **Cache embeddings** - Store computed embeddings to avoid recomputation
2. **Batch processing** - Process multiple sections in single API call
3. **Text truncation** - Already implemented (8000 chars max)
4. **Use smaller sections** - Filter out very short sections

## Example Output

```
📄 Building graph for: Maji Maji Rebellion

✅ Graph built successfully!

📊 Graph Statistics:
   Nodes: 15
   Edges: 42
   Similarity Threshold: 0.3
   Embedding Model: text-embedding-3-small

🔗 Similarity Metrics:
   Average: 0.428
   Max: 0.823
   Min: 0.305

📝 Sample Nodes:
   1. Summary (Level 0)
   2. Background (Level 1)
   3. Causes (Level 1)
   4. Colonial Policies (Level 2)
   5. Economic Exploitation (Level 2)
   ... and 10 more

🔗 Sample Edges (Top 5 by similarity):
   1. Colonial Policies ↔ Economic Exploitation
      Similarity: 0.823
   2. German Response ↔ Military Actions
      Similarity: 0.756
   3. Background ↔ Causes
      Similarity: 0.698
   4. Casualties ↔ Aftermath
      Similarity: 0.654
   5. Traditional Beliefs ↔ Religious Motivation
      Similarity: 0.612
   ... and 37 more
```

## Integration with Decolonial Analysis

This graph structure enables:

1. **Identifying dominant narratives** - Clusters of similar sections
2. **Finding underrepresented topics** - Isolated nodes with few connections
3. **Analyzing perspective balance** - Compare similarity within colonial vs. native topics
4. **Cross-language comparison** - Build graphs for different languages and compare

## Troubleshooting

### No edges created

- Lower `SIMILARITY_THRESHOLD` (try 0.2)
- Check if sections have enough text
- Verify OpenAI API key is valid

### Too many edges

- Raise `SIMILARITY_THRESHOLD` (try 0.4 or 0.5)
- Increase `min_text_length` to filter short sections

### API errors

- Check API key in environment variables
- Verify OpenAI account has credits
- Check rate limits

## Next Steps

Potential enhancements:

- [ ] Caching layer for embeddings
- [ ] Batch embedding generation
- [ ] Alternative embedding models (Sentence Transformers)
- [ ] Graph visualization with Pyvis
- [ ] Hierarchical clustering
- [ ] Topic modeling integration
