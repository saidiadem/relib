/**
 * API Client for querying the backend knowledge graph API
 */

class GraphAPIClient {
    constructor(baseURL = "http://localhost:8000/api/v1") {
        this.baseURL = baseURL;
    }

    /**
     * Get full graph data
     * @param {string|null} topic - Optional topic filter
     * @param {boolean} includeMetadata - Include metadata in response
     * @returns {Promise<Object>} Graph data with nodes and edges
     */
    async getFullGraph(topic = null, includeMetadata = true) {
        const params = new URLSearchParams();
        if (topic) params.append("topic", topic);
        params.append("include_metadata", includeMetadata);

        const url = `${this.baseURL}/graph/full?${params}`;
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Failed to fetch graph: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Get nodes with optional filtering
     * @param {Object} options - Filter options
     * @param {string|null} options.topic - Topic filter
     * @param {number|null} options.group - Group filter
     * @param {number} options.limit - Maximum number of nodes
     * @returns {Promise<Array>} Array of nodes
     */
    async getNodes({ topic = null, group = null, limit = 100 } = {}) {
        const params = new URLSearchParams();
        if (topic) params.append("topic", topic);
        if (group !== null) params.append("group", group);
        params.append("limit", limit);

        const url = `${this.baseURL}/graph/nodes?${params}`;
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Failed to fetch nodes: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Get a specific node by ID
     * @param {string} nodeId - Node ID
     * @returns {Promise<Object>} Node data
     */
    async getNode(nodeId) {
        const url = `${this.baseURL}/graph/nodes/${nodeId}`;
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Failed to fetch node: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Get neighboring nodes for a specific node
     * @param {string} nodeId - Node ID
     * @param {number} maxDepth - Maximum depth for neighbor traversal
     * @returns {Promise<Array>} Array of neighboring nodes
     */
    async getNeighbors(nodeId, maxDepth = 1) {
        const params = new URLSearchParams({ max_depth: maxDepth });
        const url = `${this.baseURL}/graph/nodes/${nodeId}/neighbors?${params}`;
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Failed to fetch neighbors: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Get edges with optional filtering
     * @param {Object} options - Filter options
     * @param {string|null} options.nodeId - Filter by node ID
     * @param {number} options.minSimilarity - Minimum similarity threshold
     * @param {number} options.limit - Maximum number of edges
     * @returns {Promise<Array>} Array of edges
     */
    async getEdges({ nodeId = null, minSimilarity = 0.0, limit = 100 } = {}) {
        const params = new URLSearchParams();
        if (nodeId) params.append("node_id", nodeId);
        params.append("min_similarity", minSimilarity);
        params.append("limit", limit);

        const url = `${this.baseURL}/graph/edges?${params}`;
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Failed to fetch edges: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Query graph with complex filters
     * @param {Object} request - Query request
     * @param {Array<string>|null} request.nodeIds - Specific node IDs to query
     * @param {string|null} request.topic - Topic filter
     * @param {boolean} request.includeNeighbors - Include neighboring nodes
     * @param {number} request.maxDepth - Maximum depth for neighbor traversal
     * @returns {Promise<Object>} Query response with graph data
     */
    async queryGraph({
        nodeIds = null,
        topic = null,
        includeNeighbors = false,
        maxDepth = 1,
    } = {}) {
        const url = `${this.baseURL}/graph/query`;
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                node_ids: nodeIds,
                topic: topic,
                include_neighbors: includeNeighbors,
                max_depth: maxDepth,
            }),
        });

        if (!response.ok) {
            throw new Error(`Failed to query graph: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Build graph from Wikipedia article
     * @param {string} articleTitle - Wikipedia article title
     * @param {Array<string>} languages - Languages to analyze
     * @returns {Promise<Object>} Build result
     */
    async buildGraph(articleTitle, languages = ["en"]) {
        const params = new URLSearchParams({ article_title: articleTitle });
        languages.forEach((lang) => params.append("languages", lang));

        const url = `${this.baseURL}/graph/build?${params}`;
        const response = await fetch(url, { method: "POST" });

        if (!response.ok) {
            throw new Error(`Failed to build graph: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Convert API graph data to vis.js DataSet format
     * @param {Object} graphData - Graph data from API
     * @returns {Object} Object with nodes and edges DataSets
     */
    convertToVisFormat(graphData) {
        const nodesData = graphData.nodes.map((node) => ({
            id: node.id,
            label: node.label,
            content: node.content,
            group: node.group,
            shape: node.shape || "dot",
            size: node.size || 5,
            color: node.color,
            font: { color: "#36454F" },
            x: node.x,
            y: node.y,
        }));

        const edgesData = graphData.edges.map((edge) => ({
            from: edge.source,
            to: edge.target,
            width: edge.width || edge.similarity * 3,
            title: edge.title || `Similarity: ${edge.similarity.toFixed(2)}`,
            value: edge.value || edge.similarity,
        }));

        return {
            nodes: new vis.DataSet(nodesData),
            edges: new vis.DataSet(edgesData),
        };
    }
}

// Create a global instance
const graphAPI = new GraphAPIClient();
