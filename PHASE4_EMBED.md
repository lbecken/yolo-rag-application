# Phase 4: Python Embedding API (`/embed`)

## Overview

Phase 4 exposes a REST API endpoint for generating text embeddings. This allows the Java service (or any client) to request embeddings for arbitrary text, such as user queries during the RAG pipeline.

## Endpoint Specification

### POST `/embed`

Generate embeddings for a list of text strings.

#### Request

```json
{
  "texts": ["string1", "string2", ...]
}
```

#### Response

```json
{
  "vectors": [[0.1, 0.2, ...], [0.3, 0.4, ...]],
  "dimension": 384,
  "num_texts": 2
}
```

#### Response Fields

- `vectors`: List of embedding vectors (each vector is a list of 384 floats)
- `dimension`: The embedding dimension (384 for all-MiniLM-L6-v2)
- `num_texts`: Number of texts that were embedded

## Testing

### Prerequisites

Ensure the services are running:

```bash
docker-compose up --build
```

### Manual Testing with curl

#### Embed a single text

```bash
curl -X POST http://localhost:8000/embed \
  -H "Content-Type: application/json" \
  -d '{"texts": ["What is machine learning?"]}'
```

#### Embed multiple texts

```bash
curl -X POST http://localhost:8000/embed \
  -H "Content-Type: application/json" \
  -d '{"texts": ["First query", "Second query", "Third query"]}'
```

#### Check vector dimension

```bash
curl -X POST http://localhost:8000/embed \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Test"]}' | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'Dimension: {len(data[\"vectors\"][0])}')"
```

### Running Unit Tests

#### Inside Docker container (recommended)

```bash
docker-compose exec python-service pytest test_embed.py -v
```

#### Locally (if dependencies installed)

```bash
cd python-service
pytest test_embed.py -v
```

### Expected Test Output

```
test_embed.py::TestEmbedEndpoint::test_embed_single_text PASSED
test_embed.py::TestEmbedEndpoint::test_embed_multiple_texts PASSED
test_embed.py::TestEmbedEndpoint::test_embed_empty_texts_returns_error PASSED
test_embed.py::TestEmbedEndpoint::test_embed_different_texts_produce_different_vectors PASSED
test_embed.py::TestEmbedEndpoint::test_embed_similar_texts_produce_similar_vectors PASSED
test_embed.py::TestEmbedEndpoint::test_embed_vectors_are_normalized PASSED
test_embed.py::TestEmbedEndpoint::test_embed_missing_texts_field PASSED
test_embed.py::test_embed_health_check PASSED
```

## Integration with Java Service

The Java service can call this endpoint to get embeddings for user queries:

```java
// Example WebClient call
WebClient webClient = WebClient.create("http://python-service:8000");

Map<String, List<String>> request = Map.of("texts", List.of(userQuery));

EmbedResponse response = webClient.post()
    .uri("/embed")
    .bodyValue(request)
    .retrieve()
    .bodyToMono(EmbedResponse.class)
    .block();

List<List<Double>> vectors = response.getVectors();
```

## Model Consistency

The `/embed` endpoint uses the **same embedding model** as the `/ingest` endpoint:

- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimension**: 384

This ensures that query embeddings are consistent with document chunk embeddings stored in the database, which is essential for accurate semantic similarity search.

## Error Handling

| Status Code | Description |
|-------------|-------------|
| 200 | Success - embeddings generated |
| 400 | Bad Request - empty texts list |
| 422 | Validation Error - missing required fields |
| 500 | Internal Server Error - embedding generation failed |

## Files Modified/Added

- `python-service/main.py` - Added EmbedRequest, EmbedResponse models and `/embed` endpoint
- `python-service/test_embed.py` - Unit tests for the endpoint
- `python-service/requirements.txt` - Added pytest and httpx for testing
- `PHASE4_EMBED.md` - This documentation

## Next Steps (Phase 5)

With the embedding API complete, Phase 5 can implement:

- RAG query pipeline in Java service
- Calling `/embed` to vectorize user queries
- Combining retrieval results with LLM generation
