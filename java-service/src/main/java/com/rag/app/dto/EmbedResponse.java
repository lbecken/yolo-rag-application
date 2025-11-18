package com.rag.app.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

/**
 * Response DTO from the Python /embed endpoint.
 * Matches the EmbedResponse model in Python service.
 */
public class EmbedResponse {

    private List<List<Double>> vectors;

    private int dimension;

    @JsonProperty("num_texts")
    private int numTexts;

    public EmbedResponse() {
    }

    public List<List<Double>> getVectors() {
        return vectors;
    }

    public void setVectors(List<List<Double>> vectors) {
        this.vectors = vectors;
    }

    public int getDimension() {
        return dimension;
    }

    public void setDimension(int dimension) {
        this.dimension = dimension;
    }

    public int getNumTexts() {
        return numTexts;
    }

    public void setNumTexts(int numTexts) {
        this.numTexts = numTexts;
    }
}
