"""
Tests for embedding_config.py
"""
import pytest
import os
from embedding_config import EmbeddingProvider


class TestEmbeddingProvider:
    def test_default_provider(self):
        """Test default provider"""
        # Remove OPENAI_API_KEY if it exists
        original_key = os.environ.pop('OPENAI_API_KEY', None)
        try:
            embeddings = EmbeddingProvider.get_embeddings()
            assert embeddings is not None
        finally:
            if original_key:
                os.environ['OPENAI_API_KEY'] = original_key
    
    def test_sentence_transformers_provider(self):
        """Test sentence-transformers provider"""
        embeddings = EmbeddingProvider.get_embeddings("sentence-transformers")
        assert embeddings is not None
    
    def test_auto_detection(self):
        """Test auto-detect"""
        embeddings = EmbeddingProvider.get_embeddings("auto")
        assert embeddings is not None
    
    def test_openai_without_key_fails(self):
        """OpenAI without key should fail"""
        original_key = os.environ.pop('OPENAI_API_KEY', None)
        try:
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                EmbeddingProvider.get_embeddings("openai")
        finally:
            if original_key:
                os.environ['OPENAI_API_KEY'] = original_key
    
    def test_invalid_provider_fails(self):
        """Invalid provider should fail"""
        with pytest.raises(ValueError):
            EmbeddingProvider.get_embeddings("invalid_provider")
    
    def test_get_available_providers(self):
        """Test provider listing"""
        providers = EmbeddingProvider.get_available_providers()
        assert "sentence-transformers" in providers
        assert "huggingface" in providers
        assert providers["sentence-transformers"]["available"] is True
