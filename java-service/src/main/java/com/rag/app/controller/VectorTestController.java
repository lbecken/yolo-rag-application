package com.rag.app.controller;

import com.rag.app.client.EmbeddingClient;
import com.rag.app.model.Chunk;
import com.rag.app.model.Document;
import com.rag.app.repository.ChunkRepository;
import com.rag.app.repository.DocumentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/**
 * Test controller for Phase 2: Vector operations testing.
 * This controller provides endpoints to test pgvector integration and similarity search.
 */
@RestController
@RequestMapping("/api/test/vector")
@RequiredArgsConstructor
@Slf4j
public class VectorTestController {

    private final DocumentRepository documentRepository;
    private final ChunkRepository chunkRepository;
    private final EmbeddingClient embeddingClient;

    /**
     * Initialize test data: Create a sample document with chunks and embeddings
     */
    @PostMapping("/init")
    public ResponseEntity<Map<String, Object>> initializeTestData() {
        log.info("Initializing test data for vector operations...");

        // Create a test document
        Document document = Document.builder()
                .title("Test Document for Vector Search")
                .filename("test_vector_search.pdf")
                .build();

        // Create sample chunks with embeddings
        // Using simple synthetic embeddings for demonstration
        List<Chunk> chunks = new ArrayList<>();

        // Chunk 1: About machine learning
        Chunk chunk1 = Chunk.builder()
                .text("Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data.")
                .pageStart(0)
                .pageEnd(0)
                .chunkIndex(0)
                .build();
        chunk1.setEmbedding(generateSyntheticEmbedding(1));
        document.addChunk(chunk1);
        chunks.add(chunk1);

        // Chunk 2: About deep learning
        Chunk chunk2 = Chunk.builder()
                .text("Deep learning uses neural networks with multiple layers to progressively extract higher-level features from raw input.")
                .pageStart(0)
                .pageEnd(0)
                .chunkIndex(1)
                .build();
        chunk2.setEmbedding(generateSyntheticEmbedding(2));
        document.addChunk(chunk2);
        chunks.add(chunk2);

        // Chunk 3: About natural language processing
        Chunk chunk3 = Chunk.builder()
                .text("Natural language processing enables computers to understand, interpret, and generate human language.")
                .pageStart(1)
                .pageEnd(1)
                .chunkIndex(2)
                .build();
        chunk3.setEmbedding(generateSyntheticEmbedding(3));
        document.addChunk(chunk3);
        chunks.add(chunk3);

        // Chunk 4: About computer vision
        Chunk chunk4 = Chunk.builder()
                .text("Computer vision trains computers to interpret and understand the visual world using digital images.")
                .pageStart(1)
                .pageEnd(1)
                .chunkIndex(3)
                .build();
        chunk4.setEmbedding(generateSyntheticEmbedding(4));
        document.addChunk(chunk4);
        chunks.add(chunk4);

        // Save the document (cascades to chunks)
        Document savedDocument = documentRepository.save(document);

        Map<String, Object> response = new HashMap<>();
        response.put("message", "Test data initialized successfully");
        response.put("documentId", savedDocument.getId());
        response.put("chunksCreated", chunks.size());
        response.put("chunks", chunks.stream().map(c -> Map.of(
                "id", c.getId(),
                "text", c.getText(),
                "chunkIndex", c.getChunkIndex()
        )).toList());

        log.info("Created test document with {} chunks", chunks.size());
        return ResponseEntity.ok(response);
    }

    /**
     * Test vector similarity search
     */
    @PostMapping("/search")
    public ResponseEntity<Map<String, Object>> testVectorSearch(@RequestParam(defaultValue = "3") int limit) {
        log.info("Testing vector similarity search with limit={}", limit);

        // Create a query embedding similar to chunk 2 (deep learning)
        float[] queryEmbedding = generateSyntheticEmbedding(2);
        String queryEmbeddingStr = embeddingToString(queryEmbedding);

        // Search for similar chunks
        List<Chunk> similarChunks = chunkRepository.findTopKSimilarChunks(queryEmbeddingStr, limit);

        Map<String, Object> response = new HashMap<>();
        response.put("queryEmbedding", queryEmbeddingStr);
        response.put("limit", limit);
        response.put("resultsCount", similarChunks.size());
        response.put("results", similarChunks.stream().map(chunk -> Map.of(
                "id", chunk.getId(),
                "documentId", chunk.getDocument().getId(),
                "text", chunk.getText(),
                "chunkIndex", chunk.getChunkIndex(),
                "pageStart", chunk.getPageStart(),
                "pageEnd", chunk.getPageEnd()
        )).toList());

        log.info("Found {} similar chunks", similarChunks.size());
        return ResponseEntity.ok(response);
    }

    /**
     * Get all chunks in the database
     */
    @GetMapping("/chunks")
    public ResponseEntity<Map<String, Object>> getAllChunks() {
        List<Chunk> chunks = chunkRepository.findAll();

        Map<String, Object> response = new HashMap<>();
        response.put("totalChunks", chunks.size());
        response.put("chunks", chunks.stream().map(chunk -> Map.of(
                "id", chunk.getId(),
                "documentId", chunk.getDocument().getId(),
                "text", chunk.getText(),
                "chunkIndex", chunk.getChunkIndex(),
                "embeddingDimension", chunk.getEmbedding().length
        )).toList());

        return ResponseEntity.ok(response);
    }

    /**
     * Clear all test data
     */
    @DeleteMapping("/clear")
    public ResponseEntity<Map<String, String>> clearTestData() {
        log.info("Clearing all test data...");

        long chunkCount = chunkRepository.count();
        long documentCount = documentRepository.count();

        chunkRepository.deleteAll();
        documentRepository.deleteAll();

        Map<String, String> response = new HashMap<>();
        response.put("message", "Test data cleared successfully");
        response.put("chunksDeleted", String.valueOf(chunkCount));
        response.put("documentsDeleted", String.valueOf(documentCount));

        log.info("Deleted {} chunks and {} documents", chunkCount, documentCount);
        return ResponseEntity.ok(response);
    }

    /**
     * Generate a synthetic 384-dimensional embedding for testing.
     * In production, this would come from the embedding model.
     *
     * @param seed Seed value to generate different but deterministic embeddings
     */
    private float[] generateSyntheticEmbedding(int seed) {
        Random random = new Random(seed);
        float[] embedding = new float[384]; // Match the embedding dimension

        for (int i = 0; i < 384; i++) {
            // Generate values between -1 and 1
            embedding[i] = (random.nextFloat() * 2.0f) - 1.0f;
        }

        // Normalize the embedding to unit length (common for embeddings)
        float norm = 0.0f;
        for (float v : embedding) {
            norm += v * v;
        }
        norm = (float) Math.sqrt(norm);

        for (int i = 0; i < embedding.length; i++) {
            embedding[i] /= norm;
        }

        return embedding;
    }

    /**
     * Helper method to convert float array to pgvector string format for queries.
     * This is needed for the repository query parameter.
     */
    private String embeddingToString(float[] embedding) {
        if (embedding == null || embedding.length == 0) {
            return null;
        }
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < embedding.length; i++) {
            if (i > 0) {
                sb.append(",");
            }
            sb.append(embedding[i]);
        }
        sb.append("]");
        return sb.toString();
    }

    // ==================== Phase 5 Test Endpoints ====================

    /**
     * Test the EmbeddingClient by embedding a single text.
     * Demonstrates calling Python /embed endpoint from Java.
     */
    @PostMapping("/embed")
    public ResponseEntity<Map<String, Object>> testEmbed(@RequestParam(defaultValue = "What is machine learning?") String text) {
        log.info("Testing EmbeddingClient with text: {}", text);

        try {
            float[] embedding = embeddingClient.embedSingle(text);
            String vectorStr = EmbeddingClient.toPgVectorFormat(embedding);

            Map<String, Object> response = new HashMap<>();
            response.put("text", text);
            response.put("dimension", embedding.length);
            response.put("embeddingPreview", vectorStr.substring(0, Math.min(100, vectorStr.length())) + "...");
            response.put("embeddingFull", vectorStr);

            log.info("Successfully generated embedding with {} dimensions", embedding.length);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("Failed to generate embedding: {}", e.getMessage());
            return ResponseEntity.internalServerError().body(Map.of(
                    "error", e.getMessage(),
                    "text", text
            ));
        }
    }

    /**
     * Test the full Phase 5 flow:
     * 1. Embed query text using EmbeddingClient
     * 2. Search for similar chunks using findNearestChunks
     *
     * This demonstrates the complete RAG retrieval pipeline.
     */
    @PostMapping("/semantic-search")
    public ResponseEntity<Map<String, Object>> testSemanticSearch(
            @RequestParam(defaultValue = "How do neural networks work?") String query,
            @RequestParam(defaultValue = "5") int limit) {
        log.info("Testing semantic search with query: '{}', limit: {}", query, limit);

        try {
            // Step 1: Generate embedding for the query
            float[] queryEmbedding = embeddingClient.embedSingle(query);
            String vectorStr = EmbeddingClient.toPgVectorFormat(queryEmbedding);

            // Step 2: Get all document IDs (in a real app, you might filter these)
            List<Long> documentIds = documentRepository.findAll().stream()
                    .map(Document::getId)
                    .toList();

            if (documentIds.isEmpty()) {
                return ResponseEntity.ok(Map.of(
                        "message", "No documents in database. Run /api/test/vector/init first.",
                        "query", query
                ));
            }

            // Step 3: Search for similar chunks
            List<Chunk> similarChunks = chunkRepository.findNearestChunks(documentIds, vectorStr, limit);

            Map<String, Object> response = new HashMap<>();
            response.put("query", query);
            response.put("embeddingDimension", queryEmbedding.length);
            response.put("documentsSearched", documentIds.size());
            response.put("resultsCount", similarChunks.size());
            response.put("results", similarChunks.stream().map(chunk -> {
                Map<String, Object> chunkInfo = new HashMap<>();
                chunkInfo.put("id", chunk.getId());
                chunkInfo.put("documentId", chunk.getDocument().getId());
                chunkInfo.put("documentTitle", chunk.getDocument().getTitle());
                chunkInfo.put("text", chunk.getText());
                chunkInfo.put("chunkIndex", chunk.getChunkIndex());
                chunkInfo.put("pageStart", chunk.getPageStart());
                chunkInfo.put("pageEnd", chunk.getPageEnd());
                return chunkInfo;
            }).toList());

            log.info("Found {} similar chunks for query", similarChunks.size());
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("Semantic search failed: {}", e.getMessage(), e);
            return ResponseEntity.internalServerError().body(Map.of(
                    "error", e.getMessage(),
                    "query", query
            ));
        }
    }

    /**
     * Test findTopKSimilarChunks with real embeddings (search all documents)
     */
    @PostMapping("/search-all")
    public ResponseEntity<Map<String, Object>> testSearchAll(
            @RequestParam(defaultValue = "artificial intelligence") String query,
            @RequestParam(defaultValue = "3") int limit) {
        log.info("Testing search-all with query: '{}', limit: {}", query, limit);

        try {
            float[] queryEmbedding = embeddingClient.embedSingle(query);
            String vectorStr = EmbeddingClient.toPgVectorFormat(queryEmbedding);

            List<Chunk> similarChunks = chunkRepository.findTopKSimilarChunks(vectorStr, limit);

            Map<String, Object> response = new HashMap<>();
            response.put("query", query);
            response.put("limit", limit);
            response.put("resultsCount", similarChunks.size());
            response.put("results", similarChunks.stream().map(chunk -> Map.of(
                    "id", chunk.getId(),
                    "documentId", chunk.getDocument().getId(),
                    "text", chunk.getText(),
                    "chunkIndex", chunk.getChunkIndex()
            )).toList());

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("Search-all failed: {}", e.getMessage());
            return ResponseEntity.internalServerError().body(Map.of(
                    "error", e.getMessage(),
                    "query", query
            ));
        }
    }

    /**
     * Health check for the test controller
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of(
                "status", "UP",
                "message", "Vector test controller is ready"
        ));
    }
}
