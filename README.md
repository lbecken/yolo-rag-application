# RAG PDF Query Application

A Retrieval-Augmented Generation (RAG) application for querying PDF documents using natural language. Upload PDF files, extract content, generate embeddings, and ask questions powered by a local LLM.

## Architecture

This project uses a hybrid architecture:

- **Frontend** (`frontend/`): React + Vite web UI for document management and Q&A chat
- **Python Service** (`python-service/`): Handles PDF ingestion, text extraction, chunking, and embedding generation
- **Java Spring Boot Service** (`java-service/`): Provides REST API and RAG pipeline orchestration
- **PostgreSQL with pgvector**: Vector database for storing document chunks and embeddings
- **Local LLM**: For generating answers (e.g., via Ollama)

## Project Structure

```
yolo-rag-application/
├── frontend/               # React + Vite web UI
│   ├── src/
│   │   ├── api/           # API client functions
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components (DocumentList, Upload, Chat)
│   │   ├── App.jsx        # Main app with routing
│   │   └── main.jsx       # Entry point
│   ├── package.json
│   ├── vite.config.js
│   └── start.sh           # Script to start dev server
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
- Node.js 18+ (for frontend development)
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

   Then start the frontend (in a separate terminal):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   - Frontend: http://localhost:5173

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

#### Frontend

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

   Or use the start script:
   ```bash
   ./start.sh
   ```

The frontend will be available at http://localhost:5173 with hot module replacement enabled.

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

### Frontend
- React 19: UI framework
- Vite 7: Build tool with HMR
- React Router 7: Client-side routing

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

## Project Status

**Current Phase**: Phase 8 Complete ✅

### Completed Phases:

**Phase 0**: Basic Setup ✅
- ✅ Python FastAPI service with health endpoint
- ✅ Java Spring Boot service with health endpoint
- ✅ PostgreSQL with pgvector extension
- ✅ Docker Compose orchestration
- ✅ Basic project structure

**Phase 1**: Model Setup & Configuration ✅
- ✅ Ollama service running in Docker (port 11434)
- ✅ Embedding model configured: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- ✅ Chat model configured: `llama3.2:3b` via Ollama
- ✅ Model testing scripts and validation
- See `PHASE1_SETUP.md` for details

**Phase 2**: Database Schema & pgvector Integration ✅
- ✅ Flyway database migrations configured
- ✅ `documents` and `chunks` tables with proper indexes
- ✅ HNSW index for fast vector similarity search
- ✅ JPA entities and repositories
- ✅ Vector similarity search queries
- See `PHASE2_SCHEMA.md` for details

**Phase 3**: PDF Ingestion Service ✅
- ✅ PDF text extraction using PyMuPDF
- ✅ Smart text chunking (1500 chars, 200 overlap)
- ✅ Embedding generation pipeline
- ✅ Database integration with transactions
- ✅ POST /ingest endpoint
- See `PHASE3_INGESTION.md` for details

**Phase 4**: Python Embedding API (/embed) ✅

**Phase 5**: Java Data Access and Embedding Client ✅

**Phase 6**: RAG QA Service ✅

**Phase 7**: Document Upload Endpoint ✅

**Phase 8**: Web UI ✅
- ✅ Vite + React frontend application
- ✅ Document management page with list/delete
- ✅ PDF upload interface
- ✅ Chat/Q&A interface with citations
- ✅ API client for Java service integration
- ✅ CORS configuration for frontend access

### Testing Phase 3

Run the comprehensive test script:
```bash
python test_phase3.py
```

Or test manually:
```bash
# Upload a PDF
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@/path/to/document.pdf" \
  -F "title=My Document"

# Verify in database
docker-compose exec db psql -U raguser -d ragdb -c "SELECT * FROM documents;"
docker-compose exec db psql -U raguser -d ragdb -c "SELECT COUNT(*) FROM chunks;"
```

### Upcoming Phases:

**Phase 4**: RAG Query Pipeline
- Query endpoint accepting natural language questions
- Vector similarity search for relevant chunks
- Context assembly from top-k chunks
- LLM prompt engineering
- Answer generation with sources

**Future Enhancements**:
- Query history and result caching
- Advanced search filters
- Multi-document conversations
- Authentication and user management

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