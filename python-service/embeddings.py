"""
Embedding Generation Service
Handles text embedding using sentence-transformers
"""

from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np
import logging
from model_config import EMBEDDING_MODEL_NAME, EMBEDDING_DIMENSION

logger = logging.getLogger(__name__)

# Global model instance (lazy loaded)
_embedding_model = None


def get_embedding_model() -> SentenceTransformer:
    """
    Get or initialize the embedding model.
    Uses lazy loading to avoid loading model on import.

    Returns:
        SentenceTransformer model instance
    """
    global _embedding_model

    if _embedding_model is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        logger.info(f"Embedding model loaded successfully. Dimension: {EMBEDDING_DIMENSION}")

    return _embedding_model


def generate_embedding(text: str) -> np.ndarray:
    """
    Generate embedding for a single text string.

    Args:
        text: Input text to embed

    Returns:
        Numpy array of shape (EMBEDDING_DIMENSION,)
    """
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding


def generate_embeddings_batch(texts: List[str], batch_size: int = 32) -> np.ndarray:
    """
    Generate embeddings for a batch of texts.

    Args:
        texts: List of input texts to embed
        batch_size: Number of texts to process at once (default: 32)

    Returns:
        Numpy array of shape (len(texts), EMBEDDING_DIMENSION)
    """
    model = get_embedding_model()
    logger.info(f"Generating embeddings for {len(texts)} texts in batches of {batch_size}")

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    logger.info(f"Generated {len(embeddings)} embeddings with dimension {embeddings.shape[1]}")
    return embeddings


def encode_chunks(chunks: List[Dict[str, any]], batch_size: int = 32) -> np.ndarray:
    """
    Generate embeddings for a list of chunk dictionaries.

    Args:
        chunks: List of chunk dicts (must have 'text' key)
        batch_size: Number of chunks to process at once

    Returns:
        Numpy array of shape (len(chunks), EMBEDDING_DIMENSION)
    """
    if not chunks:
        logger.warning("No chunks provided for encoding")
        return np.array([])

    texts = [chunk["text"] for chunk in chunks]
    logger.info(f"Encoding {len(texts)} chunks")

    embeddings = generate_embeddings_batch(texts, batch_size=batch_size)

    return embeddings


def verify_embedding_dimension(embedding: np.ndarray) -> bool:
    """
    Verify that an embedding has the expected dimension.

    Args:
        embedding: The embedding array to check

    Returns:
        True if dimension matches config, False otherwise
    """
    if len(embedding.shape) == 1:
        actual_dim = embedding.shape[0]
    else:
        actual_dim = embedding.shape[1]

    if actual_dim != EMBEDDING_DIMENSION:
        logger.error(
            f"Embedding dimension mismatch! Expected {EMBEDDING_DIMENSION}, got {actual_dim}"
        )
        return False

    return True
