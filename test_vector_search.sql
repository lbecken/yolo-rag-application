-- Test Vector Similarity Search
-- This script demonstrates how to query chunks using vector similarity
 
-- 1. View all documents
SELECT id, title, total_chunks, upload_timestamp
FROM documents
ORDER BY upload_timestamp DESC;
 
-- 2. View sample chunks from a document (replace document_id with your actual ID)
SELECT
    id,
    document_id,
    chunk_index,
    page_start,
    substring(content, 1, 100) as content_preview
FROM chunks
WHERE document_id = 1  -- Change this to your document ID
ORDER BY chunk_index
LIMIT 5;
 
-- 3. Get a sample embedding vector to test search
-- This gets the embedding from the first chunk
WITH sample_vector AS (
    SELECT embedding
    FROM chunks
    WHERE document_id = 1  -- Change this to your document ID
    LIMIT 1
)
-- 4. Find similar chunks using L2 distance (vector similarity)
SELECT
    c.id,
    c.document_id,
    c.chunk_index,
    substring(c.content, 1, 150) as content_preview,
    c.embedding <-> (SELECT embedding FROM sample_vector) as distance
FROM chunks c
ORDER BY c.embedding <-> (SELECT embedding FROM sample_vector)
LIMIT 5;
 
-- 5. Find similar chunks using cosine distance (alternative similarity metric)
WITH sample_vector AS (
    SELECT embedding
    FROM chunks
    WHERE document_id = 1
    LIMIT 1
)
SELECT
    c.id,
    c.document_id,
    c.chunk_index,
    substring(c.content, 1, 150) as content_preview,
    1 - (c.embedding <=> (SELECT embedding FROM sample_vector)) as cosine_similarity
FROM chunks c
ORDER BY c.embedding <=> (SELECT embedding FROM sample_vector)
LIMIT 5; 