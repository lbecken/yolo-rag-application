package com.rag.app.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.Type;

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
     * Hibernate uses VectorType to convert between float[] and PostgreSQL vector type.
     */
    @Column(name = "embedding", nullable = false, columnDefinition = "vector(384)")
    @Type(VectorType.class)
    private float[] embedding;

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

    // Note: VectorType handles conversion between float[] and PostgreSQL vector automatically
    // No need for manual conversion methods anymore
}
