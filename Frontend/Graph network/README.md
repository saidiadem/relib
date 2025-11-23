# Knowledge Graph Frontend

This frontend visualizes knowledge graphs using vis.js network visualization library. It supports both local hard-coded data and dynamic API-based data from the backend.

## Structure

### Files

- **graph.html** - Main HTML page with network visualization
- **graph-data.js** - Graph data loading (supports local and API modes)
- **api-client.js** - API client for backend communication
- **graph-init.js** - Graph initialization and configuration
- **graph-highlight.js** - Node highlighting functionality
- **graph-filter.js** - Node filtering functionality


Fetches data dynamically from the backend API.

```javascript
var dataMode = "api"; // in graph-data.js
var apiBaseURL = "http://localhost:8000/api/v1"; // Configure backend URL
```

## API Integration

### Available API Endpoints

#### Get Full Graph

```javascript
GET /api/v1/graph/full?topic=&include_metadata=true
```

#### Get Nodes

```javascript
GET /api/v1/graph/nodes?topic=&group=&limit=100
```

#### Get Specific Node

```javascript
GET / api / v1 / graph / nodes / { node_id };
```

#### Get Node Neighbors

```javascript
GET /api/v1/graph/nodes/{node_id}/neighbors?max_depth=1
```

#### Get Edges

```javascript
GET /api/v1/graph/edges?node_id=&min_similarity=0.0&limit=100
```

#### Query Graph (POST)

```javascript
POST /api/v1/graph/query
Body: {
  "node_ids": ["node1", "node2"],
  "topic": "vaccine",
  "include_neighbors": true,
  "max_depth": 2
}
```

#### Build Graph from Article (POST)

```javascript
POST /api/v1/graph/build?article_title=Vaccines&languages=en
```

### Using the API Client

```javascript
// Get full graph
const graphData = await graphAPI.getFullGraph();

// Get nodes by group
const proVaxNodes = await graphAPI.getNodes({ group: 1 });

// Get specific node
const node = await graphAPI.getNode("provax1");

// Get neighbors
const neighbors = await graphAPI.getNeighbors("provax1", 2);

// Query with filters
const result = await graphAPI.queryGraph({
  nodeIds: ["provax1", "provax2"],
  includeNeighbors: true,
  maxDepth: 1,
});

// Convert API data to vis.js format
const { nodes, edges } = graphAPI.convertToVisFormat(graphData);
```

## Graph Data Format

### Node Structure

```javascript
{
  id: "unique_id",
  label: "Node Label",
  content: "Detailed description",
  group: 1,              // Group/category (1=provax, 2=antivax, 3=hesitancy)
  size: 10,              // Visual size
  color: "#34A853",      // Color
  shape: "dot",          // Shape
  x: 100,                // Optional X position
  y: 200                 // Optional Y position
}
```

### Edge Structure

```javascript
{
  source: "node_id_1",   // Source node ID
  target: "node_id_2",   // Target node ID
  similarity: 0.75,      // Similarity score (0-1)
  width: 2.25,           // Visual width
  title: "Similarity: 0.75",  // Tooltip
  value: 0.75            // Value for physics
}
```

## Features

### Interactive Visualization

- **Drag & Drop**: Move nodes around
- **Zoom & Pan**: Mouse wheel and drag
- **Node Selection**: Click to select and highlight
- **Hover Info**: Tooltips on hover
- **Search**: Search nodes by label
- **Filtering**: Filter by node properties

### Neighborhood Highlighting

Clicking a node highlights:

- Selected node (full color)
- Direct neighbors (medium opacity)
- 2nd degree neighbors (low opacity)
- Other nodes (very low opacity)

### Color Coding

- **Green (#34A853)**: Pro-vaccine statements
- **Red (#EA4335)**: Anti-vaccine statements
- **Yellow (#FBBC05)**: Vaccine hesitancy statements

## Running the Frontend

### With Local Data

1. Open `graph.html` in a web browser
2. Data loads from hard-coded values in `graph-data.js`

### With API Data

1. Start the backend server:

   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. Update `graph-data.js`:

   ```javascript
   var dataMode = "api";
   var apiBaseURL = "http://localhost:8000/api/v1";
   ```

3. Open `graph.html` in a web browser
4. Data fetches from the API

## CORS Configuration

If using API mode, ensure the backend allows CORS from your frontend origin:

```python
# backend/app/core/config.py
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "file://",  # For local HTML files
]
```

## Customization

### Physics Configuration

Modify in `graph.html`:

```javascript
physics: {
  forceAtlas2Based: {
    gravitationalConstant: -50,
    centralGravity: 0.015,
    springLength: 100,
    springConstant: 0.08,
    damping: 0.4,
    avoidOverlap: 0
  },
  solver: "forceAtlas2Based",
  stabilization: {
    iterations: 1000
  }
}
```

### Visual Styling

Modify node and edge properties in the options object.

## Example: Building Custom Graph

```javascript
// Build graph from Wikipedia article
async function buildArticleGraph(articleTitle) {
  try {
    // Trigger graph build
    const buildResult = await graphAPI.buildGraph(articleTitle, ["en"]);
    console.log("Graph built:", buildResult);

    // Fetch the new graph
    const graphData = await graphAPI.getFullGraph(articleTitle);

    // Convert to vis.js format
    const { nodes, edges } = graphAPI.convertToVisFormat(graphData);

    // Update network
    network.setData({ nodes, edges });
  } catch (error) {
    console.error("Failed to build graph:", error);
  }
}

// Usage
buildArticleGraph("Vaccines");
```

## Troubleshooting

### Graph Not Loading from API

1. Check backend is running: `curl http://localhost:8000/health`
2. Check console for CORS errors
3. Verify `apiBaseURL` is correct
4. Check network tab for failed requests

### Empty Graph

1. Check if data mode is set correctly
2. Verify API returns data: Visit `http://localhost:8000/api/v1/graph/full` in browser
3. Check console for errors

### Performance Issues

1. Limit number of nodes/edges
2. Adjust physics stabilization iterations
3. Use filtering to show subsets of data
4. Disable physics after stabilization

## Dependencies

- **vis-network**: ^9.1.2 - Network visualization
- **tom-select**: ^2.0.0-rc.4 - Enhanced select dropdown
- **bootstrap**: ^5.0.0-beta3 - UI styling

All loaded via CDN in `graph.html`.
