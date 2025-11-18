#!/bin/bash
# 1. Upload a PDF via Java POST (/api/documents)
# 2. Java forward to Python POST (/ingest)
# 3. Python extracts text, chunks, generates embeddings, stores in DB
#curl -X POST http://localhost:8080/api/documents \
#  -F "file=@your-document.pdf" \
#  -F "title=My Document"

# List all documents
# Returns list of docuents: Document ID, creation date, title, chunk count
curl http://localhost:8080/api/documents

# Get a specific document
#curl http://localhost:8080/api/documents/1

# Delete a document
#curl -X DELETE http://localhost:8080/api/documents/1
