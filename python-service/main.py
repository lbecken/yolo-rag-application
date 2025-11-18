"""
PDF Ingestion and Embedding Service
Handles PDF upload, text extraction, chunking, and embedding generation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging

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
    logger.info("Service ready to accept requests")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down PDF Ingestion Service...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
