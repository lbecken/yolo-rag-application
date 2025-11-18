package com.rag.app.client;

import com.rag.app.dto.EmbedRequest;
import com.rag.app.dto.EmbedResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.Arrays;
import java.util.List;

/**
 * Client for calling the Python embedding service.
 * Provides methods to generate embeddings for text using the /embed endpoint.
 */
@Service
public class EmbeddingClient {

    private static final Logger logger = LoggerFactory.getLogger(EmbeddingClient.class);

    private final WebClient webClient;

    public EmbeddingClient(
            WebClient.Builder webClientBuilder,
            @Value("${python.service.url}") String pythonServiceUrl) {
        this.webClient = webClientBuilder
                .baseUrl(pythonServiceUrl)
                .build();
        logger.info("EmbeddingClient initialized with base URL: {}", pythonServiceUrl);
    }

    /**
     * Generate an embedding for a single text string.
     *
     * @param text The text to embed
     * @return The embedding as a float array (384 dimensions)
     * @throws RuntimeException if the embedding request fails
     */
    public float[] embedSingle(String text) {
        logger.debug("Generating embedding for text of length: {}", text.length());

        EmbedRequest request = new EmbedRequest(List.of(text));

        EmbedResponse response = webClient.post()
                .uri("/embed")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(request)
                .retrieve()
                .bodyToMono(EmbedResponse.class)
                .block();

        if (response == null || response.getVectors() == null || response.getVectors().isEmpty()) {
            throw new RuntimeException("Failed to get embedding response from Python service");
        }

        List<Double> embedding = response.getVectors().get(0);
        float[] result = new float[embedding.size()];
        for (int i = 0; i < embedding.size(); i++) {
            result[i] = embedding.get(i).floatValue();
        }

        logger.debug("Generated embedding with {} dimensions", result.length);
        return result;
    }

    /**
     * Generate embeddings for multiple text strings in batch.
     *
     * @param texts The list of texts to embed
     * @return A list of embeddings, each as a float array (384 dimensions)
     * @throws RuntimeException if the embedding request fails
     */
    public List<float[]> embedBatch(List<String> texts) {
        logger.debug("Generating embeddings for {} texts", texts.size());

        EmbedRequest request = new EmbedRequest(texts);

        EmbedResponse response = webClient.post()
                .uri("/embed")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(request)
                .retrieve()
                .bodyToMono(EmbedResponse.class)
                .block();

        if (response == null || response.getVectors() == null) {
            throw new RuntimeException("Failed to get embedding response from Python service");
        }

        List<float[]> results = response.getVectors().stream()
                .map(vector -> {
                    float[] arr = new float[vector.size()];
                    for (int i = 0; i < vector.size(); i++) {
                        arr[i] = vector.get(i).floatValue();
                    }
                    return arr;
                })
                .toList();

        logger.debug("Generated {} embeddings with {} dimensions each",
                results.size(),
                results.isEmpty() ? 0 : results.get(0).length);
        return results;
    }

    /**
     * Convert a float array embedding to pgvector format string.
     *
     * @param embedding The embedding as a float array
     * @return The embedding in pgvector format: '[0.1, 0.2, ...]'
     */
    public static String toPgVectorFormat(float[] embedding) {
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
}
