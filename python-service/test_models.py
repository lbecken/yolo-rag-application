#!/usr/bin/env python3
"""
Test script for Phase 1: Local LLM & Embeddings Model Setup

This script tests both the embedding model and the chat model to ensure
they are properly configured and working.

Usage:
    python test_models.py

Expected output:
    1. A sample answer from the local LLM via Ollama
    2. An embedding vector with the correct dimensions
"""

import sys
from typing import List
import numpy as np

# Import model configuration
from model_config import (
    EMBEDDING_MODEL_NAME,
    EMBEDDING_DIMENSION,
    LLM_MODEL_NAME,
    OLLAMA_BASE_URL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
)


def test_embedding_model():
    """Test the sentence-transformers embedding model."""
    print("=" * 80)
    print("TESTING EMBEDDING MODEL")
    print("=" * 80)
    print(f"Model: {EMBEDDING_MODEL_NAME}")
    print(f"Expected dimension: {EMBEDDING_DIMENSION}")
    print()

    try:
        from sentence_transformers import SentenceTransformer

        print("Loading embedding model...")
        # Load the model (will download if not cached)
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print("✓ Model loaded successfully!")
        print()

        # Test with a sample sentence
        test_text = "This is a test sentence for generating embeddings."
        print(f"Test text: '{test_text}'")
        print()

        print("Generating embedding...")
        embedding = model.encode(test_text)

        # Verify the embedding
        print(f"✓ Embedding generated successfully!")
        print(f"  - Vector type: {type(embedding)}")
        print(f"  - Vector shape: {embedding.shape}")
        print(f"  - Vector dimension: {len(embedding)}")
        print(f"  - Expected dimension: {EMBEDDING_DIMENSION}")
        print()

        # Verify dimension matches configuration
        if len(embedding) == EMBEDDING_DIMENSION:
            print("✓ Dimension matches configuration!")
        else:
            print(
                f"✗ WARNING: Dimension mismatch! Expected {EMBEDDING_DIMENSION}, got {len(embedding)}"
            )
        print()

        # Show a sample of the embedding vector
        print("First 10 values of the embedding vector:")
        print(embedding[:10])
        print()

        # Additional statistics
        print("Embedding statistics:")
        print(f"  - Min value: {np.min(embedding):.4f}")
        print(f"  - Max value: {np.max(embedding):.4f}")
        print(f"  - Mean value: {np.mean(embedding):.4f}")
        print(f"  - Std deviation: {np.std(embedding):.4f}")
        print()

        return True

    except Exception as e:
        print(f"✗ Error testing embedding model: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_llm_model():
    """Test the Ollama chat model."""
    print("=" * 80)
    print("TESTING LLM (CHAT) MODEL")
    print("=" * 80)
    print(f"Model: {LLM_MODEL_NAME}")
    print(f"Ollama URL: {OLLAMA_BASE_URL}")
    print()

    try:
        import ollama

        # Configure the client
        client = ollama.Client(host=OLLAMA_BASE_URL)

        # Check if the model is available
        print("Checking available models...")
        try:
            models = client.list()
            available_models = [model["name"] for model in models.get("models", [])]
            print(f"Available models: {available_models}")
            print()

            if LLM_MODEL_NAME not in available_models:
                print(
                    f"⚠ Model '{LLM_MODEL_NAME}' not found in available models."
                )
                print(f"Please pull it first with: docker exec rag-ollama ollama pull {LLM_MODEL_NAME}")
                print("Or run: docker-compose exec ollama ollama pull {LLM_MODEL_NAME}")
                print()
                print("Attempting to pull the model now...")
                # Try to pull the model
                client.pull(LLM_MODEL_NAME)
                print(f"✓ Model '{LLM_MODEL_NAME}' pulled successfully!")
                print()
        except Exception as e:
            print(f"Note: Could not list/pull models: {e}")
            print("This is okay if the model is already available.")
            print()

        # Test with a sample prompt
        test_prompt = "Explain what Retrieval-Augmented Generation (RAG) is in one short paragraph."
        print(f"Test prompt: '{test_prompt}'")
        print()

        print("Generating response...")
        print("(This may take a few moments on first run)")
        print()

        response = client.generate(
            model=LLM_MODEL_NAME,
            prompt=test_prompt,
            options={
                "temperature": DEFAULT_TEMPERATURE,
                "num_predict": DEFAULT_MAX_TOKENS,
            },
        )

        answer = response["response"]
        print("✓ Response generated successfully!")
        print()
        print("-" * 80)
        print("LLM RESPONSE:")
        print("-" * 80)
        print(answer)
        print("-" * 80)
        print()

        # Show some statistics about the response
        print("Response statistics:")
        print(f"  - Length (characters): {len(answer)}")
        print(f"  - Length (words): {len(answer.split())}")
        print(f"  - Model used: {response.get('model', 'unknown')}")
        print(
            f"  - Total duration: {response.get('total_duration', 0) / 1e9:.2f}s"
        )
        print()

        return True

    except Exception as e:
        print(f"✗ Error testing LLM model: {e}")
        import traceback

        traceback.print_exc()
        print()
        print("TROUBLESHOOTING:")
        print("1. Make sure Ollama service is running:")
        print("   docker-compose up -d ollama")
        print()
        print("2. Pull the model manually:")
        print(f"   docker-compose exec ollama ollama pull {LLM_MODEL_NAME}")
        print()
        print("3. Check Ollama is accessible:")
        print(f"   curl {OLLAMA_BASE_URL}/api/tags")
        print()
        return False


def main():
    """Run all model tests."""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "PHASE 1: MODEL TESTING" + " " * 35 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # Test embedding model
    embedding_success = test_embedding_model()

    # Test LLM model
    llm_success = test_llm_model()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Embedding Model: {'✓ PASS' if embedding_success else '✗ FAIL'}")
    print(f"LLM Model:       {'✓ PASS' if llm_success else '✗ FAIL'}")
    print()

    if embedding_success and llm_success:
        print("✓ All tests passed! Phase 1 is complete.")
        print()
        print("Model Configuration:")
        print(f"  EMBEDDING_MODEL_NAME = '{EMBEDDING_MODEL_NAME}'")
        print(f"  LLM_MODEL_NAME = '{LLM_MODEL_NAME}'")
        print()
        print("You can now proceed to Phase 2: PDF Ingestion.")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
