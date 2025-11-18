package com.rag.app.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * Entity representing a text chunk from a document with its embedding.
 * Chunks are created by splitting documents into smaller pieces for semantic search.
 */
@Entity
@Table(name = "chunks")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Chunk {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "document_id", nullable = false)
    private Document document;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String text;

    @Column(name = "page_start", nullable = false)
    private Integer pageStart;

    @Column(name = "page_end", nullable = false)
    private Integer pageEnd;

    @Column(name = "chunk_index", nullable = false)
    private Integer chunkIndex;

    /**
     * The embedding vector stored as a pgvector type.
     * We store it as a String in PostgreSQL's vector format: '[0.1, 0.2, ...]'
     * and convert to/from float[] in the application layer.
     */
    @Column(name = "embedding", nullable = false, columnDefinition = "vector(384)")
    private String embedding;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    /**
     * Automatically set the created_at timestamp before persisting
     */
    @PrePersist
    protected void onCreate() {
        if (createdAt == null) {
            createdAt = LocalDateTime.now();
        }
    }

    /**
     * Convert a float array to pgvector string format: '[0.1, 0.2, ...]'
     */
    public static String embeddingToString(float[] embedding) {
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

    /**
     * Convert a pgvector string format to float array
     */
    public static float[] stringToEmbedding(String embeddingStr) {
        if (embeddingStr == null || embeddingStr.isEmpty()) {
            return null;
        }
        // Remove brackets and split by comma
        String cleaned = embeddingStr.replaceAll("[\\[\\] ]", "");
        String[] parts = cleaned.split(",");
        float[] result = new float[parts.length];
        for (int i = 0; i < parts.length; i++) {
            result[i] = Float.parseFloat(parts[i]);
        }
        return result;
    }

    /**
     * Get embedding as float array
     */
    public float[] getEmbeddingArray() {
        return stringToEmbedding(this.embedding);
    }

    /**
     * Set embedding from float array
     */
    public void setEmbeddingArray(float[] embeddingArray) {
        this.embedding = embeddingToString(embeddingArray);
    }
}
