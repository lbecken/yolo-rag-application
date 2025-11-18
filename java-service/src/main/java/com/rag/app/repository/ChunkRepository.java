package com.rag.app.repository;

import com.rag.app.model.Chunk;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Repository for Chunk entity operations.
 * Includes custom queries for vector similarity search using pgvector.
 */
@Repository
public interface ChunkRepository extends JpaRepository<Chunk, Long> {

    /**
     * Find all chunks for a specific document, ordered by chunk index
     */
    List<Chunk> findByDocumentIdOrderByChunkIndexAsc(Long documentId);

    /**
     * Count chunks for a specific document
     */
    long countByDocumentId(Long documentId);

    /**
     * Find the top K most similar chunks using cosine distance.
     *
     * Uses pgvector's <-> operator for cosine distance.
     * Lower distance = more similar.
     *
     * @param embeddingVector The query embedding in pgvector format: '[0.1, 0.2, ...]'
     * @param limit Maximum number of results to return
     * @return List of chunks ordered by similarity (most similar first)
     */
    @Query(value = """
        SELECT c.*
        FROM chunks c
        ORDER BY c.embedding <-> CAST(:embeddingVector AS vector)
        LIMIT :limit
        """, nativeQuery = true)
    List<Chunk> findTopKSimilarChunks(
        @Param("embeddingVector") String embeddingVector,
        @Param("limit") int limit
    );

    /**
     * Find the top K most similar chunks within a specific document.
     *
     * @param documentId The document to search within
     * @param embeddingVector The query embedding in pgvector format
     * @param limit Maximum number of results to return
     * @return List of chunks ordered by similarity (most similar first)
     */
    @Query(value = """
        SELECT c.*
        FROM chunks c
        WHERE c.document_id = :documentId
        ORDER BY c.embedding <-> CAST(:embeddingVector AS vector)
        LIMIT :limit
        """, nativeQuery = true)
    List<Chunk> findTopKSimilarChunksInDocument(
        @Param("documentId") Long documentId,
        @Param("embeddingVector") String embeddingVector,
        @Param("limit") int limit
    );

    /**
     * Find similar chunks with a distance threshold.
     * Only returns chunks with cosine distance less than the threshold.
     *
     * @param embeddingVector The query embedding in pgvector format
     * @param threshold Maximum distance threshold (0.0 to 2.0 for cosine)
     * @param limit Maximum number of results to return
     * @return List of chunks within the distance threshold
     */
    @Query(value = """
        SELECT c.*
        FROM chunks c
        WHERE (c.embedding <-> CAST(:embeddingVector AS vector)) < :threshold
        ORDER BY c.embedding <-> CAST(:embeddingVector AS vector)
        LIMIT :limit
        """, nativeQuery = true)
    List<Chunk> findSimilarChunksWithinThreshold(
        @Param("embeddingVector") String embeddingVector,
        @Param("threshold") double threshold,
        @Param("limit") int limit
    );

    /**
     * Find the top K nearest chunks from specific documents using cosine distance.
     *
     * This method filters chunks by a list of document IDs and returns the most
     * similar chunks based on vector similarity.
     *
     * @param documentIds List of document IDs to search within
     * @param embeddingVector The query embedding in pgvector format: '[0.1, 0.2, ...]'
     * @param limit Maximum number of results to return (k)
     * @return List of chunks ordered by similarity (most similar first)
     */
    @Query(value = """
        SELECT c.*
        FROM chunks c
        WHERE c.document_id IN :documentIds
        ORDER BY c.embedding <-> CAST(:embeddingVector AS vector)
        LIMIT :limit
        """, nativeQuery = true)
    List<Chunk> findNearestChunks(
        @Param("documentIds") List<Long> documentIds,
        @Param("embeddingVector") String embeddingVector,
        @Param("limit") int limit
    );
}
