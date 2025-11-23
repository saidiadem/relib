# ReLib

<div align="center">

<img src="Frontend/assets/image.png" alt="ReLib Logo" width="400"/>

  <br>

  <br>

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()
[![Made with Python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Made with JavaScript](https://img.shields.io/badge/Made%20with-JavaScript-yellow.svg)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Last Updated](https://img.shields.io/badge/Last%20Updated-November%202025-brightgreen.svg)]()

</div>

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Installation & Setup](#-installation--setup)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Development Guidelines](#-development-guidelines)
- [License](#-license)

## 🔍 Overview

ReLib is an advanced knowledge graph visualization platform designed to explore and analyze historical narratives, with a focus on colonial history and power dynamics. The system provides interactive graph networks that visualize Wikipedia articles as interconnected sections, while highlighting colonial and native perspectives through intelligent text analysis and color-coded source attribution.

The platform employs sophisticated visualization techniques including colored auras, semantic highlighting, and source differentiation to provide users with nuanced insights into historical narratives and the biases present in academic sources.

## ✨ Key Features

### 🕸️ Interactive Knowledge Graph Visualization

- **Dynamic Wikipedia Integration**: Fetch and display Wikipedia articles with automatic section parsing
- **Section-Based Navigation**: Click article nodes to load full content, then navigate to specific sections
- **Neighborhood Highlighting**: Explore relationships between article sections and sources
- **Physics-Based Layout**: Animated node placement with customizable draw order
- **Real-Time Search**: Search and filter nodes dynamically

### 🎨 Colonial Narrative Analysis

- **Intelligent Text Highlighting**:
  - **Red**: Colonizer-related terms (French, colonial, occupation, European, invasion, etc.)
  - **Green**: Native/indigenous terms (Tunisian, Bey, nationalist, independence, resistance, etc.)
  - **Yellow**: Action verbs connecting colonial and native actors (occupied, invaded, resisted, liberated, etc.)
- **Source Attribution**:
  - **Red Dots**: Western/colonial academic sources
  - **Green Dots**: Tunisian/local sources
- **Visual Auras**: Each article section displays a unique colored aura for visual distinction

### 📊 Graph Network Features

- **Animated Node Addition**: Nodes appear sequentially with smooth transitions
- **Edge Relationships**: Dashed arrows from sources to content, solid arrows between sections
- **Similarity Scores**: Visual representation of relationship strength through edge width
- **Hover Tooltips**: Detailed information on nodes and edges
- **Wikipedia Sidebar**: Split-screen article view with section navigation

### 🔍 Advanced Backend API

- **Knowledge Graph Service**: Manages nodes, edges, and relationships
- **Query System**: Filter by node IDs, include neighbors, adjust depth
- **Multiple Endpoints**: Full graph access, filtered queries, node/edge retrieval

## 🏛️ Architecture

ReLib consists of three main components:

1. **Landing Page**: Entry point with animated background and search functionality
2. **Graph Visualization**: Interactive network showing Wikipedia articles as interconnected sections with source attribution
3. **Backend API**: FastAPI-powered service providing knowledge graph data and query capabilities

## 🛠️ Technology Stack

### Frontend Technologies

- **[vis.js](https://visjs.github.io/vis-network/)**: Network visualization library for interactive graph networks
- **Vanilla JavaScript**: Core functionality without framework dependencies
- **Wikipedia MediaWiki API**: Real-time article fetching and parsing
- **CSS3**: Advanced styling with animations and transitions

### Backend Technologies

- **[Python 3.13](https://www.python.org/)**: Core programming language
- **[FastAPI](https://fastapi.tiangolo.com/)**: Modern, fast web framework for building APIs
- **[Pydantic](https://docs.pydantic.dev/)**: Data validation using Python type annotations
- **[NetworkX](https://networkx.org/)**: Python library for graph network operations and analysis
- **[Uvicorn](https://www.uvicorn.org/)**: Lightning-fast ASGI server implementation

## 🚀 Installation & Setup

### Prerequisites

- Python 3.13+
- uv (Python package installer)
- Git

### Step-by-Step Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd relib
   ```

2. **Backend Setup**

   ```bash
   cd backend

   # Create virtual environment with uv
   uv venv

   # Activate virtual environment
   # On Windows:
   .venv\Scripts\activate
   # On Unix or MacOS:
   source .venv/bin/activate

   # Install dependencies
   uv pip install -r requirements.txt
   ```

3. **Start the FastAPI Backend**

   ```bash
   # From the backend directory
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`

   - API Documentation: `http://localhost:8000/docs`
   - Alternative Docs: `http://localhost:8000/redoc`

4. **Frontend Setup**

   ```bash
   cd ../Frontend

   # For development, use Python's built-in HTTP server
   python -m http.server 8080
   ```

5. **Access the Application**

   - Graph Visualization: `http://localhost:8080/Graph%20network/index.html`

## 🎮 Running the Application

### Quick Start

Once you have completed the installation, follow these steps to run ReLib:

1. **Start the Backend Server** (Terminal 1)

   ```bash
   cd backend
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   You should see output like:

   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
   INFO:     Started reloader process
   INFO:     Started server process
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   ```

2. **Start the Frontend Server** (Terminal 2)

   ```bash
   cd Frontend
   python -m http.server 8080
   ```

   You should see:

   ```
   Serving HTTP on :: port 8080 (http://[::]:8080/) ...
   ```

3. **Open in Browser**

   Navigate to: `http://localhost:8080/Graph%20network/index.html`

### Verifying the Setup

- **Backend Health Check**: Visit `http://localhost:8000/docs` to see the interactive API documentation
- **Frontend**: The graph visualization should load with the French Protectorate of Tunisia network
- **Wikipedia Integration**: Click on any article node to load Wikipedia content in the sidebar

### Troubleshooting

| Issue                     | Solution                                                                                                     |
| ------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Backend won't start       | Ensure virtual environment is activated and dependencies are installed: `uv pip install -r requirements.txt` |
| Frontend shows blank page | Check browser console for errors. Verify backend is running on port 8000                                     |
| CORS errors               | Ensure backend `origins` list includes `http://localhost:8080` in `app/main.py`                              |
| Graph doesn't load data   | Verify `apiBaseURL` in `graph-data.js` points to `http://localhost:8000/api/v1`                              |
| Port already in use       | Change port numbers: Backend `--port 8001`, Frontend `python -m http.server 8081`                            |

### Configuration

**Backend Configuration** (`backend/app/main.py`):

```python
# CORS settings for frontend access
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
```

**Frontend Configuration** (`Frontend/Graph network/graph-data.js`):

```javascript
var dataMode = "api"; // Use backend API
var apiBaseURL = "http://localhost:8000/api/v1";
```

## 📚 API Documentation

### Endpoints

| Endpoint                            | Method | Description                                     |
| ----------------------------------- | ------ | ----------------------------------------------- |
| `/api/v1/graph/full`                | GET    | Retrieve complete knowledge graph               |
| `/api/v1/graph/query`               | POST   | Query graph with filters and neighbor inclusion |
| `/api/v1/graph/nodes`               | GET    | Get filtered list of nodes                      |
| `/api/v1/graph/nodes/{node_id}`     | GET    | Get specific node by ID                         |
| `/api/v1/graph/neighbors/{node_id}` | GET    | Get neighboring nodes                           |
| `/api/v1/graph/edges`               | GET    | Get filtered list of edges                      |

### Example: Query Graph

```bash
POST /api/v1/graph/query
Content-Type: application/json

{
  "node_ids": ["article1", "section1"],
  "include_neighbors": true,
  "max_depth": 2
}
```

### Example Response

```json
{
  "nodes": [
    {
      "id": "article1",
      "label": "French protectorate of Tunisia",
      "content": "The French protectorate of Tunisia was established by the Treaty of Bardo in 1881",
      "group": 1,
      "size": 15,
      "color": {
        "background": "#D4B896",
        "border": "#8B0000"
      },
      "shape": "box",
      "borderWidth": 3,
      "draw_order": 1
    }
  ],
  "edges": [
    {
      "source": "source1",
      "target": "article1",
      "similarity": 0.95,
      "width": 1,
      "dashes": true,
      "arrows": "to",
      "draw_order": 8
    }
  ],
  "metadata": {
    "node_count": 14,
    "edge_count": 18,
    "query_type": "filtered"
  }
}
```

## 📁 Project Structure

```
README.md
backend/
    app/
        main.py                      # FastAPI application entry point
        __init__.py
        api/
            routes/
                graph.py             # Graph API endpoints
                analysis.py          # Analysis endpoints
        models/
            graph_models.py          # Pydantic models for graph data
            schemas.py               # Request/response schemas
        services/
            graph_query_service.py   # Knowledge graph service with sample data
            analysis_orchestrator.py # Analysis orchestration service
            knowledge_graph_builder.py # Graph building utilities
            wikipedia_service.py     # Wikipedia API integration
        analyzers/
            actor_analyzer.py        # Actor analysis
            agency_analyzer.py       # Agency detection
            context_analyzer.py      # Context analysis
            language_analyzer.py     # Language pattern analysis
            provenance_scorer.py     # Source provenance scoring
        data/                        # Data files for analysis
    requirements.txt                 # Python dependencies
    pyproject.toml                  # Project configuration
    .venv/                          # Virtual environment

Frontend/
    Graph network/
        index.html                   # Main graph visualization page
        graph.html                   # Alternative graph page
        graph-data.js                # Data management and API integration
        graph-init.js                # Graph initialization
        graph-highlight.js           # Node highlighting functionality
        graph-filter.js              # Filtering functionality
        api-client.js                # API communication utilities
        styles.css                   # Graph visualization styles
    assets/
        image.png                    # ReLib logo
```

## 💻 Development Guidelines

### Backend Development

1. **Models**: Define data structures in `app/models/graph_models.py` using Pydantic
2. **Services**: Implement business logic in `app/services/`
3. **Routes**: Add API endpoints in `app/api/routes/`
4. **Type Safety**: Use type hints and Pydantic validation throughout

### Frontend Development

1. **Graph Data**: Manage nodes and edges in `Frontend/Graph network/graph-data.js`
2. **API Integration**: All backend communication through `api-client.js`
3. **Wikipedia Integration**: Article fetching via MediaWiki API
4. **Highlighting**: Node highlighting managed in `graph-highlight.js`
5. **Filtering**: Graph filtering functionality in `graph-filter.js`
6. **Initialization**: Graph setup and configuration in `graph-init.js`

### Adding New Sources

To add a new academic source:

```python
# In backend/app/services/graph_query_service.py
GraphNode(
    id="source13",
    label="Author (Year)",
    content="Full citation details",
    group=4,  # or 5 for native sources
    size=8,
    color="#DC143C",  # Red for colonial, #28A745 for native
    shape="dot",
    draw_order=20,
)
```

### Adding New Article Sections

```python
GraphNode(
    id="section7",
    label="Section Title",
    content="Section description",
    group=1,
    size=10,
    color={"background": "#D4B896", "border": "#ColorCode"},
    shape="box",
    borderWidth=3,
    draw_order=8,
)
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

<div align="center">
  <sub>Built with ❤️ by the ReLib Team</sub>
</div>
