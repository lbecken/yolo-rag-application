# Phase 3: PDF Ingestion Service

## Overview

Phase 3 implements a complete PDF ingestion pipeline in the Python service that:
1. Accepts PDF uploads via HTTP
2. Extracts text from PDF pages
3. Chunks text into manageable pieces
4. Generates embeddings using sentence-transformers
5. Stores documents and chunks with embeddings in PostgreSQL

## Implementation

### New Files Created

1. **`python-service/pdf_utils.py`** - PDF text extraction and chunking
   - `extract_text_from_pdf()` - Extracts text per page using PyMuPDF
   - `chunk_text()` - Basic chunking with configurable max_chars and overlap
   - `chunk_text_smart()` - Advanced chunking that respects sentence boundaries
   - `extract_and_chunk_pdf()` - Convenience function for complete extraction

2. **`python-service/embeddings.py`** - Embedding generation service
   - `get_embedding_model()` - Lazy loads sentence-transformers model
   - `generate_embedding()` - Single text embedding
   - `generate_embeddings_batch()` - Batch embedding generation
   - `encode_chunks()` - Generate embeddings for chunk dictionaries

3. **`python-service/db.py`** - Database integration layer
   - SQLAlchemy ORM models for `Document` and `Chunk` tables
   - `create_document()` - Insert document record
   - `create_chunks()` - Insert chunk records with embeddings
   - `search_similar_chunks()` - Vector similarity search
   - `ingest_document_with_chunks()` - Complete ingestion transaction

### Updated Files

1. **`python-service/requirements.txt`**
   - Added `PyMuPDF==1.23.8` for PDF text extraction
   - Added `pgvector==0.2.4` for PostgreSQL vector operations

2. **`python-service/main.py`**
   - Added `POST /ingest` endpoint
   - Accepts multipart/form-data with PDF file and optional title
   - Orchestrates the complete ingestion pipeline
   - Returns document_id and num_chunks on success

## API Endpoints

### POST /ingest

Ingest a PDF document into the system.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Parameters:
  - `file` (required): PDF file to ingest
  - `title` (optional): Document title (defaults to filename)

**Response:**
```json
{
  "status": "success",
  "document_id": 1,
  "num_chunks": 25,
  "title": "example.pdf"
}
```

**Error Responses:**
- 400: Invalid file type (not a PDF) or no text extracted
- 500: Internal error during processing

## Configuration

### Chunking Parameters

Default settings in `main.py:132-135`:
- `max_chars`: 1500 characters per chunk
- `overlap`: 200 characters overlap between chunks
- `use_smart_chunking`: True (respects sentence boundaries)

To adjust, modify the parameters in the `/ingest` endpoint.

### Embedding Configuration

Settings from `model_config.py`:
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Dimensions: 384 (matches database schema)
- Batch size: 32 (configurable in `encode_chunks()`)

## Testing

### 1. Start Services

```bash
docker-compose up --build
```

Wait for services to be ready:
- Python service: http://localhost:8000
- PostgreSQL: localhost:5432

### 2. Create a Test PDF

You can use any PDF file or create a simple one for testing.

### 3. Test the Ingestion Endpoint

Using curl:
```bash
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@/path/to/your/test.pdf" \
  -F "title=My Test Document"
```

Using Python:
```python
import requests

url = "http://localhost:8000/ingest"
files = {"file": open("test.pdf", "rb")}
data = {"title": "My Test Document"}

response = requests.post(url, files=files, data=data)
print(response.json())
```

### 4. Verify Database Records

Check documents table:
```bash
docker-compose exec db psql -U raguser -d ragdb -c "SELECT * FROM documents;"
```

Check chunks table:
```bash
docker-compose exec db psql -U raguser -d ragdb -c "SELECT id, document_id, chunk_index, page_start, page_end, substring(content, 1, 50) as content_preview FROM chunks LIMIT 5;"
```

Verify embeddings are populated:
```bash
docker-compose exec db psql -U raguser -d ragdb -c "SELECT id, document_id, array_length(embedding, 1) as embedding_dim FROM chunks LIMIT 5;"
```

Expected output: `embedding_dim` should be 384.

### 5. Check Service Logs

```bash
docker-compose logs -f python-service
```

Look for log messages like:
- "Extracting text from PDF"
- "Created N chunks from M pages"
- "Generating embeddings for N texts"
- "Successfully ingested document X with Y chunks"

## Architecture

### Ingestion Flow

```
User → POST /ingest
  ↓
  1. Save uploaded PDF to temp file
  ↓
  2. Extract text per page (PyMuPDF)
  ↓
  3. Chunk pages into ~1500 char pieces
  ↓
  4. Generate embeddings (sentence-transformers)
  ↓
  5. Insert document record
  ↓
  6. Insert chunk records with embeddings
  ↓
  7. Return document_id and num_chunks
```

### Database Transaction

The `ingest_document_with_chunks()` function wraps the entire operation in a single database transaction:
- If any step fails, the entire operation is rolled back
- No partial data is left in the database
- Ensures data consistency

## Chunking Strategy

### Basic Chunking (`chunk_text`)

- Splits text at fixed character positions
- Simple and predictable
- May split sentences mid-word

### Smart Chunking (`chunk_text_smart`)

- Attempts to split at sentence boundaries (periods)
- More natural chunk boundaries
- Better semantic coherence
- Default strategy used in `/ingest`

### Parameters

- **max_chars (1500)**: Balances context size vs. precision
  - Too small: Loss of context
  - Too large: Less precise retrieval

- **overlap (200)**: Prevents information loss at boundaries
  - Ensures continuous concepts aren't split
  - 200 chars ≈ 1-2 sentences

## Error Handling

The `/ingest` endpoint includes comprehensive error handling:

1. **File Validation**: Ensures uploaded file is a PDF
2. **Empty PDF**: Returns 400 if no text can be extracted
3. **Database Errors**: Rolls back transaction, returns 500
4. **Cleanup**: Always removes temporary files

## Performance Considerations

### Embedding Generation

- Uses batch processing (batch_size=32) for efficiency
- Sentence-transformers shows progress bar in logs
- For large PDFs (100+ pages), expect 1-2 minutes

### Database Operations

- Uses bulk insert with SQLAlchemy for chunks
- Single transaction for document + all chunks
- HNSW index enables fast vector search later

## Next Steps (Phase 4+)

With Phase 3 complete, you can now:
- Ingest multiple PDFs into the system
- Query the database for documents and chunks
- Implement the RAG query endpoint (retrieval + generation)
- Build a web UI for document upload

## Troubleshooting

### "No text could be extracted from PDF"

- PDF might be image-based (scanned). Consider adding OCR support.
- PDF might be encrypted or corrupted.

### "Database connection failed"

- Ensure PostgreSQL is running: `docker-compose ps db`
- Check environment variables in `.env` or `docker-compose.yml`
- Verify Flyway migrations ran successfully

### "Embedding dimension mismatch"

- Ensure `EMBEDDING_DIMENSION` in `model_config.py` matches database schema (384)
- Check `infrastructure/init-db.sql` and Flyway migrations

### PyMuPDF import error

- Rebuild the Python service: `docker-compose build python-service`
- Verify `PyMuPDF==1.23.8` is in `requirements.txt`

## Example Test Results

After successful ingestion, you should see:

**Documents table:**
```
 id |      title      |  file_path   |   upload_timestamp    | total_chunks
----+-----------------+--------------+-----------------------+--------------
  1 | test.pdf        | test.pdf     | 2024-01-15 10:30:00   |           25
```

**Chunks table:**
```
 id | document_id | chunk_index | page_start | page_end | embedding_dim
----+-------------+-------------+------------+----------+---------------
  1 |           1 |           0 |          0 |        0 |           384
  2 |           1 |           1 |          0 |        0 |           384
  3 |           1 |           2 |          1 |        1 |           384
```

## References

- PyMuPDF documentation: https://pymupdf.readthedocs.io/
- Sentence-transformers: https://www.sbert.net/
- pgvector: https://github.com/pgvector/pgvector
- SQLAlchemy: https://docs.sqlalchemy.org/
