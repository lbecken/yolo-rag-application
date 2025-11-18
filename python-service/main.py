"""
PDF Ingestion and Embedding Service
Handles PDF upload, text extraction, chunking, and embedding generation
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
import os
import tempfile
import shutil

# Import our modules
from pdf_utils import extract_and_chunk_pdf
from embeddings import encode_chunks, generate_embedding
from db import ingest_document_with_chunks, test_connection, search_similar_chunks, get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG PDF Ingestion Service",
    description="Service for PDF ingestion, text extraction, and embedding generation",
    version="0.1.0"
)

# Add CORS middleware to allow Java service to call this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class IngestResponse(BaseModel):
    status: str
    document_id: int
    num_chunks: int
    title: str

class ChunkResult(BaseModel):
    chunk_id: int
    document_id: int
    chunk_index: int
    page_start: Optional[int]
    page_end: Optional[int]
    text: str
    distance: float 
 
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    document_id: Optional[int] = None
 
 
class QueryResponse(BaseModel):
    query: str
    num_results: int
    results: List[ChunkResult]

# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RAG PDF Ingestion Service",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    return HealthResponse(
        status="healthy",
        service="python-ingestion-service",
        version="0.1.0"
    )


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting PDF Ingestion Service...")

    # Test database connection
    if test_connection():
        logger.info("Database connection verified")
    else:
        logger.warning("Database connection failed - some features may not work")

    logger.info("Service ready to accept requests")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down PDF Ingestion Service...")


@app.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None)
):
    """
    Ingest a PDF document: extract text, chunk it, generate embeddings, and store in database.

    Args:
        file: PDF file to ingest (multipart/form-data)
        title: Optional document title (defaults to filename)

    Returns:
        IngestResponse with status, document_id, num_chunks, and title
    """
    logger.info(f"Received ingest request for file: {file.filename}")

    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    # Use filename as title if not provided
    doc_title = title if title else file.filename

    # Create a temporary file to save the upload
    temp_file = None
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
            logger.info(f"Saved upload to temporary file: {temp_path}")

        # Step 1: Extract and chunk PDF
        logger.info("Step 1: Extracting text and chunking PDF...")
        chunks = extract_and_chunk_pdf(
            pdf_path=temp_path,
            max_chars=1500,
            overlap=200,
            use_smart_chunking=True
        )

        if not chunks:
            raise HTTPException(status_code=400, detail="No text could be extracted from PDF")

        logger.info(f"Extracted {len(chunks)} chunks from PDF")

        # Step 2: Generate embeddings
        logger.info("Step 2: Generating embeddings...")
        embeddings = encode_chunks(chunks, batch_size=32)
        logger.info(f"Generated {len(embeddings)} embeddings")

        # Step 3: Store in database
        logger.info("Step 3: Storing document and chunks in database...")
        result = ingest_document_with_chunks(
            title=doc_title,
            chunks=chunks,
            embeddings=embeddings,
            filename=file.filename  # Store original filename
        )

        logger.info(f"Successfully ingested document {result['document_id']}")

        return IngestResponse(
            status=result["status"],
            document_id=result["document_id"],
            num_chunks=result["num_chunks"],
            title=doc_title
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_path):
            os.unlink(temp_path)
            logger.debug(f"Cleaned up temporary file: {temp_path}")


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query documents using semantic search.
 
    Args:
        request: QueryRequest with query text, top_k, and optional document_id
 
    Returns:
        QueryResponse with matching chunks and distances
    """
    logger.info(f"Received query: '{request.query}' (top_k={request.top_k})")
 
    try:
        # Step 1: Generate embedding for query
        logger.info("Generating query embedding...")
        query_embedding = generate_embedding(request.query)
        logger.info(f"Query embedded (dimension: {len(query_embedding)})")
 
        # Step 2: Search for similar chunks
        db = get_db()
        try:
            results = search_similar_chunks(db, query_embedding, limit=request.top_k * 2)
 
            # Filter by document_id if specified
            if request.document_id:
                results = [(chunk, dist) for chunk, dist in results if chunk.document_id == request.document_id]
                results = results[:request.top_k]
                logger.info(f"Filtered to document {request.document_id}: {len(results)} results")
            else:
                results = results[:request.top_k]
 
            # Convert to response format
            chunk_results = [
                ChunkResult(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    chunk_index=chunk.chunk_index,
                    page_start=chunk.page_start,
                    page_end=chunk.page_end,
                    text=chunk.text,
                    distance=float(distance)
                )
                for chunk, distance in results
            ]
 
            logger.info(f"Returning {len(chunk_results)} results")
 
            return QueryResponse(
                query=request.query,
                num_results=len(chunk_results),
                results=chunk_results
            )
 
        finally:
            db.close()
 
    except Exception as e:
        logger.error(f"Error during query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
