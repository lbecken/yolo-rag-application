package com.rag.app.dto;

import java.util.List;

/**
 * Request DTO for the Python /embed endpoint.
 * Matches the EmbedRequest model in Python service.
 */
public class EmbedRequest {

    private List<String> texts;

    public EmbedRequest() {
    }

    public EmbedRequest(List<String> texts) {
        this.texts = texts;
    }

    public List<String> getTexts() {
        return texts;
    }

    public void setTexts(List<String> texts) {
        this.texts = texts;
    }
}
