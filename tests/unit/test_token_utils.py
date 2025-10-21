"""
Tests for token_utils.py
"""
import pytest
from token_utils import count_tokens, estimate_embedding_cost


class TestCountTokens:
    def test_count_short_text(self):
        """Test with short text"""
        text = "Hello world"
        tokens = count_tokens(text, method="local")
        assert tokens > 0
        assert tokens < 10
    
    def test_count_empty_text(self):
        """Test with empty text"""
        tokens = count_tokens("", method="local")
        assert tokens == 0
    
    def test_count_long_text(self):
        """Test with long text"""
        text = "word " * 1000
        tokens = count_tokens(text, method="local")
        assert tokens > 500
    
    def test_local_method(self):
        """Test local method"""
        text = "This is a test"
        tokens = count_tokens(text, method="local")
        assert tokens > 0


class TestEstimateCost:
    def test_openai_cost(self):
        """Test OpenAI cost estimation"""
        cost_info = estimate_embedding_cost(10000, "openai")
        assert "cost_usd" in cost_info
        assert "cost_brl" in cost_info
        assert cost_info["cost_usd"] > 0
    
    def test_local_cost(self):
        """Test local cost estimation"""
        cost_info = estimate_embedding_cost(10000, "sentence-transformers")
        assert "note" in cost_info
        assert "no costs" in cost_info["note"].lower()
    
    def test_large_token_count(self):
        """Test with large token count"""
        cost_info = estimate_embedding_cost(1000000, "openai")
        assert cost_info["cost_usd"] > 0.05
