package com.rag.app.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Response DTO for document upload operation.
 * Maps to Python service's IngestResponse.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DocumentUploadResponse {

    private String status;
    private Long documentId;
    private Integer numChunks;
    private String title;
}
