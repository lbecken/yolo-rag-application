package com.rag.app.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Entity representing a PDF document in the RAG system.
 * Each document can have multiple chunks with embeddings.
 */
@Entity
@Table(name = "documents")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Document {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 500)
    private String title;

    @Column(nullable = false, length = 500, unique = true)
    private String filename;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @OneToMany(mappedBy = "document", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    @Builder.Default
    private List<Chunk> chunks = new ArrayList<>();

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
     * Helper method to add a chunk to this document
     */
    public void addChunk(Chunk chunk) {
        chunks.add(chunk);
        chunk.setDocument(this);
    }

    /**
     * Helper method to remove a chunk from this document
     */
    public void removeChunk(Chunk chunk) {
        chunks.remove(chunk);
        chunk.setDocument(null);
    }
}
