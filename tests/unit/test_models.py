"""
Tests for models.py
"""
import pytest
from pydantic import ValidationError
from models import RetrieveRequest, DocumentFragment, RetrieveResponse


class TestRetrieveRequest:
    def test_valid_request(self):
        """Test with valid request"""
        request = RetrieveRequest(query="test query", top_k=5)
        assert request.query == "test query"
        assert request.top_k == 5
    
    def test_default_top_k(self):
        """Test default value of top_k"""
        request = RetrieveRequest(query="test")
        assert request.top_k == 5
    
    def test_empty_query_fails(self):
        """Empty query should fail"""
        with pytest.raises(ValidationError):
            RetrieveRequest(query="", top_k=5)
    
    def test_negative_top_k_fails(self):
        """Negative top_k should fail"""
        with pytest.raises(ValidationError):
            RetrieveRequest(query="test", top_k=-1)


class TestDocumentFragment:
    def test_valid_fragment(self):
        """Test with valid fragment"""
        fragment = DocumentFragment(source="test.py", content="print('hello')")
        assert fragment.source == "test.py"
        assert fragment.content == "print('hello')"


class TestRetrieveResponse:
    def test_valid_response(self):
        """Test with valid response"""
        fragments = [
            DocumentFragment(source="test.py", content="code1"),
            DocumentFragment(source="main.py", content="code2"),
        ]
        response = RetrieveResponse(query="test", fragments=fragments)
        assert response.query == "test"
        assert len(response.fragments) == 2
    
    def test_empty_fragments(self):
        """Response with empty fragments"""
        response = RetrieveResponse(query="test", fragments=[])
        assert response.query == "test"
        assert len(response.fragments) == 0
