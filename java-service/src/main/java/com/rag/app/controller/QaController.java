package com.rag.app.controller;

import com.rag.app.dto.QaRequest;
import com.rag.app.dto.QaResponse;
import com.rag.app.service.QaService;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/qa")
public class QaController {

    private static final Logger logger = LoggerFactory.getLogger(QaController.class);

    private final QaService qaService;

    public QaController(QaService qaService) {
        this.qaService = qaService;
    }

    /**
     * Answer a question using RAG pipeline.
     *
     * @param request Contains the question and list of document IDs to search
     * @return Answer with citations from the retrieved chunks
     */
    @PostMapping
    public ResponseEntity<QaResponse> answerQuestion(@Valid @RequestBody QaRequest request) {
        logger.info("Received QA request for question: {}", request.getQuestion());
        logger.info("Document IDs: {}", request.getDocumentIds());

        QaResponse response = qaService.answerQuestion(
                request.getQuestion(),
                request.getDocumentIds()
        );

        logger.info("Returning answer with {} citations", response.getCitations().size());
        return ResponseEntity.ok(response);
    }

    /**
     * Health check endpoint for the QA service.
     */
    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("QA Service is running");
    }
}
