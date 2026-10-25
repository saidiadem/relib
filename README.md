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
- [Installation & Setup](#-installation--setup)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
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
- **Visual Auras**: Each article section displays a unique colored aura for visual distinctio

## 🚀 Installation & Setup

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

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

<div align="center">
  <sub>Built with ✊ by the ReLib Team</sub>
</div>
