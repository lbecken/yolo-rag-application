package com.yolo.rag.service;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

@Service
@Slf4j
public class EmbeddingClient {

    private final RestTemplate restTemplate;
    private final String embeddingUrl;
    private final String embeddingModel;

    public EmbeddingClient(
            @Value("${rag.embedding.url}") String embeddingUrl,
            @Value("${rag.embedding.model}") String embeddingModel) {
        this.restTemplate = new RestTemplate();
        this.embeddingUrl = embeddingUrl;
        this.embeddingModel = embeddingModel;
    }

    /**
     * Get embedding for a text query.
     *
     * @param text The text to embed
     * @return Array of embedding values
     */
    public float[] getEmbedding(String text) {
        log.debug("Getting embedding for text: {}...", text.substring(0, Math.min(50, text.length())));

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        EmbeddingRequest request = new EmbeddingRequest(embeddingModel, text);
        HttpEntity<EmbeddingRequest> entity = new HttpEntity<>(request, headers);

        try {
            EmbeddingResponse response = restTemplate.postForObject(
                    embeddingUrl,
                    entity,
                    EmbeddingResponse.class
            );

            if (response != null && response.embedding() != null) {
                log.debug("Got embedding with {} dimensions", response.embedding().length);
                return response.embedding();
            }

            throw new RuntimeException("Empty embedding response from Ollama");
        } catch (Exception e) {
            log.error("Failed to get embedding: {}", e.getMessage());
            throw new RuntimeException("Failed to get embedding from Ollama", e);
        }
    }

    /**
     * Convert embedding array to pgvector literal format.
     *
     * @param embedding The embedding array
     * @return String in format "[0.1,0.2,...]"
     */
    public String toPgVectorLiteral(float[] embedding) {
        return "[" + Arrays.stream(toFloatArray(embedding))
                .mapToObj(String::valueOf)
                .collect(Collectors.joining(",")) + "]";
    }

    /**
     * Get embedding and format it as a pgvector literal.
     *
     * @param text The text to embed
     * @return Embedding as pgvector literal string
     */
    public String getEmbeddingAsPgVector(String text) {
        float[] embedding = getEmbedding(text);
        return toPgVectorLiteral(embedding);
    }

    private double[] toFloatArray(float[] floats) {
        double[] doubles = new double[floats.length];
        for (int i = 0; i < floats.length; i++) {
            doubles[i] = floats[i];
        }
        return doubles;
    }

    // Request/Response records for Ollama API
    private record EmbeddingRequest(
            String model,
            String prompt
    ) {}

    private record EmbeddingResponse(
            float[] embedding
    ) {}
}
