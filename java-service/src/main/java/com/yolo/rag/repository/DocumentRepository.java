package com.yolo.rag.repository;

import com.yolo.rag.entity.Document;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface DocumentRepository extends JpaRepository<Document, Long> {

    Optional<Document> findByFileHash(String fileHash);

    List<Document> findByStatus(Document.DocumentStatus status);

    List<Document> findByTitleContainingIgnoreCase(String title);
}
