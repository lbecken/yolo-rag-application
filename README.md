# RAG PDF Query Application

A Retrieval-Augmented Generation (RAG) application for querying PDF documents using natural language. Upload PDF files, extract content, generate embeddings, and ask questions powered by a local LLM.

## Architecture

This project uses a hybrid architecture:

- **Python Service** (`python-service/`): Handles PDF ingestion, text extraction, chunking, and embedding generation
- **Java Spring Boot Service** (`java-service/`): Provides REST API, RAG pipeline orchestration, and web UI
- **PostgreSQL with pgvector**: Vector database for storing document chunks and embeddings
- **Local LLM**: For generating answers (e.g., via Ollama)

## Project Structure

```
yolo-rag-application/
├── python-service/          # FastAPI service for PDF processing
│   ├── main.py             # Main application
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile
│   └── .env.example
├── java-service/           # Spring Boot service for queries
│   ├── src/
│   │   └── main/
│   │       ├── java/com/rag/app/
│   │       │   ├── RagApplication.java
│   │       │   └── controller/
│   │       │       └── HealthController.java
│   │       └── resources/
│   │           └── application.properties
│   ├── pom.xml
│   └── Dockerfile
├── infrastructure/         # Database initialization
│   └── init-db.sql
├── docker-compose.yml     # Orchestrates all services
└── README.md
```

## Prerequisites

- Docker and Docker Compose
- Java 17+ (for local development)
- Python 3.11+ (for local development)
- Maven 3.9+ (for local development)

## Phase 0 - Setup and Verification

This is Phase 0 of the project: basic project structure and environment setup.

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd yolo-rag-application
   ```

2. **Start all services**
   ```bash
   docker-compose up --build
   ```

   This will start:
   - PostgreSQL with pgvector on port 5432
   - Python service on port 8000
   - Java service on port 8080

3. **Verify services are running**

   Check Python service health:
   ```bash
   curl http://localhost:8000/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "service": "python-ingestion-service",
     "version": "0.1.0"
   }
   ```

   Check Java service health:
   ```bash
   curl http://localhost:8080/api/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "service": "rag-query-service",
     "version": "0.1.0"
   }
   ```

4. **View API documentation**
   - Python service: http://localhost:8000/docs
   - Spring Boot Actuator: http://localhost:8080/actuator/health

### Local Development Setup

#### Python Service

1. Navigate to python-service directory:
   ```bash
   cd python-service
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy environment file:
   ```bash
   cp .env.example .env
   ```

5. Run the service:
   ```bash
   python main.py
   ```

#### Java Service

1. Navigate to java-service directory:
   ```bash
   cd java-service
   ```

2. Build the project:
   ```bash
   mvn clean install
   ```

3. Run the application:
   ```bash
   mvn spring-boot:run
   ```

   Or run the JAR:
   ```bash
   java -jar target/rag-service-0.1.0.jar
   ```

## Technology Stack

### Python Service
- FastAPI: Web framework
- pypdf/pdfplumber: PDF parsing
- sentence-transformers: Embedding generation
- FAISS: Local vector search
- PostgreSQL: Database connectivity

### Java Service
- Spring Boot 3.2: Application framework
- Spring Data JPA: Database access
- PostgreSQL: Database
- Apache PDFBox: PDF processing (alternative)
- WebFlux: HTTP client for calling Python service and LLM

### Infrastructure
- PostgreSQL 16 with pgvector: Vector database
- Docker & Docker Compose: Containerization

## Next Steps

Phase 0 is complete! The project skeleton is set up with:
- ✅ Python FastAPI service with health endpoint
- ✅ Java Spring Boot service with health endpoint
- ✅ PostgreSQL with pgvector extension
- ✅ Docker Compose orchestration
- ✅ Basic project structure

### Upcoming Phases:

**Phase 1**: PDF Ingestion Pipeline
- PDF upload endpoint
- Text extraction and cleaning
- Chunking with overlap
- Embedding generation
- Storage in vector database

**Phase 2**: Vector Store & Retrieval
- Vector similarity search
- Metadata filtering
- Top-k retrieval

**Phase 3**: LLM Integration & RAG Pipeline
- Local LLM setup (Ollama)
- Prompt engineering
- Answer generation with citations

**Phase 4**: Web UI
- Document management page
- Chat interface
- Source display

## Troubleshooting

### Services won't start
- Ensure Docker is running
- Check ports 5432, 8000, and 8080 are available
- Run `docker-compose logs` to see error messages

### Database connection issues
- Wait for PostgreSQL to be fully initialized (check with `docker-compose logs db`)
- Verify pgvector extension is installed: `docker-compose exec db psql -U raguser -d ragdb -c "SELECT * FROM pg_extension WHERE extname='vector';"`

### Python service issues
- Check Python version: `python --version` (should be 3.11+)
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

### Java service issues
- Check Java version: `java -version` (should be 17+)
- Clean and rebuild: `mvn clean install -U`

## Contributing

This project is in active development. See the plan document for upcoming features and phases.

## License

[Your License Here]