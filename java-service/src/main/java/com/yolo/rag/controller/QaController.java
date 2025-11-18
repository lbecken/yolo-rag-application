package com.yolo.rag.controller;

import com.yolo.rag.dto.QaRequest;
import com.yolo.rag.dto.QaResponse;
import com.yolo.rag.service.QaService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/qa")
@RequiredArgsConstructor
@Slf4j
public class QaController {

    private final QaService qaService;

    /**
     * Answer a question using RAG pipeline.
     *
     * @param request Contains the question and list of document IDs to search
     * @return Answer with citations from the retrieved chunks
     */
    @PostMapping
    public ResponseEntity<QaResponse> answerQuestion(@Valid @RequestBody QaRequest request) {
        log.info("Received QA request for question: {}", request.getQuestion());
        log.info("Document IDs: {}", request.getDocumentIds());

        QaResponse response = qaService.answerQuestion(
                request.getQuestion(),
                request.getDocumentIds()
        );

        log.info("Returning answer with {} citations", response.getCitations().size());
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
