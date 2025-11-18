"""
Database Integration Layer
Handles PostgreSQL connections and operations using SQLAlchemy
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import ARRAY
from pgvector.sqlalchemy import Vector
from datetime import datetime
from typing import List, Dict, Optional
import numpy as np
import logging

from model_config import EMBEDDING_DIMENSION

logger = logging.getLogger(__name__)

# Database configuration from environment variables
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ragdb")
DB_USER = os.getenv("DB_USER", "raguser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "ragpass")

# Create SQLAlchemy engine
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()


# ============================================================================
# ORM Models
# ============================================================================

class Document(Base):
    """Document table ORM model"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    file_path = Column(String(1000))
    upload_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    total_chunks = Column(Integer, default=0)


class Chunk(Base):
    """Chunk table ORM model"""
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    page_start = Column(Integer)
    page_end = Column(Integer)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIMENSION))


# ============================================================================
# Database Helper Functions
# ============================================================================

def get_db() -> Session:
    """
    Get a database session.

    Returns:
        SQLAlchemy session

    Usage:
        db = get_db()
        try:
            # do database operations
            db.commit()
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
    """
    return SessionLocal()


def init_db():
    """
    Initialize database tables.
    Note: In production, this is handled by Flyway migrations.
    This is here for reference/testing only.
    """
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")


def test_connection() -> bool:
    """
    Test database connection.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        db = get_db()
        db.execute("SELECT 1")
        db.close()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False


# ============================================================================
# Document Operations
# ============================================================================

def create_document(
    db: Session,
    title: str,
    file_path: Optional[str] = None,
    total_chunks: int = 0
) -> Document:
    """
    Create a new document record.

    Args:
        db: Database session
        title: Document title
        file_path: Optional path to saved PDF file
        total_chunks: Number of chunks for this document

    Returns:
        Created Document object with ID populated
    """
    doc = Document(
        title=title,
        file_path=file_path,
        upload_timestamp=datetime.utcnow(),
        total_chunks=total_chunks
    )
    db.add(doc)
    db.flush()  # This populates doc.id without committing
    logger.info(f"Created document: {doc.id} - {title}")
    return doc


def get_document_by_id(db: Session, doc_id: int) -> Optional[Document]:
    """
    Retrieve a document by ID.

    Args:
        db: Database session
        doc_id: Document ID

    Returns:
        Document object or None if not found
    """
    return db.query(Document).filter(Document.id == doc_id).first()


def get_all_documents(db: Session, limit: int = 100) -> List[Document]:
    """
    Retrieve all documents.

    Args:
        db: Database session
        limit: Maximum number of documents to return

    Returns:
        List of Document objects
    """
    return db.query(Document).order_by(Document.upload_timestamp.desc()).limit(limit).all()


# ============================================================================
# Chunk Operations
# ============================================================================

def create_chunks(
    db: Session,
    document_id: int,
    chunks: List[Dict[str, any]],
    embeddings: np.ndarray
) -> List[Chunk]:
    """
    Create multiple chunk records with embeddings.

    Args:
        db: Database session
        document_id: ID of the parent document
        chunks: List of chunk dictionaries with keys: text, page_start, page_end, chunk_index
        embeddings: Numpy array of shape (len(chunks), EMBEDDING_DIMENSION)

    Returns:
        List of created Chunk objects
    """
    if len(chunks) != len(embeddings):
        raise ValueError(
            f"Number of chunks ({len(chunks)}) must match number of embeddings ({len(embeddings)})"
        )

    created_chunks = []

    for i, chunk_data in enumerate(chunks):
        # Convert numpy array to list for pgvector
        embedding_list = embeddings[i].tolist()

        chunk = Chunk(
            document_id=document_id,
            chunk_index=chunk_data["chunk_index"],
            page_start=chunk_data.get("page_start"),
            page_end=chunk_data.get("page_end"),
            content=chunk_data["text"],
            embedding=embedding_list
        )
        db.add(chunk)
        created_chunks.append(chunk)

    db.flush()
    logger.info(f"Created {len(created_chunks)} chunks for document {document_id}")
    return created_chunks


def get_chunks_by_document(db: Session, document_id: int) -> List[Chunk]:
    """
    Retrieve all chunks for a document.

    Args:
        db: Database session
        document_id: Document ID

    Returns:
        List of Chunk objects
    """
    return db.query(Chunk).filter(Chunk.document_id == document_id).order_by(Chunk.chunk_index).all()


def search_similar_chunks(
    db: Session,
    query_embedding: np.ndarray,
    limit: int = 5
) -> List[tuple]:
    """
    Search for similar chunks using vector similarity.

    Args:
        db: Database session
        query_embedding: Query embedding vector
        limit: Maximum number of results to return

    Returns:
        List of tuples (Chunk, distance)
    """
    # Convert numpy array to list for pgvector
    embedding_list = query_embedding.tolist()

    # Use L2 distance for similarity search
    results = db.query(
        Chunk,
        Chunk.embedding.l2_distance(embedding_list).label("distance")
    ).order_by("distance").limit(limit).all()

    logger.info(f"Found {len(results)} similar chunks")
    return results


# ============================================================================
# Combined Operations
# ============================================================================

def ingest_document_with_chunks(
    title: str,
    chunks: List[Dict[str, any]],
    embeddings: np.ndarray,
    file_path: Optional[str] = None
) -> Dict[str, any]:
    """
    Complete document ingestion: create document and all chunks in a single transaction.

    Args:
        title: Document title
        chunks: List of chunk dictionaries
        embeddings: Numpy array of embeddings
        file_path: Optional path to saved PDF

    Returns:
        Dictionary with keys: document_id, num_chunks, status
    """
    db = get_db()

    try:
        # Create document
        doc = create_document(
            db=db,
            title=title,
            file_path=file_path,
            total_chunks=len(chunks)
        )

        # Create chunks
        create_chunks(
            db=db,
            document_id=doc.id,
            chunks=chunks,
            embeddings=embeddings
        )

        # Commit transaction
        db.commit()

        logger.info(f"Successfully ingested document {doc.id} with {len(chunks)} chunks")

        return {
            "status": "success",
            "document_id": doc.id,
            "num_chunks": len(chunks)
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error ingesting document: {str(e)}")
        raise

    finally:
        db.close()
