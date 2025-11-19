# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Retrieval-Augmented Generation (RAG) application for querying PDF documents using natural language. This is a hybrid microservices architecture with Python handling PDF processing/embeddings and Java Spring Boot orchestrating queries and UI.

**Current Status**: Phase 8 complete (Web UI with Vite + React). See README.md for planned phases.

**Phase 1 Achievements**:
- ✅ Ollama service running in Docker (port 11434)
- ✅ Embedding model configured: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- ✅ Chat model configured: `llama3.2:3b` via Ollama
- ✅ Test script available: `python-service/test_models.py`
- ✅ Model configuration documented: `python-service/model_config.py`

**Phase 2 Achievements**:
- ✅ Flyway database migrations configured and implemented
- ✅ `documents` table created with indexes
- ✅ `chunks` table created with pgvector support (384-dimensional embeddings)
- ✅ HNSW index on embeddings for fast vector similarity search
- ✅ JPA entities and repositories for documents and chunks
- ✅ Vector similarity search queries implemented
- ✅ Test controller for verifying vector operations
- ✅ Documentation: `PHASE2_SCHEMA.md`

**Phase 8 Achievements**:
- ✅ Vite + React 19 frontend application
- ✅ Document management page (list, delete)
- ✅ PDF upload interface
- ✅ Chat/Q&A interface with citations
- ✅ React Router for navigation
- ✅ API client for Java service integration
- ✅ CORS configuration for frontend access

## Architecture

### Service Responsibilities

1. **Frontend** (port 5173): Web UI for document management and Q&A
   - Vite + React 19 application in `frontend/`
   - React Router for navigation between pages
   - API client connects to Java service
   - Pages: DocumentList (home), Upload, Chat

2. **Python Service** (port 8000): PDF ingestion, text extraction, chunking, and embedding generation
   - FastAPI application in `python-service/main.py`
   - Uses sentence-transformers for embeddings (384-dimensional vectors)
   - Communicates with PostgreSQL for vector storage

3. **Java Service** (port 8080): RAG pipeline orchestration and REST API
   - Spring Boot 3.2 application (Java 17)
   - Main class: `com.rag.app.RagApplication`
   - Uses WebClient for HTTP calls to Python service and LLM
   - JPA/Hibernate for database access
   - CORS enabled for frontend access

4. **PostgreSQL with pgvector** (port 5432): Vector database
   - Database: `ragdb`, User: `raguser`
   - Extension: pgvector enabled
   - Initialized via `infrastructure/init-db.sql`

5. **Ollama** (port 11434): Local LLM inference service
   - Docker service: `ollama/ollama:latest`
   - Hosts the chat model: `llama3.2:3b`
   - API endpoint: `http://ollama:11434` (in Docker) or `http://localhost:11434` (local)
   - Model storage: `ollama-data` Docker volume

### Inter-Service Communication

- Java service calls Python service via WebClient (configured in `RagApplication.java`)
- Python service URL: `http://python-service:8000` (in Docker) or `http://localhost:8000` (local)
- Python service calls Ollama for LLM inference: `http://ollama:11434` (in Docker)
- All services communicate over the `rag-network` Docker bridge network

## Development Commands

### Starting All Services (Recommended)

```bash
docker-compose up --build
```

Services will be available at:
- Frontend: http://localhost:5173
- Python service: http://localhost:8000 (docs at /docs)
- Java service: http://localhost:8080
- PostgreSQL: localhost:5432
- Ollama: http://localhost:11434 (API at /api)

### Frontend (Local Development)

```bash
cd frontend
npm install
npm run dev
```

Or use the start script:
```bash
./start.sh
```

### Python Service (Local Development)

```bash
cd python-service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Java Service (Local Development)

Build and run:
```bash
cd java-service
mvn clean install
mvn spring-boot:run
```

Or run the JAR:
```bash
java -jar target/rag-service-0.1.0.jar
```

Run tests:
```bash
mvn test
```

### Database Operations

Access PostgreSQL:
```bash
docker-compose exec db psql -U raguser -d ragdb
```

Verify pgvector extension:
```bash
docker-compose exec db psql -U raguser -d ragdb -c "SELECT * FROM pg_extension WHERE extname='vector';"
```

### Ollama Operations

Pull the chat model:
```bash
docker-compose exec ollama ollama pull llama3.2:3b
```

List available models:
```bash
docker-compose exec ollama ollama list
```

Test Ollama API:
```bash
curl http://localhost:11434/api/tags
```

### Phase 1: Test Models

Test both embedding and chat models:
```bash
# Inside Docker container (recommended)
docker-compose exec python-service python test_models.py

# Or locally if dependencies installed
cd python-service
python test_models.py
```

See `PHASE1_SETUP.md` for detailed Phase 1 setup instructions.

### Phase 2: Test Vector Operations

Verify database schema and vector similarity search:

```bash
# Check Flyway migration status
docker-compose exec db psql -U raguser -d ragdb -c "SELECT version, description, success FROM flyway_schema_history;"

# Verify tables and vector column
docker-compose exec db psql -U raguser -d ragdb -c "\d chunks"

# Initialize test data via REST API
curl -X POST http://localhost:8080/api/test/vector/init

# Test vector similarity search
curl -X POST "http://localhost:8080/api/test/vector/search?limit=3"

# Clear test data
curl -X DELETE http://localhost:8080/api/test/vector/clear
```

See `PHASE2_SCHEMA.md` for detailed Phase 2 setup and testing instructions.

## Key Configuration Files

- `docker-compose.yml`: Service orchestration with volumes (postgres_data, python_cache, ollama-data, maven-cache)
- `frontend/package.json`: Frontend dependencies (React 19, Vite, React Router)
- `frontend/vite.config.js`: Vite configuration
- `frontend/src/api/api.js`: API client for Java service (configurable via `VITE_API_URL` env var)
- `python-service/model_config.py`: **Model configuration** - embedding and LLM model names, dimensions, parameters
- `python-service/requirements.txt`: Python dependencies (FastAPI, sentence-transformers, ollama, pypdf, etc.)
- `python-service/test_models.py`: Test script for Phase 1 model validation
- `java-service/pom.xml`: Maven dependencies (Spring Boot 3.2, PostgreSQL, WebFlux, PDFBox, Flyway)
- `java-service/src/main/resources/application.properties`: All Spring configuration including database credentials, service URLs, and Flyway settings
- `java-service/src/main/resources/db/migration/`: Flyway migration scripts for database schema
- `PHASE1_SETUP.md`: Detailed Phase 1 setup and testing instructions
- `PHASE2_SCHEMA.md`: Detailed Phase 2 database schema and testing instructions

## Important Implementation Notes

### Vector Dimensions
The database is configured for 384-dimensional embeddings (matching sentence-transformers' default model). See `infrastructure/init-db.sql:10`.

### CORS Configuration
Python service has CORS enabled for all origins in `main.py:24-30`. Java service also has CORS enabled for frontend access. In production, these should be restricted to specific origins.

### Frontend API Configuration
The frontend API base URL defaults to `http://localhost:8080/api` but can be configured via the `VITE_API_URL` environment variable. See `frontend/src/api/api.js`.

### JPA Configuration
Hibernate DDL is set to `validate` in `application.properties:12`. Database schema is managed by Flyway migrations in `java-service/src/main/resources/db/migration/`. This ensures version-controlled, reproducible schema changes.

### Docker Volumes and Java Service
**IMPORTANT**: The Java service does NOT have a volume mount (unlike the Python service). This is intentional:
- Python service: Has `./python-service:/app` mount for hot-reload during development
- Java service: No volume mount because it uses a compiled JAR file that gets baked into the image
- When you modify Java code, rebuild with: `docker compose build java-service && docker compose up -d`
- DO NOT add a volume mount like `./java-service:/app` to the Java service - this will overwrite the compiled JAR and break the service

Other volumes:
- `./postgres_data` for database persistence
- `./python_cache` for Python model caching (sentence-transformers)
- `ollama-data` for Ollama model storage (Docker volume)
- `maven-cache` for Maven dependencies (Docker volume)

## Implementation Status

### ✅ Completed (Phase 0, 1, 2, 3 & 8)
- ✅ PostgreSQL with pgvector
- ✅ Python FastAPI service structure
- ✅ Java Spring Boot service structure
- ✅ Docker Compose orchestration
- ✅ Ollama service for local LLM
- ✅ Embedding model setup (sentence-transformers/all-MiniLM-L6-v2)
- ✅ Chat model setup (llama3.2:3b via Ollama)
- ✅ Model testing scripts and documentation
- ✅ Flyway database migrations
- ✅ Documents and chunks database schema
- ✅ HNSW index for vector similarity search
- ✅ JPA entities and repositories
- ✅ Vector similarity search queries
- ✅ Vector operations test controller
- ✅ PDF upload and ingestion endpoints
- ✅ Text chunking and embedding generation
- ✅ Vite + React frontend application
- ✅ Document management UI (list, upload, delete)
- ✅ Chat/Q&A interface with citations
- ✅ CORS configuration for frontend

### 🔄 Planned (Phase 4+)
- RAG query pipeline (combining retrieval + generation)
- Query history and result caching
- Advanced search filters
- Authentication and user management

When implementing new features, refer to the phase plan in README.md.

## Health Check Endpoints

- Frontend: http://localhost:5173 (Vite dev server)
- Python service: `GET http://localhost:8000/health`
- Java service: `GET http://localhost:8080/api/health`
- Spring Actuator: `GET http://localhost:8080/actuator/health`
- Ollama service: `GET http://localhost:11434/api/tags`

## Model Configuration Reference

All model settings are centralized in `python-service/model_config.py`:

```python
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

LLM_MODEL_NAME = "llama3.2:3b"
OLLAMA_BASE_URL = "http://ollama:11434"
```

**IMPORTANT**: Keep these consistent throughout the application to ensure embeddings match vector dimensions in the database.
