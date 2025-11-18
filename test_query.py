#!/usr/bin/env python3
"""
Test Semantic Search on Ingested Documents
This script allows you to query ingested PDFs using natural language
"""
 
import sys
import os
 
# Add python-service to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python-service'))
 
from embeddings import generate_embedding
from db import get_db, search_similar_chunks, get_all_documents, Chunk
import numpy as np
 
 
def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")
 
 
def list_documents():
    """List all documents in the database"""
    print_section("Available Documents")
 
    db = get_db()
    try:
        documents = get_all_documents(db, limit=100)
 
        if not documents:
            print("No documents found. Please ingest a PDF first using:")
            print("  curl -X POST http://localhost:8000/ingest -F 'file=@document.pdf'")
            return False
 
        print(f"Found {len(documents)} document(s):\n")
        for doc in documents:
            print(f"  ID: {doc.id}")
            print(f"  Title: {doc.title}")
            print(f"  Filename: {doc.filename}")
            print(f"  Created: {doc.created_at}")
            print()
 
        return True
 
    finally:
        db.close()
 
 
def semantic_search(query: str, top_k: int = 5):
    """
    Perform semantic search on all chunks
 
    Args:
        query: Natural language query
        top_k: Number of results to return
    """
    print_section(f"Searching for: '{query}'")
 
    # Step 1: Generate embedding for the query
    print("Generating query embedding...")
    query_embedding = generate_embedding(query)
    print(f"✓ Query embedded (dimension: {len(query_embedding)})")
 
    # Step 2: Search for similar chunks
    print(f"\nSearching for top {top_k} similar chunks...")
    db = get_db()
 
    try:
        results = search_similar_chunks(db, query_embedding, limit=top_k)
 
        if not results:
            print("No results found.")
            return
 
        print(f"\n✓ Found {len(results)} results:\n")
 
        # Display results
        for i, (chunk, distance) in enumerate(results, 1):
            print(f"--- Result {i} (Distance: {distance:.4f}) ---")
            print(f"Document ID: {chunk.document_id}")
            print(f"Chunk Index: {chunk.chunk_index}")
            print(f"Pages: {chunk.page_start}-{chunk.page_end}")
            print(f"\nContent:")
            print(f"{chunk.text[:500]}...")  # First 500 chars
            print()
 
        return results
 
    finally:
        db.close()
 
 
def search_in_document(query: str, document_id: int, top_k: int = 5):
    """
    Search within a specific document
 
    Args:
        query: Natural language query
        document_id: ID of the document to search in
        top_k: Number of results to return
    """
    print_section(f"Searching in Document {document_id} for: '{query}'")
 
    # Generate query embedding
    print("Generating query embedding...")
    query_embedding = generate_embedding(query)
 
    # Search chunks
    db = get_db()
 
    try:
        # Search and filter by document_id
        all_results = search_similar_chunks(db, query_embedding, limit=50)
 
        # Filter for specific document
        results = [(chunk, dist) for chunk, dist in all_results if chunk.document_id == document_id]
        results = results[:top_k]
 
        if not results:
            print(f"No results found in document {document_id}.")
            return
 
        print(f"\n✓ Found {len(results)} results:\n")
 
        for i, (chunk, distance) in enumerate(results, 1):
            print(f"--- Result {i} (Distance: {distance:.4f}) ---")
            print(f"Chunk Index: {chunk.chunk_index}")
            print(f"Pages: {chunk.page_start}-{chunk.page_end}")
            print(f"\nContent:")
            print(f"{chunk.text[:500]}...")
            print()
 
        return results
 
    finally:
        db.close()
 
 
def interactive_mode():
    """Interactive query mode"""
    print_section("Interactive Semantic Search")
    print("Type your questions to search the documents.")
    print("Commands:")
    print("  'list' - Show all documents")
    print("  'doc:N query' - Search only in document N")
    print("  'quit' or 'exit' - Exit")
    print()
 
    while True:
        try:
            user_input = input("Query> ").strip()
 
            if not user_input:
                continue
 
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
 
            if user_input.lower() == 'list':
                list_documents()
                continue
 
            # Check for document-specific query (doc:1 query text)
            if user_input.startswith('doc:'):
                try:
                    parts = user_input.split(' ', 1)
                    doc_id = int(parts[0].split(':')[1])
                    query = parts[1] if len(parts) > 1 else ""
 
                    if not query:
                        print("Please provide a query after the document ID")
                        continue
 
                    search_in_document(query, doc_id, top_k=3)
                except (ValueError, IndexError):
                    print("Invalid format. Use: doc:N query text")
                continue
 
            # Regular search across all documents
            semantic_search(user_input, top_k=3)
 
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {str(e)}")
 
 
def main():
    """Main function"""
    print("\n" + "=" * 70)
    print("  SEMANTIC SEARCH TEST")
    print("=" * 70)
 
    # Check if documents exist
    if not list_documents():
        sys.exit(1)
 
    # Check for command line arguments
    if len(sys.argv) > 1:
        # Command line query mode
        query = ' '.join(sys.argv[1:])
        semantic_search(query, top_k=5)
    else:
        # Interactive mode
        interactive_mode()
 
 
if __name__ == "__main__":
    main()
 