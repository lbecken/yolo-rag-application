"""
Tests for the /embed endpoint
Phase 4: Python Embedding API
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from model_config import EMBEDDING_DIMENSION


# Create test client
client = TestClient(app)


class TestEmbedEndpoint:
    """Test cases for the /embed endpoint"""

    def test_embed_single_text(self):
        """Test embedding a single text string"""
        request_data = {
            "texts": ["Hello, world!"]
        }

        response = client.post("/embed", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "vectors" in data
        assert "dimension" in data
        assert "num_texts" in data

        # Check dimension matches config
        assert data["dimension"] == EMBEDDING_DIMENSION

        # Check we got one vector
        assert data["num_texts"] == 1
        assert len(data["vectors"]) == 1

        # Check vector dimension
        assert len(data["vectors"][0]) == EMBEDDING_DIMENSION

    def test_embed_multiple_texts(self):
        """Test embedding multiple text strings"""
        request_data = {
            "texts": [
                "First text to embed",
                "Second text to embed",
                "Third text to embed"
            ]
        }

        response = client.post("/embed", json=request_data)

        assert response.status_code == 200
        data = response.json()

        # Check we got three vectors
        assert data["num_texts"] == 3
        assert len(data["vectors"]) == 3

        # Check each vector has correct dimension
        for vector in data["vectors"]:
            assert len(vector) == EMBEDDING_DIMENSION

    def test_embed_empty_texts_returns_error(self):
        """Test that empty texts list returns an error"""
        request_data = {
            "texts": []
        }

        response = client.post("/embed", json=request_data)

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "No texts provided" in data["detail"]

    def test_embed_different_texts_produce_different_vectors(self):
        """Test that different texts produce different embeddings"""
        request_data = {
            "texts": [
                "The cat sat on the mat",
                "Financial regulations and banking laws"
            ]
        }

        response = client.post("/embed", json=request_data)

        assert response.status_code == 200
        data = response.json()

        vector1 = data["vectors"][0]
        vector2 = data["vectors"][1]

        # Vectors should be different
        assert vector1 != vector2

    def test_embed_similar_texts_produce_similar_vectors(self):
        """Test that similar texts produce similar embeddings (cosine similarity)"""
        import numpy as np

        request_data = {
            "texts": [
                "The quick brown fox jumps over the lazy dog",
                "The fast brown fox leaps over the sleepy dog"
            ]
        }

        response = client.post("/embed", json=request_data)

        assert response.status_code == 200
        data = response.json()

        vector1 = np.array(data["vectors"][0])
        vector2 = np.array(data["vectors"][1])

        # Calculate cosine similarity
        cosine_sim = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))

        # Similar sentences should have high cosine similarity (> 0.8)
        assert cosine_sim > 0.8

    def test_embed_vectors_are_normalized(self):
        """Test that embedding vectors are properly formatted floats"""
        request_data = {
            "texts": ["Test normalization"]
        }

        response = client.post("/embed", json=request_data)

        assert response.status_code == 200
        data = response.json()

        vector = data["vectors"][0]

        # Check all values are floats
        for value in vector:
            assert isinstance(value, float)

    def test_embed_missing_texts_field(self):
        """Test that missing texts field returns validation error"""
        request_data = {}

        response = client.post("/embed", json=request_data)

        # FastAPI returns 422 for validation errors
        assert response.status_code == 422


def test_embed_health_check():
    """Verify health endpoint still works"""
    response = client.get("/health")
    assert response.status_code == 200


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
