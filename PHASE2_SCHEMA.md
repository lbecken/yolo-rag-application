# Phase 2: Database Schema & pgvector Integration

## Overview

Phase 2 implements the database schema for documents and chunks with pgvector support for semantic search. This phase establishes the foundation for storing PDF documents and their embeddings in PostgreSQL.

## What Was Implemented

### 1. Flyway Database Migrations

Replaced JPA's auto-update mode with Flyway for better migration control.

**Configuration Changes:**
- Added Flyway dependencies to `pom.xml`
- Changed `spring.jpa.hibernate.ddl-auto` from `update` to `validate`
- Configured Flyway in `application.properties`

**Migration Files:**
- `V1__create_documents_table.sql`: Creates the documents table
- `V2__create_chunks_table.sql`: Creates the chunks table with vector embeddings

### 2. Database Schema

#### Documents Table

Stores metadata about uploaded PDF documents.

```sql
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    filename VARCHAR(500) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `id`: Auto-incrementing primary key
- `title`: Human-readable document title
- `filename`: Original filename (unique constraint)
- `created_at`: Upload timestamp

**Indexes:**
- Primary key index on `id`
- Unique index on `filename`
- Index on `created_at` for sorting

#### Chunks Table

Stores document chunks with their embeddings for semantic search.

```sql
CREATE TABLE chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL,
    text TEXT NOT NULL,
    page_start INTEGER NOT NULL,
    page_end INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding vector(384) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_chunks_document FOREIGN KEY (document_id)
        REFERENCES documents(id) ON DELETE CASCADE,
    CONSTRAINT unique_chunk_per_document UNIQUE (document_id, chunk_index)
);
```

**Fields:**
- `id`: Auto-incrementing primary key
- `document_id`: Foreign key to documents table
- `text`: The actual text content of the chunk
- `page_start`: Starting page number (0-indexed)
- `page_end`: Ending page number (0-indexed)
- `chunk_index`: Sequential index within document (0-indexed)
- `embedding`: 384-dimensional vector from sentence-transformers
- `created_at`: Creation timestamp

**Indexes:**
- Primary key index on `id`
- Index on `document_id` for fast lookups
- Index on `chunk_index` for ordering
- **HNSW index on `embedding`** for fast vector similarity search
- Unique constraint on `(document_id, chunk_index)`

### 3. pgvector Integration

**HNSW Index Configuration:**
```sql
CREATE INDEX idx_chunks_embedding_hnsw ON chunks
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
```

**Parameters:**
- `m = 16`: Number of connections per layer (higher = better recall, slower build)
- `ef_construction = 64`: Size of candidate list during construction
- `vector_cosine_ops`: Use cosine distance (most common for embeddings)

**Distance Operators:**
- `<->`: Cosine distance (used in this project)
- `<#>`: Negative inner product
- `<=>`: Euclidean distance (L2)

### 4. JPA Entities

**Document Entity:**
- File: `java-service/src/main/java/com/rag/app/model/Document.java`
- Maps to `documents` table
- Manages bidirectional relationship with chunks
- Automatic timestamp generation

**Chunk Entity:**
- File: `java-service/src/main/java/com/rag/app/model/Chunk.java`
- Maps to `chunks` table
- Custom methods for embedding conversion:
  - `embeddingToString(float[])`: Convert to pgvector format
  - `stringToEmbedding(String)`: Parse from pgvector format
  - `getEmbeddingArray()`: Get as float array
  - `setEmbeddingArray(float[])`: Set from float array

### 5. JPA Repositories

**DocumentRepository:**
- File: `java-service/src/main/java/com/rag/app/repository/DocumentRepository.java`
- Standard CRUD operations
- Custom methods: `findByFilename()`, `existsByFilename()`

**ChunkRepository:**
- File: `java-service/src/main/java/com/rag/app/repository/ChunkRepository.java`
- Standard CRUD operations
- Vector similarity search queries:
  - `findTopKSimilarChunks()`: Find K most similar chunks globally
  - `findTopKSimilarChunksInDocument()`: Find K similar chunks in a document
  - `findSimilarChunksWithinThreshold()`: Find chunks within distance threshold

### 6. Test Controller

**VectorTestController:**
- File: `java-service/src/main/java/com/rag/app/controller/VectorTestController.java`
- Endpoints for testing vector operations:
  - `POST /api/test/vector/init`: Initialize test data
  - `POST /api/test/vector/search`: Test similarity search
  - `GET /api/test/vector/chunks`: List all chunks
  - `DELETE /api/test/vector/clear`: Clear test data
  - `GET /api/test/vector/health`: Health check

### 7. SQL Test Script

**File:** `infrastructure/test_vector_operations.sql`
- Direct SQL demonstration of vector operations
- Can be run in PostgreSQL client
- Shows different distance operators
- Verifies HNSW index usage

## How to Test

### Step 1: Start the Services

```bash
docker-compose up --build
```

This will:
1. Start PostgreSQL with pgvector
2. Run Flyway migrations automatically
3. Create the documents and chunks tables
4. Start the Java service

### Step 2: Verify Migrations

Check that migrations were applied successfully:

```bash
docker-compose exec db psql -U raguser -d ragdb -c "SELECT version, description, success FROM flyway_schema_history ORDER BY installed_rank;"
```

Expected output:
```
 version |         description          | success
---------+------------------------------+---------
 1       | create documents table       | t
 2       | create chunks table          | t
```

### Step 3: Verify Tables

Check that tables were created:

```bash
docker-compose exec db psql -U raguser -d ragdb -c "\dt"
```

Expected output:
```
                  List of relations
 Schema |         Name          | Type  |  Owner
--------+-----------------------+-------+---------
 public | chunks                | table | raguser
 public | documents             | table | raguser
 public | flyway_schema_history | table | raguser
 public | test_embeddings       | table | raguser
```

### Step 4: Verify Vector Column

```bash
docker-compose exec db psql -U raguser -d ragdb -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'chunks' AND column_name = 'embedding';"
```

Expected output:
```
 column_name | data_type
-------------+-----------
 embedding   | USER-DEFINED
```

### Step 5: Test via REST API

**Initialize test data:**
```bash
curl -X POST http://localhost:8080/api/test/vector/init
```

Expected response:
```json
{
  "message": "Test data initialized successfully",
  "documentId": 1,
  "chunksCreated": 4,
  "chunks": [
    {
      "id": 1,
      "text": "Machine learning is a subset of artificial intelligence...",
      "chunkIndex": 0
    },
    ...
  ]
}
```

**Test vector similarity search:**
```bash
curl -X POST "http://localhost:8080/api/test/vector/search?limit=3"
```

Expected response:
```json
{
  "queryEmbedding": "[0.1, 0.2, ...]",
  "limit": 3,
  "resultsCount": 3,
  "results": [
    {
      "id": 2,
      "documentId": 1,
      "text": "Deep learning uses neural networks...",
      "chunkIndex": 1,
      "pageStart": 0,
      "pageEnd": 0
    },
    ...
  ]
}
```

**View all chunks:**
```bash
curl http://localhost:8080/api/test/vector/chunks
```

**Clear test data:**
```bash
curl -X DELETE http://localhost:8080/api/test/vector/clear
```

### Step 6: Test via SQL

Run the SQL test script:

```bash
docker-compose exec db psql -U raguser -d ragdb < infrastructure/test_vector_operations.sql
```

Or copy it into the container and run:

```bash
docker cp infrastructure/test_vector_operations.sql $(docker-compose ps -q db):/tmp/test.sql
docker-compose exec db psql -U raguser -d ragdb -f /tmp/test.sql
```

### Step 7: Manual Vector Query Test

Test a simple vector similarity search:

```bash
docker-compose exec db psql -U raguser -d ragdb
```

```sql
-- Insert a test chunk
INSERT INTO documents (title, filename) VALUES ('Test', 'test.pdf');

INSERT INTO chunks (document_id, text, page_start, page_end, chunk_index, embedding)
VALUES (
    1,
    'This is a test chunk',
    0, 0, 0,
    (SELECT ('['|| string_agg(((random() * 2 - 1)::numeric(10,8))::text, ',') ||']')::vector
     FROM generate_series(1, 384))
);

-- Query for similar chunks
SELECT id, text
FROM chunks
ORDER BY embedding <-> (SELECT embedding FROM chunks WHERE id = 1)
LIMIT 3;
```

## Verification Checklist

At the end of Phase 2, you should be able to confirm:

- [x] Flyway is configured and running migrations
- [x] `documents` table exists with correct schema
- [x] `chunks` table exists with correct schema
- [x] `embedding` column is of type `vector(384)`
- [x] HNSW index exists on the `embedding` column
- [x] Can insert documents and chunks via JPA
- [x] Can query similar chunks using vector similarity
- [x] Vector search returns results ordered by similarity
- [x] Foreign key relationship works (cascade delete)

## Key Concepts

### Embedding Dimension

The embedding dimension (384) is determined by the sentence-transformers model:
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Dimension: 384
- Configured in: `python-service/model_config.py`
- Must match: Database schema, JPA entities, test data

### Cosine Distance

The `<->` operator calculates cosine distance:
- Range: 0 to 2
- 0 = identical vectors (most similar)
- 2 = opposite vectors (least similar)
- Formula: `1 - cosine_similarity`

### HNSW Index

Hierarchical Navigable Small World (HNSW):
- Fast approximate nearest neighbor search
- Trade-off: Build time vs. query speed vs. recall
- Better than IVFFlat for most use cases
- Parameters tunable for performance

## Next Steps

With Phase 2 complete, you're ready for:

**Phase 3:** PDF Upload & Processing
- Implement PDF upload endpoint
- Extract text from PDFs
- Split text into chunks
- Generate embeddings for chunks

**Phase 4:** RAG Query Pipeline
- Implement query endpoint
- Vector similarity search
- Context aggregation
- LLM-based answer generation

## Troubleshooting

### Migrations Not Running

If Flyway migrations don't run:

```bash
# Check Flyway status
docker-compose logs java-service | grep -i flyway

# Check if migrations exist
docker-compose exec java-service ls -la /app/BOOT-INF/classes/db/migration/

# Force rebuild
docker-compose down -v
docker-compose up --build
```

### JPA Validation Errors

If you get JPA validation errors:

```bash
# Check table schema
docker-compose exec db psql -U raguser -d ragdb -c "\d chunks"

# Check if vector extension is loaded
docker-compose exec db psql -U raguser -d ragdb -c "SELECT * FROM pg_extension WHERE extname='vector';"
```

### Vector Query Performance

If vector queries are slow:

```bash
# Check if HNSW index exists
docker-compose exec db psql -U raguser -d ragdb -c "SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'chunks';"

# Verify index is being used
docker-compose exec db psql -U raguser -d ragdb -c "EXPLAIN SELECT * FROM chunks ORDER BY embedding <-> '[0.1, 0.2]'::vector(384) LIMIT 5;"
```

## Files Created/Modified in Phase 2

**New Files:**
- `java-service/src/main/resources/db/migration/V1__create_documents_table.sql`
- `java-service/src/main/resources/db/migration/V2__create_chunks_table.sql`
- `java-service/src/main/java/com/rag/app/model/Document.java`
- `java-service/src/main/java/com/rag/app/model/Chunk.java`
- `java-service/src/main/java/com/rag/app/repository/DocumentRepository.java`
- `java-service/src/main/java/com/rag/app/repository/ChunkRepository.java`
- `java-service/src/main/java/com/rag/app/controller/VectorTestController.java`
- `infrastructure/test_vector_operations.sql`
- `PHASE2_SCHEMA.md` (this file)

**Modified Files:**
- `java-service/pom.xml`: Added Flyway dependencies
- `java-service/src/main/resources/application.properties`: Configured Flyway

## Summary

Phase 2 successfully establishes:
1. **Database schema** for documents and chunks
2. **pgvector integration** with HNSW index for fast similarity search
3. **Flyway migrations** for version-controlled schema changes
4. **JPA entities and repositories** for type-safe database access
5. **Test endpoints** to verify vector operations work correctly

The system is now ready to ingest PDF documents and perform semantic search on their content.
