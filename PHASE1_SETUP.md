# Phase 1: Local LLM & Embeddings Model Setup

## Overview

This phase sets up the local models for embeddings and text generation. After completing this phase, you'll have:

1. **Ollama** running as a Docker service for local LLM inference
2. **Embedding model** (sentence-transformers) for vector generation
3. **Chat model** (via Ollama) for answer generation
4. A **test script** that validates both models are working

## Model Choices

### Embedding Model
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions**: 384 (matches database configuration)
- **Size**: ~80MB
- **Use**: Converting text to vectors for semantic search

### Chat Model (LLM)
- **Model**: `llama3.2:3b`
- **Parameters**: ~3 billion
- **Size**: ~2GB
- **Use**: Generating answers in the RAG pipeline

These configurations are documented in `python-service/model_config.py`.

## Setup Instructions

### Step 1: Start All Services

Start all services including the new Ollama service:

```bash
docker compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Python service (port 8000)
- Java service (port 8080)
- **Ollama** (port 11434) ← New in Phase 1

### Step 2: Verify Ollama is Running

Check that Ollama is running:

```bash
docker compose ps ollama
```

You should see the ollama container in "Up" status.

Test Ollama API:

```bash
curl http://localhost:11434/api/tags
```

### Step 3: Pull the Chat Model

Pull the Llama 3.2 model into Ollama:

```bash
docker compose exec ollama ollama pull llama3.2:3b
```

This will download ~2GB. It may take a few minutes depending on your internet connection.

**Alternative models** you can try:
- `mistral:7b` - Larger, better quality (4.1GB)
- `phi3:3.8b` - Microsoft's Phi-3 (2.3GB)
- `gemma:2b` - Google's smaller model (1.4GB)

To use a different model, edit `LLM_MODEL_NAME` in `python-service/model_config.py` and pull that model instead.

### Step 4: Install Python Dependencies

The Python service container needs the updated requirements (including the `ollama` package):

```bash
# Rebuild the Python service to install new dependencies
docker compose build python-service

# Restart the Python service
docker compose up -d python-service
```

Or, if developing locally:

```bash
cd python-service
pip install -r requirements.txt
```

### Step 5: Run the Test Script

Now test that both models are working:

```bash
# Option 1: Run inside the Docker container (recommended)
docker compose exec python-service python test_models.py

# Option 2: Run locally (if you have dependencies installed)
cd python-service
python test_models.py
```

### Expected Output

The test script will:

1. **Test Embedding Model**:
   - Load `all-MiniLM-L6-v2`
   - Generate a 384-dimensional embedding vector
   - Display vector statistics

2. **Test Chat Model**:
   - Connect to Ollama
   - Send a test prompt about RAG
   - Display the generated answer

Example output:

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PHASE 1: MODEL TESTING                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

================================================================================
TESTING EMBEDDING MODEL
================================================================================
Model: sentence-transformers/all-MiniLM-L6-v2
Expected dimension: 384

Loading embedding model...
✓ Model loaded successfully!

Test text: 'This is a test sentence for generating embeddings.'

Generating embedding...
✓ Embedding generated successfully!
  - Vector type: <class 'numpy.ndarray'>
  - Vector shape: (384,)
  - Vector dimension: 384
  - Expected dimension: 384

✓ Dimension matches configuration!

[... embedding values ...]

================================================================================
TESTING LLM (CHAT) MODEL
================================================================================
Model: llama3.2:3b
Ollama URL: http://ollama:11434

[... model checks ...]

Generating response...

✓ Response generated successfully!

--------------------------------------------------------------------------------
LLM RESPONSE:
--------------------------------------------------------------------------------
Retrieval-Augmented Generation (RAG) is a technique that combines the strengths
of large language models with external knowledge retrieval. It works by first
retrieving relevant documents from a knowledge base, then using those documents
as context for the LLM to generate more accurate and informed responses...
--------------------------------------------------------------------------------

================================================================================
SUMMARY
================================================================================
Embedding Model: ✓ PASS
LLM Model:       ✓ PASS

✓ All tests passed! Phase 1 is complete.

Model Configuration:
  EMBEDDING_MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
  LLM_MODEL_NAME = 'llama3.2:3b'

You can now proceed to Phase 2: PDF Ingestion.
```

## Usage 

Users can now: 
1. Start all services: `docker compose up -d` 
2. Pull chat model: `docker compose exec ollama ollama pull llama3.2:3b` 
3. Run tests: `docker compose exec python-service python test_models.py` 


## Troubleshooting

### Ollama Connection Issues

If you get connection errors to Ollama:

```bash
# Check if Ollama container is running
docker compose ps ollama

# Check Ollama logs
docker compose logs ollama

# Restart Ollama
docker compose restart ollama
```

### Model Not Found

If the test script says the model isn't found:

```bash
# List available models
docker compose exec ollama ollama list

# Pull the model manually
docker compose exec ollama ollama pull llama3.2:3b
```

### Embedding Model Download Issues

The embedding model downloads automatically on first use. If it fails:

```bash
# Clear cache and retry
rm -rf python_cache/*
docker compose restart python-service
docker compose exec python-service python test_models.py
```

### Memory Issues

If you run out of memory:

1. **For the Chat Model**: Try a smaller model like `gemma:2b` or `phi3:mini`
2. **For Embeddings**: The current model is already quite small (80MB)
3. **System Resources**: Ensure Docker has at least 4GB RAM allocated

## Configuration Files

All model configurations are centralized in:

- **`python-service/model_config.py`**: Model names, dimensions, and parameters
- **`docker-compose.yml`**: Ollama service configuration
- **`python-service/requirements.txt`**: Python dependencies including `ollama`

## Next Steps

Once Phase 1 tests pass successfully:

✅ You have working local models
✅ You can generate embeddings (384-dimensional vectors)
✅ You can generate text with the LLM
✅ Model names are documented and consistent

**Proceed to Phase 2**: PDF Ingestion and Processing

## Architecture Notes

### Why Two Different Model Systems?

- **Sentence-Transformers** (Python library): Optimized for embeddings, runs in Python process
- **Ollama** (Service): Optimized for LLM inference, runs as separate service with model caching

This separation is intentional:
- Embeddings are fast and run during PDF ingestion
- LLM generation is slower and runs during query time
- Ollama provides a clean API and manages model lifecycle

### Model Storage

- **Sentence-transformers models**: Cached in `python_cache/` volume
- **Ollama models**: Stored in `ollama-data` Docker volume
- Both persist across container restarts

### GPU Support

To enable GPU acceleration for Ollama (NVIDIA GPUs only):

1. Edit `docker-compose.yml`
2. Uncomment the GPU configuration under the `ollama` service
3. Ensure you have `nvidia-docker` installed
4. Restart: `docker compose up -d ollama`

GPU acceleration significantly speeds up LLM inference.
