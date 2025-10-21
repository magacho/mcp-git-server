"""
Tests for token_utils.py
"""
import pytest
from token_utils import contar_tokens, estimar_custo_embeddings


class TestCountTokens:
    def test_count_short_text(self):
        """Test with short text"""
        text = "Hello world"
        tokens = contar_tokens(text, metodo="local")
        assert tokens > 0
        assert tokens < 10
    
    def test_count_empty_text(self):
        """Test with empty text"""
        tokens = contar_tokens("", metodo="local")
        assert tokens == 0
    
    def test_count_long_text(self):
        """Test with long text"""
        text = "word " * 1000
        tokens = contar_tokens(text, metodo="local")
        assert tokens > 500
    
    def test_local_method(self):
        """Test local method"""
        text = "This is a test"
        tokens = contar_tokens(text, metodo="local")
        assert tokens > 0


class TestEstimateCost:
    def test_openai_cost(self):
        """Test OpenAI cost estimation"""
        cost_info = estimar_custo_embeddings(10000, "openai")
        assert "custo_usd" in cost_info
        assert "custo_brl" in cost_info
        assert cost_info["custo_usd"] > 0
    
    def test_local_cost(self):
        """Test local cost estimation"""
        cost_info = estimar_custo_embeddings(10000, "sentence-transformers")
        assert "nota" in cost_info
        assert "sem custos" in cost_info["nota"].lower()
    
    def test_large_token_count(self):
        """Test with large token count"""
        cost_info = estimar_custo_embeddings(1000000, "openai")
        assert cost_info["custo_usd"] > 0.05
