-- Phase 2: Create documents table
-- This table stores metadata about uploaded PDF documents

-- Ensure pgvector extension is available
CREATE EXTENSION IF NOT EXISTS vector;

-- Create documents table
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    filename VARCHAR(500) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Add index for common queries
    CONSTRAINT unique_filename UNIQUE (filename)
);

-- Create index on created_at for sorting
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);

-- Add comment for documentation
COMMENT ON TABLE documents IS 'Stores metadata for uploaded PDF documents';
COMMENT ON COLUMN documents.id IS 'Primary key';
COMMENT ON COLUMN documents.title IS 'Human-readable title of the document';
COMMENT ON COLUMN documents.filename IS 'Original filename of the uploaded PDF';
COMMENT ON COLUMN documents.created_at IS 'Timestamp when the document was uploaded';
