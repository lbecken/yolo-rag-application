package com.yolo.rag.repository;

import com.yolo.rag.entity.Chunk;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ChunkRepository extends JpaRepository<Chunk, Long> {

    List<Chunk> findByDocumentId(Long documentId);

    List<Chunk> findByDocumentIdOrderByChunkIndex(Long documentId);

    /**
     * Find the nearest chunks to a query embedding using pgvector cosine distance.
     * The embedding parameter should be formatted as a pgvector literal (e.g., "[0.1,0.2,...]").
     *
     * @param embedding   The query embedding as a pgvector literal string
     * @param documentIds List of document IDs to search within
     * @param limit       Maximum number of chunks to return
     * @return List of chunks ordered by similarity (closest first)
     */
    @Query(value = """
            SELECT c.* FROM chunks c
            WHERE c.document_id IN :documentIds
            ORDER BY c.embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
            """, nativeQuery = true)
    List<Chunk> findNearestChunks(
            @Param("embedding") String embedding,
            @Param("documentIds") List<Long> documentIds,
            @Param("limit") int limit
    );

    /**
     * Find the nearest chunks with similarity score using pgvector cosine distance.
     * Returns chunks with their cosine similarity score.
     */
    @Query(value = """
            SELECT c.*,
                   1 - (c.embedding <=> CAST(:embedding AS vector)) as similarity
            FROM chunks c
            WHERE c.document_id IN :documentIds
            ORDER BY c.embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
            """, nativeQuery = true)
    List<Object[]> findNearestChunksWithScore(
            @Param("embedding") String embedding,
            @Param("documentIds") List<Long> documentIds,
            @Param("limit") int limit
    );

    /**
     * Find chunks by document ID with pagination support.
     */
    @Query("SELECT c FROM Chunk c WHERE c.document.id = :documentId ORDER BY c.chunkIndex")
    List<Chunk> findChunksByDocumentId(@Param("documentId") Long documentId);

    /**
     * Count chunks for a document.
     */
    long countByDocumentId(Long documentId);
}
