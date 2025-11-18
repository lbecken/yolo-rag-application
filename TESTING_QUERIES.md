# Testing Document Queries
 
After ingesting a PDF, you can test querying in several ways:
 
## Prerequisites
 
1. **Ingest a PDF first:**
   ```bash
   curl -X POST "http://localhost:8000/ingest" \
     -F "file=@/path/to/document.pdf" \
     -F "title=My Document"
   ```
 
2. **Note the document_id returned** from the ingestion response.
 
## Method 1: HTTP API - Query Endpoint
 
### Basic Query (All Documents)
 
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic of the document?",
    "top_k": 5
  }'
```
 
### Query Specific Document
 
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain the methodology",
    "top_k": 3,
    "document_id": 1
  }'
```
 
### Example Response
 
```json
{
  "query": "What is the main topic?",
  "num_results": 5,
  "results": [
    {
      "chunk_id": 3,
      "document_id": 1,
      "chunk_index": 2,
      "page_start": 0,
      "page_end": 0,
      "content": "The main topic of this document is...",
      "distance": 0.234
    },
    ...
  ]
}
```
 
**Note**: Lower distance = more similar/relevant.
 
## Method 2: Python Script (Interactive)
 
Make the script executable and run it:
 
```bash
chmod +x test_query.py
python test_query.py
```
 
This opens an interactive prompt where you can:
 
### Commands
 
- **Type any question** - Searches all documents
  ```
  Query> What is machine learning?
  ```
 
- **`list`** - Show all ingested documents
  ```
  Query> list
  ```
 
- **`doc:N query`** - Search only in document N
  ```
  Query> doc:1 What is the methodology?
  ```
 
- **`quit` or `exit`** - Exit the program
 
### One-off Query (Non-interactive)
 
```bash
python test_query.py "What is the main topic?"
```
 
## Method 3: Direct SQL Queries
 
For lower-level testing and debugging:
 
```bash
# Run the SQL test script
docker-compose exec db psql -U raguser -d ragdb -f /path/to/test_vector_search.sql
```
 
Or run individual queries:
 
### Find Similar Chunks Using Vector Similarity
 
```bash
docker-compose exec db psql -U raguser -d ragdb
```
 
Then in the PostgreSQL prompt:
 
```sql
-- Get a sample embedding from chunk 1
WITH sample_vector AS (
    SELECT embedding FROM chunks WHERE id = 1
)
-- Find top 5 most similar chunks
SELECT
    c.id,
    c.document_id,
    c.chunk_index,
    substring(c.content, 1, 200) as preview,
    c.embedding <-> (SELECT embedding FROM sample_vector) as distance
FROM chunks c
ORDER BY distance
LIMIT 5;
```
 
### Search by Cosine Similarity
 
```sql
WITH sample_vector AS (
    SELECT embedding FROM chunks WHERE id = 1
)
SELECT
    c.id,
    substring(c.content, 1, 150) as preview,
    1 - (c.embedding <=> (SELECT embedding FROM sample_vector)) as similarity
FROM chunks c
ORDER BY c.embedding <=> (SELECT embedding FROM sample_vector) DESC
LIMIT 5;
```
 
## Method 4: FastAPI Docs (Swagger UI)
 
1. Open http://localhost:8000/docs in your browser
2. Find the **POST /query** endpoint
3. Click "Try it out"
4. Enter your query:
   ```json
   {
     "query": "your question here",
     "top_k": 5
   }
   ```
5. Click "Execute"
6. View the response below
 
## Understanding the Results
 
### Distance Metrics
 
The `/query` endpoint uses **L2 distance** (Euclidean distance):
- **Lower values** = more similar
- Typical range: 0.0 to 2.0
- < 0.5: Very similar
- 0.5-1.0: Moderately similar
- > 1.0: Less similar
 
### Cosine Similarity (SQL)
 
When using cosine similarity:
- **Higher values** = more similar
- Range: -1 to 1
- > 0.8: Very similar
- 0.5-0.8: Moderately similar
- < 0.5: Less similar
 
## Example Workflow
 
### 1. Ingest a Document
 
```bash
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@research_paper.pdf" \
  -F "title=AI Research Paper"
```
 
Response:
```json
{
  "status": "success",
  "document_id": 1,
  "num_chunks": 42,
  "title": "AI Research Paper"
}
```
 
### 2. Query the Document
 
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main findings?",
    "top_k": 3,
    "document_id": 1
  }'
```
 
### 3. Review Results
 
The response will show the top 3 most relevant chunks from your document, ranked by similarity to your question.
 
### 4. Interactive Exploration
 
```bash
python test_query.py
```
 
```
Query> list
  ID: 1
  Title: AI Research Paper
  Chunks: 42
  ...
 
Query> What methodology was used?
 
  --- Result 1 (Distance: 0.312) ---
  Document ID: 1
  Chunk Index: 5
  Pages: 2-2
 
  Content:
  Our methodology involved a novel approach...
 
Query> doc:1 What are the limitations?
 
Query> quit
```
 
## Troubleshooting
 
### "No results found"
 
- Check that documents were ingested: `python test_query.py` then type `list`
- Verify chunks exist:
  ```bash
  docker-compose exec db psql -U raguser -d ragdb -c "SELECT COUNT(*) FROM chunks;"
  ```
- Ensure embeddings are present:
  ```bash
  docker-compose exec db psql -U raguser -d ragdb -c "SELECT COUNT(*) FROM chunks WHERE embedding IS NOT NULL;"
  ```
 
### "Error: cannot import embeddings"
 
- Make sure you're in the project root directory
- Check that `python-service/embeddings.py` exists
- The Python service must be running (for HTTP queries) or sentence-transformers installed locally (for test_query.py)
 
### Query returns irrelevant results
 
- Try different phrasings of your question
- Increase `top_k` to see more results
- Check if the document actually contains information about your query
- Consider the chunking - very specific info might be split across chunks
 
### Slow query performance
 
- First query is slow (model loading): 5-10 seconds
- Subsequent queries should be fast: < 1 second
- For large datasets (1000+ chunks), consider tuning HNSW index parameters
 
## What's Next?
 
This query functionality provides **retrieval** - the "R" in RAG. For the full RAG pipeline:
 
**Phase 4** will add:
- LLM integration (Ollama)
- Prompt engineering
- Context assembly from multiple chunks
- Answer generation with citations
- Combined `/ask` endpoint (retrieval + generation)
 
**Current Capabilities:**
- ✅ Semantic search across all documents
- ✅ Filter search to specific document
- ✅ Rank by relevance
- ✅ View relevant text chunks
 
**Coming Soon (Phase 4):**
- ⏳ Generate natural language answers
- ⏳ Cite sources in responses
- ⏳ Multi-document reasoning
- ⏳ Conversational context
 
## Advanced: Custom Search
 
You can modify the search behavior by editing `python-service/db.py`:
 
### Change Distance Metric
 
Currently uses L2 distance (`<->`). To use cosine distance (`<=>`):
 
```python
# In db.py, search_similar_chunks function:
results = db.query(
    Chunk,
    Chunk.embedding.cosine_distance(embedding_list).label("distance")  # Changed
).order_by("distance").limit(limit).all()
```
 
### Add Metadata Filtering
 
Filter by page number, date, or other criteria:
 
```python
results = db.query(
    Chunk,
    Chunk.embedding.l2_distance(embedding_list).label("distance")
).filter(
    Chunk.page_start >= min_page,
    Chunk.page_end <= max_page
).order_by("distance").limit(limit).all()
```
 
## Testing Tips
 
1. **Start Simple**: Query with broad questions to verify the system works
2. **Iterate**: Refine queries based on results
3. **Compare**: Try the same query with different top_k values
4. **Verify**: Use SQL queries to inspect raw data when debugging
5. **Monitor**: Check service logs: `docker-compose logs -f python-service`
 
## Sample Queries to Try
 
### General Understanding
- "What is this document about?"
- "Summarize the main points"
- "What are the key takeaways?"
 
### Specific Information
- "What is the methodology?"
- "What are the results?"
- "What are the limitations?"
 
### Factual Lookup
- "What is the definition of [term]?"
- "Who are the authors?"
- "What date was this published?"
 
### Analysis
- "What evidence supports the conclusion?"
- "What are the pros and cons?"
- "How does this compare to [topic]?"
