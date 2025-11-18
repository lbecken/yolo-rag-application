"""
PDF Processing Utilities
Handles PDF text extraction and text chunking
"""

import fitz  # PyMuPDF
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> List[str]:
    """
    Extract text from a PDF file, one entry per page.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        List of strings, one per page

    Raises:
        Exception: If PDF cannot be read or processed
    """
    try:
        logger.info(f"Extracting text from PDF: {pdf_path}")
        doc = fitz.open(pdf_path)
        pages = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            pages.append(text)
            logger.debug(f"Extracted {len(text)} characters from page {page_num + 1}")

        doc.close()
        logger.info(f"Successfully extracted {len(pages)} pages from PDF")
        return pages

    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise


def chunk_text(
    pages: List[str],
    max_chars: int = 1500,
    overlap: int = 200
) -> List[Dict[str, any]]:
    """
    Chunk text from pages into smaller pieces with overlap.

    Args:
        pages: List of text strings, one per page
        max_chars: Maximum characters per chunk (default: 1500)
        overlap: Number of characters to overlap between chunks (default: 200)

    Returns:
        List of chunk dictionaries with keys:
            - text: The chunk text
            - page_start: Starting page number (0-indexed)
            - page_end: Ending page number (0-indexed)
            - chunk_index: Sequential chunk index
    """
    logger.info(f"Chunking {len(pages)} pages with max_chars={max_chars}, overlap={overlap}")

    chunks = []
    chunk_index = 0

    for page_num, page_text in enumerate(pages):
        # Skip empty pages
        if not page_text.strip():
            logger.debug(f"Skipping empty page {page_num}")
            continue

        # If page is smaller than max_chars, treat it as a single chunk
        if len(page_text) <= max_chars:
            chunks.append({
                "text": page_text.strip(),
                "page_start": page_num,
                "page_end": page_num,
                "chunk_index": chunk_index
            })
            chunk_index += 1
            logger.debug(f"Page {page_num} fits in single chunk")
            continue

        # Split page into chunks with overlap
        start = 0
        while start < len(page_text):
            end = start + max_chars
            chunk_text = page_text[start:end]

            # Only add non-empty chunks
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text.strip(),
                    "page_start": page_num,
                    "page_end": page_num,
                    "chunk_index": chunk_index
                })
                chunk_index += 1

            # Move start forward, accounting for overlap
            start = end - overlap

            # Prevent infinite loop if overlap >= max_chars
            if overlap >= max_chars:
                start = end

    logger.info(f"Created {len(chunks)} chunks from {len(pages)} pages")
    return chunks


def chunk_text_smart(
    pages: List[str],
    max_chars: int = 1500,
    overlap: int = 200
) -> List[Dict[str, any]]:
    """
    Advanced chunking that tries to split on sentence boundaries.

    This version attempts to create chunks at natural break points (periods, newlines)
    rather than arbitrary character positions.

    Args:
        pages: List of text strings, one per page
        max_chars: Maximum characters per chunk
        overlap: Number of characters to overlap between chunks

    Returns:
        List of chunk dictionaries with same format as chunk_text()
    """
    logger.info(f"Smart chunking {len(pages)} pages with max_chars={max_chars}, overlap={overlap}")

    chunks = []
    chunk_index = 0

    for page_num, page_text in enumerate(pages):
        # Skip empty pages
        if not page_text.strip():
            continue

        # If page is smaller than max_chars, treat it as a single chunk
        if len(page_text) <= max_chars:
            chunks.append({
                "text": page_text.strip(),
                "page_start": page_num,
                "page_end": page_num,
                "chunk_index": chunk_index
            })
            chunk_index += 1
            continue

        # Smart chunking: try to split on sentence boundaries
        sentences = page_text.replace('\n', ' ').split('. ')
        current_chunk = ""

        for sentence in sentences:
            # Add period back (except for last sentence which might not have one)
            sentence = sentence.strip()
            if sentence and not sentence.endswith('.'):
                sentence += '.'

            # Check if adding this sentence would exceed max_chars
            if len(current_chunk) + len(sentence) + 1 > max_chars and current_chunk:
                # Save current chunk
                chunks.append({
                    "text": current_chunk.strip(),
                    "page_start": page_num,
                    "page_end": page_num,
                    "chunk_index": chunk_index
                })
                chunk_index += 1

                # Start new chunk with overlap
                # Take last 'overlap' characters from current chunk
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
            else:
                # Add sentence to current chunk
                current_chunk += (" " + sentence) if current_chunk else sentence

        # Don't forget the last chunk
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "page_start": page_num,
                "page_end": page_num,
                "chunk_index": chunk_index
            })
            chunk_index += 1

    logger.info(f"Smart chunking created {len(chunks)} chunks from {len(pages)} pages")
    return chunks


def extract_and_chunk_pdf(
    pdf_path: str,
    max_chars: int = 1500,
    overlap: int = 200,
    use_smart_chunking: bool = True
) -> List[Dict[str, any]]:
    """
    Convenience function to extract and chunk a PDF in one call.

    Args:
        pdf_path: Path to the PDF file
        max_chars: Maximum characters per chunk
        overlap: Number of characters to overlap between chunks
        use_smart_chunking: If True, use smart chunking (sentence boundaries)

    Returns:
        List of chunk dictionaries
    """
    pages = extract_text_from_pdf(pdf_path)

    if use_smart_chunking:
        return chunk_text_smart(pages, max_chars, overlap)
    else:
        return chunk_text(pages, max_chars, overlap)
