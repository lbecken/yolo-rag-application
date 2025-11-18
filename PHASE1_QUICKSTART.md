# Phase 1 Quick Start Guide

Quick reference for setting up and testing local models.

## 🚀 Quick Setup (5 minutes)

### 1. Start all services
```bash
docker compose up -d
```

### 2. Pull the chat model
```bash
docker compose exec ollama ollama pull llama3.2:3b
```

### 3. Rebuild Python service (for ollama dependency)
```bash
docker compose build python-service
docker compose up -d python-service
```

### 4. Run tests
```bash
docker compose exec python-service python test_models.py
```

## ✅ Expected Result

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PHASE 1: MODEL TESTING                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

================================================================================
TESTING EMBEDDING MODEL
================================================================================
✓ Model loaded successfully!
✓ Embedding generated successfully!
✓ Dimension matches configuration!

================================================================================
TESTING LLM (CHAT) MODEL
================================================================================
✓ Response generated successfully!

[LLM response about RAG...]

================================================================================
SUMMARY
================================================================================
Embedding Model: ✓ PASS
LLM Model:       ✓ PASS

✓ All tests passed! Phase 1 is complete.
```

## 📝 Common Commands

### Service Management
```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart a specific service
docker compose restart python-service

# View logs
docker compose logs -f python-service
docker compose logs -f ollama

# Check service status
docker compose ps
```

### Ollama Commands
```bash
# Pull a model
docker compose exec ollama ollama pull llama3.2:3b

# List available models
docker compose exec ollama ollama list

# Remove a model
docker compose exec ollama ollama rm llama3.2:3b

# Check Ollama API
curl http://localhost:11434/api/tags

# Interactive chat (for testing)
docker compose exec ollama ollama run llama3.2:3b
```

### Testing
```bash
# Run model tests
docker compose exec python-service python test_models.py

# Test embedding only
docker compose exec python-service python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
embedding = model.encode('test')
print(f'Dimension: {len(embedding)}')
"

# Test Ollama only
curl -X POST http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "What is RAG?",
  "stream": false
}'
```

### Health Checks
```bash
# Check all services
curl http://localhost:8000/health    # Python service
curl http://localhost:8080/actuator/health  # Java service
curl http://localhost:11434/api/tags # Ollama

# Or all at once
curl -s http://localhost:8000/health && echo " - Python ✓" && \
curl -s http://localhost:8080/actuator/health && echo " - Java ✓" && \
curl -s http://localhost:11434/api/tags && echo " - Ollama ✓"
```

### Python Service Development
```bash
# Enter Python service container
docker compose exec python-service bash

# Install new Python dependencies
docker compose exec python-service pip install <package>

# Or rebuild after updating requirements.txt
docker compose build python-service
docker compose up -d python-service
```

## 🐛 Troubleshooting

### Ollama Not Responding
```bash
# Check if container is running
docker compose ps ollama

# Check logs
docker compose logs ollama

# Restart Ollama
docker compose restart ollama

# If still failing, recreate
docker compose down
docker compose up -d ollama
```

### Model Not Found
```bash
# Verify model is pulled
docker compose exec ollama ollama list

# If not there, pull it
docker compose exec ollama ollama pull llama3.2:3b

# If pull fails, check disk space
df -h
```

### Embedding Test Fails
```bash
# Check Python dependencies
docker compose exec python-service pip list | grep sentence-transformers

# Clear cache and retry
rm -rf python_cache/*
docker compose restart python-service
docker compose exec python-service python test_models.py
```

### Connection Refused Errors
```bash
# Make sure all services are on the same network
docker network ls
docker network inspect yolo-rag-application_rag-network

# Verify service names resolve
docker compose exec python-service ping -c 2 ollama
docker compose exec java-service ping -c 2 python-service
```

## 📊 Model Information

### Embedding Model: all-MiniLM-L6-v2
- **Provider**: sentence-transformers (Hugging Face)
- **Dimensions**: 384
- **Download**: Automatic on first use (~80MB)
- **Cache Location**: `./python_cache/`
- **Speed**: Very fast (~1000 vectors/sec on CPU)

### Chat Model: llama3.2:3b
- **Provider**: Meta via Ollama
- **Parameters**: ~3 billion
- **Download**: Manual via `ollama pull` (~2GB)
- **Storage**: Docker volume `ollama-data`
- **Speed**: ~10-50 tokens/sec on CPU (varies by hardware)

## 🔄 Alternative Models

### Smaller Chat Models (Faster, Less Accurate)
```bash
docker compose exec ollama ollama pull gemma:2b     # 1.4GB
docker compose exec ollama ollama pull phi3:mini    # 2.2GB
```

### Larger Chat Models (Slower, More Accurate)
```bash
docker compose exec ollama ollama pull mistral:7b       # 4.1GB
docker compose exec ollama ollama pull llama3.1:8b      # 4.7GB
docker compose exec ollama ollama pull llama3.2:11b     # 6.5GB (if you have 16GB+ RAM)
```

After changing models, update `LLM_MODEL_NAME` in `python-service/model_config.py`.

## 📖 Next Steps

Once Phase 1 tests pass:

1. ✅ Your local models are working
2. ✅ You can generate embeddings
3. ✅ You can generate text
4. → **Proceed to Phase 2**: PDF Ingestion

See `README.md` for the full phase plan.

## 💡 Tips

- **First run**: Model downloads can take 5-10 minutes total
- **Disk space**: Ensure you have at least 5GB free
- **RAM**: Recommend 8GB minimum, 16GB+ for larger models
- **GPU**: Optional but speeds up inference 10-100x
- **Persistence**: Models are cached and persist across restarts

## 🔗 Resources

- Ollama docs: https://ollama.ai/
- Sentence-transformers: https://www.sbert.net/
- Model hub: https://ollama.ai/library
- This project's docs: `PHASE1_SETUP.md` (detailed guide)
