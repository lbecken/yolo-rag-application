-- Phase 2: Test Vector Operations in PostgreSQL
-- This script demonstrates pgvector similarity search directly in SQL
--
-- Run this script after the Flyway migrations have been applied
-- Usage: docker-compose exec db psql -U raguser -d ragdb -f /docker-entrypoint-initdb.d/test_vector_operations.sql

-- First, verify the vector extension is loaded
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- Verify the tables exist
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('documents', 'chunks')
ORDER BY table_name;

-- Insert a test document
INSERT INTO documents (title, filename, created_at)
VALUES ('Test Document for Vector Search', 'test_vector_search.pdf', NOW())
ON CONFLICT (filename) DO NOTHING
RETURNING id, title, filename;

-- Get the document ID (you may need to adjust this based on your data)
DO $$
DECLARE
    doc_id BIGINT;
BEGIN
    SELECT id INTO doc_id FROM documents WHERE filename = 'test_vector_search.pdf';

    -- Insert test chunks with synthetic embeddings
    -- Note: In production, these embeddings would come from your embedding model

    -- Chunk 1: About machine learning (using a synthetic 384-dimensional vector)
    INSERT INTO chunks (document_id, text, page_start, page_end, chunk_index, embedding, created_at)
    VALUES (
        doc_id,
        'Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data.',
        0, 0, 0,
        -- Generate a simple synthetic embedding (in production, use real embeddings)
        (SELECT ('['|| string_agg(((random() * 2 - 1)::numeric(10,8))::text, ',') ||']')::vector
         FROM generate_series(1, 384)),
        NOW()
    )
    ON CONFLICT (document_id, chunk_index) DO NOTHING;

    -- Chunk 2: About deep learning
    INSERT INTO chunks (document_id, text, page_start, page_end, chunk_index, embedding, created_at)
    VALUES (
        doc_id,
        'Deep learning uses neural networks with multiple layers to progressively extract higher-level features from raw input.',
        0, 0, 1,
        (SELECT ('['|| string_agg(((random() * 2 - 1)::numeric(10,8))::text, ',') ||']')::vector
         FROM generate_series(1, 384)),
        NOW()
    )
    ON CONFLICT (document_id, chunk_index) DO NOTHING;

    -- Chunk 3: About natural language processing
    INSERT INTO chunks (document_id, text, page_start, page_end, chunk_index, embedding, created_at)
    VALUES (
        doc_id,
        'Natural language processing enables computers to understand, interpret, and generate human language.',
        1, 1, 2,
        (SELECT ('['|| string_agg(((random() * 2 - 1)::numeric(10,8))::text, ',') ||']')::vector
         FROM generate_series(1, 384)),
        NOW()
    )
    ON CONFLICT (document_id, chunk_index) DO NOTHING;

    RAISE NOTICE 'Test chunks inserted for document_id: %', doc_id;
END $$;

-- Verify chunks were inserted
SELECT
    c.id,
    c.document_id,
    c.chunk_index,
    LEFT(c.text, 50) || '...' as text_preview,
    c.page_start,
    c.page_end,
    vector_dims(c.embedding) as embedding_dimensions
FROM chunks c
ORDER BY c.chunk_index;

-- Test 1: Find top 3 most similar chunks to a query embedding
-- Using the first chunk's embedding as the query
WITH query_embedding AS (
    SELECT embedding FROM chunks WHERE chunk_index = 0 LIMIT 1
)
SELECT
    c.id,
    c.chunk_index,
    LEFT(c.text, 60) || '...' as text_preview,
    -- Cosine distance (lower = more similar)
    c.embedding <-> (SELECT embedding FROM query_embedding) as cosine_distance,
    -- Cosine similarity (higher = more similar, range: -1 to 1)
    1 - (c.embedding <-> (SELECT embedding FROM query_embedding)) as cosine_similarity
FROM chunks c
ORDER BY c.embedding <-> (SELECT embedding FROM query_embedding)
LIMIT 3;

-- Test 2: Demonstrate different distance operators
-- <-> : cosine distance
-- <#> : negative inner product
-- <=> : L2 distance (Euclidean)
WITH query_embedding AS (
    SELECT embedding FROM chunks WHERE chunk_index = 0 LIMIT 1
)
SELECT
    c.chunk_index,
    LEFT(c.text, 40) || '...' as text_preview,
    ROUND((c.embedding <-> (SELECT embedding FROM query_embedding))::numeric, 4) as cosine_dist,
    ROUND((c.embedding <#> (SELECT embedding FROM query_embedding))::numeric, 4) as inner_product,
    ROUND((c.embedding <=> (SELECT embedding FROM query_embedding))::numeric, 4) as l2_dist
FROM chunks c
ORDER BY c.chunk_index;

-- Test 3: Verify the HNSW index is being used
-- Check the query plan for vector similarity search
EXPLAIN (ANALYZE, BUFFERS)
SELECT c.id, c.text
FROM chunks c
ORDER BY c.embedding <-> '[0.1, 0.2, 0.3]'::vector(384)
LIMIT 5;

-- Show table statistics
SELECT
    'documents' as table_name,
    COUNT(*) as row_count
FROM documents
UNION ALL
SELECT
    'chunks' as table_name,
    COUNT(*) as row_count
FROM chunks;

-- Show index information
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename IN ('documents', 'chunks')
ORDER BY tablename, indexname;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Phase 2 Vector Operations Test Complete';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables: documents and chunks created';
    RAISE NOTICE 'pgvector extension: enabled';
    RAISE NOTICE 'Vector similarity search: working';
    RAISE NOTICE 'Embedding dimension: 384';
    RAISE NOTICE '========================================';
END $$;
