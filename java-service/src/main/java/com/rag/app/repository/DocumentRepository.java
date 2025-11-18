package com.rag.app.repository;

import com.rag.app.model.Document;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * Repository for Document entity operations.
 */
@Repository
public interface DocumentRepository extends JpaRepository<Document, Long> {

    /**
     * Find a document by its filename
     */
    Optional<Document> findByFilename(String filename);

    /**
     * Check if a document with the given filename exists
     */
    boolean existsByFilename(String filename);
}
