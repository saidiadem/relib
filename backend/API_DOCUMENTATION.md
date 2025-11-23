# Backend API - Knowledge Graph Endpoints

## Overview

The backend provides RESTful API endpoints for querying and building knowledge graphs. Built with FastAPI, it supports filtering, graph traversal, and dynamic graph construction.

## Base URL

```
http://localhost:8000/api/v1
```

## API Endpoints

### 1. Get Full Graph

Retrieve the complete knowledge graph with all nodes and edges.

**Endpoint:** `GET /graph/full`

**Query Parameters:**

- `topic` (optional): Filter by topic keyword
- `include_metadata` (boolean, default: true): Include graph statistics

**Response:**

```json
{
  "nodes": [
    {
      "id": "provax1",
      "label": "Vaccines save lives",
      "content": "Vaccines have been scientifically proven...",
      "group": 1,
      "size": 10,
      "color": "#34A853",
      "shape": "dot",
      "x": null,
      "y": null,
      "metadata": {}
    }
  ],
  "edges": [
    {
      "source": "provax1",
      "target": "provax2",
      "similarity": 0.8,
      "width": 2.4,
      "title": "Similarity: 0.80",
      "value": 0.8,
      "metadata": {}
    }
  ],
  "metadata": {
    "node_count": 7,
    "edge_count": 10,
    "groups": [1, 2, 3],
    "avg_similarity": 0.62
  }
}
```

**Example:**

```bash
curl "http://localhost:8000/api/v1/graph/full?topic=vaccine&include_metadata=true"
```

---

### 2. Get Nodes

Retrieve nodes with optional filtering.

**Endpoint:** `GET /graph/nodes`

**Query Parameters:**

- `topic` (optional): Filter by topic in label or content
- `group` (optional): Filter by group number
- `limit` (integer, default: 100, max: 1000): Maximum nodes to return

**Response:**

```json
[
  {
    "id": "provax1",
    "label": "Vaccines save lives",
    "content": "...",
    "group": 1,
    "size": 10,
    "color": "#34A853",
    "shape": "dot",
    "metadata": {}
  }
]
```

**Examples:**

```bash
# Get all pro-vaccine nodes (group 1)
curl "http://localhost:8000/api/v1/graph/nodes?group=1&limit=50"

# Search for nodes about "immunity"
curl "http://localhost:8000/api/v1/graph/nodes?topic=immunity"
```

---

### 3. Get Specific Node

Retrieve a single node by ID.

**Endpoint:** `GET /graph/nodes/{node_id}`

**Path Parameters:**

- `node_id` (required): Node identifier

**Response:**

```json
{
  "id": "provax1",
  "label": "Vaccines save lives",
  "content": "Vaccines have been scientifically proven...",
  "group": 1,
  "size": 10,
  "color": "#34A853",
  "shape": "dot",
  "metadata": {}
}
```

**Example:**

```bash
curl "http://localhost:8000/api/v1/graph/nodes/provax1"
```

**Error Response (404):**

```json
{
  "detail": "Node provax1 not found"
}
```

---

### 4. Get Node Neighbors

Retrieve neighboring nodes up to a specified depth.

**Endpoint:** `GET /graph/nodes/{node_id}/neighbors`

**Path Parameters:**

- `node_id` (required): Node identifier

**Query Parameters:**

- `max_depth` (integer, default: 1, range: 1-3): Maximum traversal depth

**Response:**

```json
[
  {
    "id": "provax2",
    "label": "Herd immunity protects everyone",
    "group": 1,
    "size": 8,
    "color": "#34A853"
  },
  {
    "id": "hesitancy1",
    "label": "Need more research",
    "group": 3,
    "size": 8,
    "color": "#FBBC05"
  }
]
```

**Examples:**

```bash
# Get direct neighbors (depth 1)
curl "http://localhost:8000/api/v1/graph/nodes/provax1/neighbors?max_depth=1"

# Get neighbors up to 2 hops away
curl "http://localhost:8000/api/v1/graph/nodes/provax1/neighbors?max_depth=2"
```

---

### 5. Get Edges

Retrieve edges with optional filtering.

**Endpoint:** `GET /graph/edges`

**Query Parameters:**

- `node_id` (optional): Filter edges connected to this node
- `min_similarity` (float, default: 0.0, range: 0-1): Minimum similarity threshold
- `limit` (integer, default: 100, max: 1000): Maximum edges to return

**Response:**

```json
[
  {
    "source": "provax1",
    "target": "provax2",
    "similarity": 0.8,
    "width": 2.4,
    "title": "Similarity: 0.80",
    "value": 0.8,
    "metadata": {}
  }
]
```

**Examples:**

```bash
# Get all edges for a node
curl "http://localhost:8000/api/v1/graph/edges?node_id=provax1"

# Get only strong connections (similarity >= 0.7)
curl "http://localhost:8000/api/v1/graph/edges?min_similarity=0.7&limit=50"
```

---

### 6. Query Graph (Complex Filtering)

Execute complex graph queries with multiple filters.

**Endpoint:** `POST /graph/query`

**Request Body:**

```json
{
  "node_ids": ["provax1", "provax2"],
  "topic": "vaccine",
  "include_neighbors": true,
  "max_depth": 2
}
```

**Request Fields:**

- `node_ids` (optional): Array of specific node IDs
- `topic` (optional): Topic filter
- `include_neighbors` (boolean, default: false): Include neighboring nodes
- `max_depth` (integer, default: 1, range: 1-3): Neighbor traversal depth

**Response:**

```json
{
  "graph": {
    "nodes": [...],
    "edges": [...],
    "metadata": {
      "node_count": 5,
      "edge_count": 8,
      "query_type": "filtered"
    }
  },
  "query_metadata": {
    "requested_nodes": ["provax1", "provax2"],
    "include_neighbors": true,
    "max_depth": 2
  }
}
```

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/graph/query" \
  -H "Content-Type: application/json" \
  -d '{
    "node_ids": ["provax1", "antivax1"],
    "include_neighbors": true,
    "max_depth": 1
  }'
```

---

### 7. Build Graph from Article

Build a knowledge graph from a Wikipedia article.

**Endpoint:** `POST /graph/build`

**Query Parameters:**

- `article_title` (required): Wikipedia article title
- `languages` (array, default: ["en"]): Languages to analyze

**Response:**

```json
{
  "status": "success",
  "article": "Vaccines",
  "node_count": 15,
  "edge_count": 22
}
```

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/graph/build?article_title=Vaccines&languages=en&languages=fr"
```

---

## Data Models

### GraphNode

```python
{
  "id": str,                    # Unique identifier
  "label": str,                 # Display label
  "content": Optional[str],     # Detailed content
  "group": int,                 # Category/group number
  "size": float,                # Visual size (based on importance)
  "color": Optional[str],       # Hex color code
  "shape": str,                 # Shape type (default: "dot")
  "x": Optional[float],         # X coordinate
  "y": Optional[float],         # Y coordinate
  "metadata": Dict              # Additional metadata
}
```

### GraphEdge

```python
{
  "source": str,                # Source node ID
  "target": str,                # Target node ID
  "similarity": float,          # Similarity score (0-1)
  "width": Optional[float],     # Visual width
  "title": Optional[str],       # Tooltip text
  "value": Optional[float],     # Value for physics
  "metadata": Dict              # Additional metadata
}
```

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid parameter value"
}
```

### 404 Not Found

```json
{
  "detail": "Node provax99 not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Database connection failed"
}
```

---

## Usage Examples

### Python

```python
import httpx

# Get full graph
async with httpx.AsyncClient() as client:
    response = await client.get("http://localhost:8000/api/v1/graph/full")
    graph_data = response.json()
    print(f"Loaded {len(graph_data['nodes'])} nodes")

# Query specific nodes with neighbors
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/graph/query",
        json={
            "node_ids": ["provax1"],
            "include_neighbors": True,
            "max_depth": 2
        }
    )
    result = response.json()
    print(f"Query returned {len(result['graph']['nodes'])} nodes")
```

### JavaScript/Frontend

```javascript
// Get full graph
const response = await fetch("http://localhost:8000/api/v1/graph/full");
const graphData = await response.json();

// Get nodes by group
const provaxResponse = await fetch(
  "http://localhost:8000/api/v1/graph/nodes?group=1&limit=50"
);
const provaxNodes = await provaxResponse.json();

// Query with POST
const queryResponse = await fetch("http://localhost:8000/api/v1/graph/query", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    node_ids: ["provax1", "provax2"],
    include_neighbors: true,
    max_depth: 1,
  }),
});
const queryResult = await queryResponse.json();
```

---

## Running the Server

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000

# Run with custom host
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Server will be available at:

- API: http://localhost:8000/api/v1
- Docs: http://localhost:8000/docs (Swagger UI)
- ReDoc: http://localhost:8000/redoc (Alternative docs)

---

## CORS Configuration

Configure allowed origins in `backend/app/core/config.py`:

```python
class Settings(BaseSettings):
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "file://",  # For local HTML files
    ]
```

---

## Sample Data

The API includes sample vaccine sentiment data:

**Groups:**

- Group 1 (Green): Pro-vaccine statements
- Group 2 (Red): Anti-vaccine statements
- Group 3 (Yellow): Vaccine hesitancy statements

**Sample Nodes:**

- `provax1`: "Vaccines save lives"
- `antivax1`: "Vaccines contain toxins"
- `hesitancy1`: "Need more research"

**Sample Edges:**

- Strong connections within pro-vaccine group (similarity: 0.7-0.9)
- Weaker connections in anti-vaccine group (similarity: 0.3-0.5)
- Bridge connections through hesitancy nodes (similarity: 0.4-0.6)

---

## Testing

```bash
# Health check
curl http://localhost:8000/health

# Get API docs
curl http://localhost:8000/

# Test graph endpoint
curl http://localhost:8000/api/v1/graph/full | jq .
```

---

## Future Enhancements

- [ ] Database persistence (currently in-memory)
- [ ] User authentication
- [ ] Rate limiting
- [ ] Caching layer
- [ ] WebSocket support for real-time updates
- [ ] Graph algorithms (centrality, clustering, etc.)
- [ ] Export formats (GraphML, JSON-LD, etc.)
- [ ] Advanced semantic analysis
