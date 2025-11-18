package com.rag.app.controller;

import com.rag.app.dto.DocumentDTO;
import com.rag.app.dto.DocumentUploadResponse;
import com.rag.app.model.Document;
import com.rag.app.repository.DocumentRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;

import java.io.IOException;
import java.util.List;
import java.util.Map;

/**
 * Controller for document upload and management operations.
 * Handles PDF uploads by forwarding them to the Python ingestion service.
 */
@RestController
@RequestMapping("/api/documents")
public class DocumentController {

    private static final Logger logger = LoggerFactory.getLogger(DocumentController.class);

    private final WebClient webClient;
    private final DocumentRepository documentRepository;

    public DocumentController(
            WebClient.Builder webClientBuilder,
            @Value("${python.service.url}") String pythonServiceUrl,
            DocumentRepository documentRepository) {
        this.webClient = webClientBuilder
                .baseUrl(pythonServiceUrl)
                .build();
        this.documentRepository = documentRepository;
        logger.info("DocumentController initialized with Python service URL: {}", pythonServiceUrl);
    }

    /**
     * Upload a PDF document for ingestion.
     * Forwards the file to Python service's /ingest endpoint.
     *
     * @param file The PDF file to upload
     * @param title Optional title for the document (defaults to filename)
     * @return Response with document ID and chunk count
     */
    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<DocumentUploadResponse> uploadDocument(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "title", required = false) String title) {

        logger.info("Received document upload request: filename={}, size={} bytes",
                file.getOriginalFilename(), file.getSize());

        // Validate file type
        String filename = file.getOriginalFilename();
        if (filename == null || !filename.toLowerCase().endsWith(".pdf")) {
            logger.warn("Invalid file type: {}", filename);
            return ResponseEntity.badRequest()
                    .body(DocumentUploadResponse.builder()
                            .status("error")
                            .title("File must be a PDF")
                            .build());
        }

        try {
            // Build multipart request for Python service
            MultipartBodyBuilder bodyBuilder = new MultipartBodyBuilder();

            // Add file part
            bodyBuilder.part("file", new ByteArrayResource(file.getBytes()) {
                @Override
                public String getFilename() {
                    return file.getOriginalFilename();
                }
            }).contentType(MediaType.APPLICATION_PDF);

            // Add title if provided
            if (title != null && !title.isBlank()) {
                bodyBuilder.part("title", title);
            }

            logger.info("Forwarding document to Python ingestion service...");

            // Forward to Python /ingest endpoint
            Map<String, Object> pythonResponse = webClient.post()
                    .uri("/ingest")
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(BodyInserters.fromMultipartData(bodyBuilder.build()))
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();

            if (pythonResponse == null) {
                logger.error("No response from Python service");
                return ResponseEntity.internalServerError()
                        .body(DocumentUploadResponse.builder()
                                .status("error")
                                .title("No response from ingestion service")
                                .build());
            }

            // Map Python response to our DTO
            DocumentUploadResponse response = DocumentUploadResponse.builder()
                    .status((String) pythonResponse.get("status"))
                    .documentId(((Number) pythonResponse.get("document_id")).longValue())
                    .numChunks(((Number) pythonResponse.get("num_chunks")).intValue())
                    .title((String) pythonResponse.get("title"))
                    .build();

            logger.info("Document ingested successfully: id={}, chunks={}",
                    response.getDocumentId(), response.getNumChunks());

            return ResponseEntity.ok(response);

        } catch (WebClientResponseException e) {
            logger.error("Python service returned error: {} - {}",
                    e.getStatusCode(), e.getResponseBodyAsString());
            return ResponseEntity.status(e.getStatusCode())
                    .body(DocumentUploadResponse.builder()
                            .status("error")
                            .title("Ingestion failed: " + e.getResponseBodyAsString())
                            .build());
        } catch (IOException e) {
            logger.error("Failed to read uploaded file", e);
            return ResponseEntity.internalServerError()
                    .body(DocumentUploadResponse.builder()
                            .status("error")
                            .title("Failed to process uploaded file")
                            .build());
        } catch (Exception e) {
            logger.error("Unexpected error during document upload", e);
            return ResponseEntity.internalServerError()
                    .body(DocumentUploadResponse.builder()
                            .status("error")
                            .title("Upload failed: " + e.getMessage())
                            .build());
        }
    }

    /**
     * List all ingested documents.
     *
     * @return List of documents with their metadata
     */
    @GetMapping
    public ResponseEntity<List<DocumentDTO>> listDocuments() {
        logger.info("Listing all documents");

        List<Document> documents = documentRepository.findAll();

        List<DocumentDTO> documentDTOs = documents.stream()
                .map(doc -> DocumentDTO.builder()
                        .id(doc.getId())
                        .title(doc.getTitle())
                        .filename(doc.getFilename())
                        .createdAt(doc.getCreatedAt())
                        .chunkCount(doc.getChunks() != null ? doc.getChunks().size() : 0)
                        .build())
                .toList();

        logger.info("Returning {} documents", documentDTOs.size());
        return ResponseEntity.ok(documentDTOs);
    }

    /**
     * Get a single document by ID.
     *
     * @param id Document ID
     * @return Document details or 404 if not found
     */
    @GetMapping("/{id}")
    public ResponseEntity<DocumentDTO> getDocument(@PathVariable Long id) {
        logger.info("Getting document with id: {}", id);

        return documentRepository.findById(id)
                .map(doc -> {
                    DocumentDTO dto = DocumentDTO.builder()
                            .id(doc.getId())
                            .title(doc.getTitle())
                            .filename(doc.getFilename())
                            .createdAt(doc.getCreatedAt())
                            .chunkCount(doc.getChunks() != null ? doc.getChunks().size() : 0)
                            .build();
                    return ResponseEntity.ok(dto);
                })
                .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Delete a document by ID.
     *
     * @param id Document ID
     * @return 204 No Content if deleted, 404 if not found
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteDocument(@PathVariable Long id) {
        logger.info("Deleting document with id: {}", id);

        if (!documentRepository.existsById(id)) {
            logger.warn("Document not found: {}", id);
            return ResponseEntity.notFound().build();
        }

        documentRepository.deleteById(id);
        logger.info("Document deleted: {}", id);
        return ResponseEntity.noContent().build();
    }
}
