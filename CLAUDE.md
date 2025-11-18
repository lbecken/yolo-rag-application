# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Retrieval-Augmented Generation (RAG) application for querying PDF documents using natural language. This is a hybrid microservices architecture with Python handling PDF processing/embeddings and Java Spring Boot orchestrating queries and UI.

**Current Status**: Phase 0 complete (basic infrastructure setup). See README.md for planned phases.

## Architecture

### Service Responsibilities

1. **Python Service** (port 8000): PDF ingestion, text extraction, chunking, and embedding generation
   - FastAPI application in `python-service/main.py`
   - Will use sentence-transformers for embeddings (384-dimensional vectors)
   - Communicates with PostgreSQL for vector storage

2. **Java Service** (port 8080): RAG pipeline orchestration, REST API, and web UI
   - Spring Boot 3.2 application (Java 17)
   - Main class: `com.rag.app.RagApplication`
   - Uses WebClient for HTTP calls to Python service and LLM
   - JPA/Hibernate for database access

3. **PostgreSQL with pgvector** (port 5432): Vector database
   - Database: `ragdb`, User: `raguser`
   - Extension: pgvector enabled
   - Initialized via `infrastructure/init-db.sql`

### Inter-Service Communication

- Java service calls Python service via WebClient (configured in `RagApplication.java`)
- Python service URL: `http://python-service:8000` (in Docker) or `http://localhost:8000` (local)
- LLM integration planned via Ollama at `http://localhost:11434` (see `application.properties`)

## Development Commands

### Starting All Services (Recommended)

```bash
docker-compose up --build
```

Services will be available at:
- Python service: http://localhost:8000 (docs at /docs)
- Java service: http://localhost:8080
- PostgreSQL: localhost:5432

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

## Key Configuration Files

- `docker-compose.yml`: Service orchestration with volumes mounted at `./postgres_data` and `./python_cache`
- `python-service/requirements.txt`: Python dependencies (FastAPI, sentence-transformers, pypdf, etc.)
- `java-service/pom.xml`: Maven dependencies (Spring Boot 3.2, PostgreSQL, WebFlux, PDFBox)
- `java-service/src/main/resources/application.properties`: All Spring configuration including database credentials and service URLs

## Important Implementation Notes

### Vector Dimensions
The database is configured for 384-dimensional embeddings (matching sentence-transformers' default model). See `infrastructure/init-db.sql:10`.

### CORS Configuration
Python service has CORS enabled for all origins in `main.py:24-30`. In production, this should be restricted to specific origins.

### JPA Configuration
Hibernate DDL is set to `update` in `application.properties:12`, which auto-updates schema. For production, use migrations (Flyway/Liquibase).

### Docker Volumes and Java Service
**IMPORTANT**: The Java service does NOT have a volume mount (unlike the Python service). This is intentional:
- Python service: Has `./python-service:/app` mount for hot-reload during development
- Java service: No volume mount because it uses a compiled JAR file that gets baked into the image
- When you modify Java code, rebuild with: `docker compose build java-service && docker compose up -d`
- DO NOT add a volume mount like `./java-service:/app` to the Java service - this will overwrite the compiled JAR and break the service

Other volumes:
- `./postgres_data` for database persistence
- `./python_cache` for Python model caching

## Planned Features (Not Yet Implemented)

The following are planned but NOT yet implemented:
- PDF upload and ingestion endpoints
- Text chunking and embedding generation
- Vector similarity search
- LLM integration with Ollama
- RAG query pipeline
- Web UI

When implementing new features, refer to the phase plan in README.md.

## Health Check Endpoints

- Python service: `GET http://localhost:8000/health`
- Java service: `GET http://localhost:8080/api/health`
- Spring Actuator: `GET http://localhost:8080/actuator/health`
