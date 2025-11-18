#!/bin/bash
# 1. Test EmbeddingClient (calls Python /embed)
# Custom text
echo "1. Test EmbeddingClient"
curl -X POST "http://localhost:8080/api/test/vector/embed?text=What%20is%20deep%20learning"

# 2. Test Full Semantic Search (uses findNearestChunks)
# Custom query and limit
echo ""
echo "2. Test Full Semantic Search"
curl -X POST "http://localhost:8080/api/test/vector/semantic-search?query=How%20do%20neural%20networks%20work&limit=3"

# 3. Test Search All Chunks
echo ""
echo "3. Test Search All Chunks"
curl -X POST "http://localhost:8080/api/test/vector/search-all?query=artificial%20intelligence&limit=3"

