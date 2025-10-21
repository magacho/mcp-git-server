"""
Global test configuration for pytest
"""
import pytest
import os
from unittest.mock import Mock, MagicMock

# Configure environment variables for tests
os.environ["REPO_URL"] = "https://github.com/octocat/Hello-World.git"
os.environ["REPO_BRANCH"] = "master"
os.environ["EMBEDDING_PROVIDER"] = "sentence-transformers"

@pytest.fixture
def mock_vectorstore():
    """Mock for vectorstore"""
    mock = MagicMock()
    mock.as_retriever.return_value = MagicMock()
    return mock

@pytest.fixture
def sample_documents():
    """Sample documents for tests"""
    from langchain_core.documents import Document
    return [
        Document(page_content="def hello(): return 'world'", metadata={"source": "test.py"}),
        Document(page_content="# README\nTest project", metadata={"source": "README.md"}),
        Document(page_content="import os\nprint('test')", metadata={"source": "main.py"}),
    ]

@pytest.fixture
def mock_embeddings():
    """Mock for embeddings"""
    mock = MagicMock()
    mock.embed_query.return_value = [0.1] * 384  # Fake vector
    mock.embed_documents.return_value = [[0.1] * 384]
    return mock
