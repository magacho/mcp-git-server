"""
Unit tests for request validation
"""
import pytest
from pydantic import ValidationError
from models import RetrieveRequest


class TestQueryValidation:
    """Test query validation logic"""
    
    def test_valid_query(self):
        """Test that valid queries are accepted"""
        req = RetrieveRequest(query="How does authentication work?", top_k=5)
        assert req.query == "How does authentication work?"
        assert req.top_k == 5
    
    def test_query_too_short(self):
        """Test that queries shorter than 3 characters are rejected"""
        with pytest.raises(ValidationError) as exc_info:
            RetrieveRequest(query="ab", top_k=5)
        assert "at least 3 characters" in str(exc_info.value).lower()
    
    def test_query_empty_string(self):
        """Test that empty queries are rejected"""
        with pytest.raises(ValidationError) as exc_info:
            RetrieveRequest(query="", top_k=5)
        # Pydantic's built-in min_length=1 catches empty string before our custom validator
        assert "at least 1 character" in str(exc_info.value).lower()
    
    def test_query_whitespace_only(self):
        """Test that whitespace-only queries are rejected"""
        with pytest.raises(ValidationError) as exc_info:
            RetrieveRequest(query="   ", top_k=5)
        assert "cannot be empty" in str(exc_info.value).lower()
    
    def test_query_too_long(self):
        """Test that queries longer than 1000 characters are rejected"""
        long_query = "a" * 1001
        with pytest.raises(ValidationError) as exc_info:
            RetrieveRequest(query=long_query, top_k=5)
        assert "1000" in str(exc_info.value)
    
    def test_query_script_tag(self):
        """Test that queries with <script> tags are rejected"""
        with pytest.raises(ValidationError) as exc_info:
            RetrieveRequest(query="<script>alert('xss')</script>", top_k=5)
        assert "unsafe" in str(exc_info.value).lower()
    
    def test_query_javascript_protocol(self):
        """Test that queries with javascript: are rejected"""
        with pytest.raises(ValidationError) as exc_info:
            RetrieveRequest(query="javascript:alert(1)", top_k=5)
        assert "unsafe" in str(exc_info.value).lower()
    
    def test_query_onerror(self):
        """Test that queries with onerror= are rejected"""
        with pytest.raises(ValidationError) as exc_info:
            RetrieveRequest(query="<img src=x onerror=alert(1)>", top_k=5)
        assert "unsafe" in str(exc_info.value).lower()
    
    def test_query_whitespace_normalized(self):
        """Test that excessive whitespace is normalized"""
        req = RetrieveRequest(query="How   does    this  work?", top_k=5)
        assert req.query == "How does this work?"
    
    def test_query_stripped(self):
        """Test that leading/trailing whitespace is removed"""
        req = RetrieveRequest(query="  How does this work?  ", top_k=5)
        assert req.query == "How does this work?"


class TestTopKValidation:
    """Test top_k parameter validation"""
    
    def test_top_k_valid_range(self):
        """Test that top_k accepts values 1-50"""
        for k in [1, 5, 10, 25, 50]:
            req = RetrieveRequest(query="test query", top_k=k)
            assert req.top_k == k
    
    def test_top_k_zero_fails(self):
        """Test that top_k=0 is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            RetrieveRequest(query="test", top_k=0)
        assert "greater than or equal to 1" in str(exc_info.value).lower()
    
    def test_top_k_negative_fails(self):
        """Test that negative top_k is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            RetrieveRequest(query="test", top_k=-5)
        assert "greater than or equal to 1" in str(exc_info.value).lower()
    
    def test_top_k_too_large_fails(self):
        """Test that top_k > 50 is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            RetrieveRequest(query="test", top_k=51)
        assert "less than or equal to 50" in str(exc_info.value).lower()
    
    def test_top_k_default(self):
        """Test that top_k defaults to 5"""
        req = RetrieveRequest(query="test query")
        assert req.top_k == 5


class TestEdgeCases:
    """Test edge cases in validation"""
    
    def test_unicode_query(self):
        """Test that unicode characters are accepted"""
        req = RetrieveRequest(query="Como funciona autenticação?", top_k=5)
        assert req.query == "Como funciona autenticação?"
    
    def test_query_with_numbers(self):
        """Test that queries with numbers are accepted"""
        req = RetrieveRequest(query="What is API v2.0?", top_k=5)
        assert req.query == "What is API v2.0?"
    
    def test_query_with_special_chars(self):
        """Test that safe special characters are accepted"""
        req = RetrieveRequest(query="How to use @decorator?", top_k=5)
        assert req.query == "How to use @decorator?"
    
    def test_query_with_code(self):
        """Test that code snippets are accepted"""
        req = RetrieveRequest(query="function test() { return true; }", top_k=5)
        assert "function test()" in req.query
