"""
Additional tests for token_utils.py to increase coverage
"""
import os
import pytest
from unittest.mock import patch, MagicMock
from token_utils import (
    count_tokens_local,
    count_tokens_openai,
    count_tokens,
    estimate_embedding_cost
)


class TestCountTokensLocal:
    """Tests for count_tokens_local function"""
    
    def test_code_text_estimation(self):
        """Test token estimation for code"""
        code_text = "def hello():\n    print('hello')"
        tokens = count_tokens_local(code_text)
        
        # Code should use ~3 chars per token
        assert tokens > 0
        assert tokens >= len(code_text) // 4
    
    def test_python_code(self):
        """Test Python code detection"""
        text = "This is .py code with python syntax"
        tokens = count_tokens_local(text)
        assert tokens == len(text) // 3
    
    def test_javascript_code(self):
        """Test JavaScript code detection"""
        text = "This is .js code with javascript"
        tokens = count_tokens_local(text)
        assert tokens == len(text) // 3
    
    def test_typescript_code(self):
        """Test TypeScript code detection"""
        text = "This is .ts code"
        tokens = count_tokens_local(text)
        assert tokens == len(text) // 3
    
    def test_java_code(self):
        """Test Java code detection"""
        text = "This is .java code"
        tokens = count_tokens_local(text)
        assert tokens == len(text) // 3
    
    def test_cpp_code(self):
        """Test C++ code detection"""
        text = "This is .cpp code"
        tokens = count_tokens_local(text)
        assert tokens == len(text) // 3
    
    def test_natural_text(self):
        """Test natural language text"""
        text = "This is natural language text without code references"
        tokens = count_tokens_local(text)
        assert tokens == len(text) // 4
    
    def test_empty_text(self):
        """Test empty text"""
        tokens = count_tokens_local("")
        assert tokens == 0
    
    def test_case_insensitive_code_detection(self):
        """Test case insensitive code extension detection"""
        text = "This has .PY in uppercase"
        tokens = count_tokens_local(text)
        assert tokens == len(text) // 3


class TestCountTokensOpenai:
    """Tests for count_tokens_openai function"""
    
    @patch('token_utils.tiktoken.encoding_for_model')
    def test_with_valid_model(self, mock_encoding_for_model):
        """Test with valid model"""
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]
        mock_encoding_for_model.return_value = mock_encoding
        
        tokens = count_tokens_openai("test text", "text-embedding-ada-002")
        
        assert tokens == 5
        mock_encoding_for_model.assert_called_once_with("text-embedding-ada-002")
    
    @patch('token_utils.tiktoken.get_encoding')
    @patch('token_utils.tiktoken.encoding_for_model')
    def test_fallback_to_base_encoding(self, mock_encoding_for_model, mock_get_encoding):
        """Test fallback when model not found"""
        mock_encoding_for_model.side_effect = Exception("Model not found")
        
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3]
        mock_get_encoding.return_value = mock_encoding
        
        tokens = count_tokens_openai("test text")
        
        assert tokens == 3
        mock_get_encoding.assert_called_once_with("cl100k_base")
    
    @patch('token_utils.tiktoken.encoding_for_model')
    def test_empty_text(self, mock_encoding_for_model):
        """Test with empty text"""
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = []
        mock_encoding_for_model.return_value = mock_encoding
        
        tokens = count_tokens_openai("")
        
        assert tokens == 0


class TestCountTokens:
    """Tests for count_tokens function"""
    
    def test_explicit_local_method(self):
        """Test explicit local method"""
        text = "Natural language text"
        tokens = count_tokens(text, method="local")
        
        assert tokens == len(text) // 4
    
    @patch('token_utils.count_tokens_openai')
    def test_explicit_tiktoken_method(self, mock_openai):
        """Test explicit tiktoken method"""
        mock_openai.return_value = 10
        
        tokens = count_tokens("test text", method="tiktoken")
        
        assert tokens == 10
        mock_openai.assert_called_once()
    
    @patch('token_utils.count_tokens_openai')
    def test_auto_method_small_text(self, mock_openai):
        """Test auto method with small text (< 10000 chars)"""
        mock_openai.return_value = 50
        
        text = "short text" * 100  # Still < 10000 chars
        tokens = count_tokens(text, method="auto")
        
        # Should use tiktoken for small text
        mock_openai.assert_called_once()
    
    def test_auto_method_large_text(self):
        """Test auto method with large text (>= 10000 chars)"""
        text = "x" * 10000  # Large text
        tokens = count_tokens(text, method="auto")
        
        # Should use local approximation
        assert tokens == len(text) // 4
    
    def test_invalid_method(self):
        """Test with invalid method"""
        with pytest.raises(ValueError) as exc_info:
            count_tokens("test", method="invalid_method")
        
        assert "not supported" in str(exc_info.value)
    
    @patch.dict(os.environ, {"TOKEN_COUNT_METHOD": "local"})
    def test_method_from_env(self):
        """Test method from environment variable"""
        text = "test text"
        tokens = count_tokens(text, method=None)
        
        # Should use env var value
        assert tokens == len(text) // 4
    
    @patch('token_utils.count_tokens_openai')
    def test_default_method(self, mock_openai):
        """Test default method (auto)"""
        mock_openai.return_value = 5
        
        with patch.dict(os.environ, {}, clear=True):
            text = "test"
            tokens = count_tokens(text)
            
            # Should use auto (which will use tiktoken for small text)
            assert tokens >= 0
    
    @patch('token_utils.count_tokens_openai')
    def test_custom_model(self, mock_openai):
        """Test with custom model"""
        mock_openai.return_value = 15
        
        tokens = count_tokens("test", method="tiktoken", model="gpt-4")
        
        mock_openai.assert_called_once_with("test", "gpt-4")


class TestEstimateEmbeddingCost:
    """Tests for estimate_embedding_cost function"""
    
    def test_openai_cost_calculation(self):
        """Test OpenAI cost calculation"""
        result = estimate_embedding_cost(1000, provider="openai")
        
        assert result["provider"] == "OpenAI"
        assert result["total_tokens"] == 1000
        assert result["cost_usd"] == 0.0001  # 1000 tokens / 1000 * 0.0001
        assert result["cost_brl"] > 0
    
    def test_openai_large_token_count(self):
        """Test with large token count"""
        result = estimate_embedding_cost(1000000, provider="openai")
        
        assert result["cost_usd"] == 0.1  # 1M tokens / 1000 * 0.0001
        assert result["cost_brl"] == round(0.1 * 5.5, 4)
    
    def test_openai_zero_tokens(self):
        """Test with zero tokens"""
        result = estimate_embedding_cost(0, provider="openai")
        
        assert result["cost_usd"] == 0.0
        assert result["cost_brl"] == 0.0
    
    def test_local_provider_no_cost(self):
        """Test local provider has no cost"""
        result = estimate_embedding_cost(10000, provider="sentence-transformers")
        
        assert result["provider"] == "sentence-transformers"
        assert result["total_tokens"] == 10000
        assert result["cost_usd"] == 0.0
        assert result["cost_brl"] == 0.0
        assert "no costs" in result["note"].lower()
    
    def test_huggingface_provider_no_cost(self):
        """Test HuggingFace provider has no cost"""
        result = estimate_embedding_cost(5000, provider="huggingface")
        
        assert result["cost_usd"] == 0.0
        assert result["cost_brl"] == 0.0
        assert "note" in result
    
    def test_unknown_provider_no_cost(self):
        """Test unknown provider defaults to no cost"""
        result = estimate_embedding_cost(3000, provider="custom-provider")
        
        assert result["provider"] == "custom-provider"
        assert result["cost_usd"] == 0.0
        assert result["cost_brl"] == 0.0
    
    def test_default_provider(self):
        """Test default provider (openai)"""
        result = estimate_embedding_cost(2000)
        
        assert result["provider"] == "OpenAI"
        assert result["total_tokens"] == 2000


class TestIntegrationScenarios:
    """Integration tests for token counting scenarios"""
    
    def test_mixed_content_estimation(self):
        """Test estimation with mixed code and text"""
        content = """
        # Documentation
        This is a description
        
        def function():
            return "result"
        """
        
        tokens_local = count_tokens(content, method="local")
        assert tokens_local > 0
    
    def test_long_document_processing(self):
        """Test processing long document"""
        long_text = "Lorem ipsum " * 1000  # ~12000 chars
        
        tokens = count_tokens(long_text, method="auto")
        
        # Should use local method for large text
        assert tokens > 0
        assert tokens == len(long_text) // 4
    
    def test_cost_estimation_workflow(self):
        """Test complete cost estimation workflow"""
        MIN_TOKENS_FOR_COST_TEST = 1000  # Minimum tokens to generate measurable cost
        text = "Sample text for embedding " * 100  # Make it long enough to generate cost
        
        # Count tokens
        tokens = count_tokens(text, method="local")
        
        # Estimate cost - use at least MIN_TOKENS_FOR_COST_TEST for meaningful cost
        cost_openai = estimate_embedding_cost(max(tokens, MIN_TOKENS_FOR_COST_TEST), "openai")
        cost_local = estimate_embedding_cost(tokens, "sentence-transformers")
        
        assert cost_openai["cost_usd"] > 0
        assert cost_local["cost_usd"] == 0
