-- Initialize RAG database with pgvector extension

-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a simple test table to verify pgvector is working
--CREATE TABLE IF NOT EXISTS test_embeddings (
--    id SERIAL PRIMARY KEY,
--    content TEXT,
--    embedding vector(384)
--);

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialized successfully with pgvector extension';
END $$;
