"""
Model Configuration for RAG Application

This file defines the models used throughout the application.
Keep these consistent to ensure embeddings and generation work correctly.
"""

# ============================================================================
# EMBEDDING MODEL CONFIGURATION
# ============================================================================
# Using sentence-transformers for local embedding generation
# Model: all-MiniLM-L6-v2
# - Dimensions: 384 (matches database configuration in init-db.sql)
# - Size: ~80MB
# - Performance: Good balance of speed and quality
# - Use case: Semantic search and document retrieval
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# ============================================================================
# LLM (CHAT) MODEL CONFIGURATION
# ============================================================================
# Using Ollama for local LLM inference
# Model: llama3.2:3b
# - Parameters: ~3 billion
# - Size: ~2GB
# - Performance: Fast inference, good quality for local deployment
# - Use case: Answer generation in RAG pipeline
LLM_MODEL_NAME = "llama3.2:3b"

# Alternative models you can try:
# - "mistral:7b" - Larger model, better quality but slower
# - "phi3:3.8b" - Microsoft's Phi-3, also good quality
# - "gemma:2b" - Google's smaller model, faster but lower quality

# ============================================================================
# OLLAMA CONFIGURATION
# ============================================================================
# Ollama service URL (adjust based on your setup)
# - Docker: http://ollama:11434
# - Local: http://localhost:11434
OLLAMA_BASE_URL = "http://ollama:11434"

# ============================================================================
# GENERATION PARAMETERS
# ============================================================================
# Default parameters for text generation
DEFAULT_TEMPERATURE = 0.7  # Lower = more focused, Higher = more creative
DEFAULT_MAX_TOKENS = 512   # Maximum tokens in generated response
DEFAULT_TOP_P = 0.9        # Nucleus sampling parameter
DEFAULT_TOP_K = 40         # Top-k sampling parameter

# ============================================================================
# RAG PARAMETERS
# ============================================================================
# Number of similar documents to retrieve for context
TOP_K_RETRIEVAL = 5

# Maximum context length to send to LLM (in characters)
MAX_CONTEXT_LENGTH = 4000
