-- Phase 2: Create chunks table with pgvector support
-- This table stores document chunks with their embeddings for semantic search

CREATE TABLE chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT NOT NULL,
    text TEXT NOT NULL,
    page_start INTEGER NOT NULL,
    page_end INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding vector(384) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraint
    CONSTRAINT fk_chunks_document FOREIGN KEY (document_id)
        REFERENCES documents(id) ON DELETE CASCADE,

    -- Ensure unique chunk index per document
    CONSTRAINT unique_chunk_per_document UNIQUE (document_id, chunk_index)
);

-- Create index on document_id for fast lookups
CREATE INDEX idx_chunks_document_id ON chunks(document_id);

-- Create index on chunk_index for ordering
CREATE INDEX idx_chunks_chunk_index ON chunks(chunk_index);

-- Create HNSW index for fast vector similarity search
-- Using cosine distance (most common for embeddings)
-- m=16: number of connections per layer (default)
-- ef_construction=64: size of dynamic candidate list for construction (default)
CREATE INDEX idx_chunks_embedding_hnsw ON chunks
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Alternative: IVFFlat index (faster build, slower query)
-- Uncomment if you prefer IVFFlat over HNSW
-- CREATE INDEX idx_chunks_embedding_ivfflat ON chunks
--     USING ivfflat (embedding vector_cosine_ops)
--     WITH (lists = 100);

-- Add comments for documentation
COMMENT ON TABLE chunks IS 'Stores document chunks with embeddings for semantic search';
COMMENT ON COLUMN chunks.id IS 'Primary key';
COMMENT ON COLUMN chunks.document_id IS 'Foreign key to documents table';
COMMENT ON COLUMN chunks.text IS 'The actual text content of the chunk';
COMMENT ON COLUMN chunks.page_start IS 'Starting page number of this chunk (0-indexed)';
COMMENT ON COLUMN chunks.page_end IS 'Ending page number of this chunk (0-indexed)';
COMMENT ON COLUMN chunks.chunk_index IS 'Sequential index of chunk within the document (0-indexed)';
COMMENT ON COLUMN chunks.embedding IS '384-dimensional embedding vector from sentence-transformers/all-MiniLM-L6-v2';
COMMENT ON COLUMN chunks.created_at IS 'Timestamp when the chunk was created';
