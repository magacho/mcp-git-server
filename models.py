from pydantic import BaseModel, Field, field_validator
from typing import List
import re

class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Query string for document retrieval")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of top documents to retrieve")
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and sanitize query string"""
        if not v or not v.strip():
            raise ValueError('Query cannot be empty or only whitespace')
        
        # Normalize whitespace
        v = re.sub(r'\s+', ' ', v.strip())
        
        # Check minimum length
        if len(v) < 3:
            raise ValueError('Query must be at least 3 characters long')
        
        # Check for XSS patterns
        xss_patterns = [
            r'<script',
            r'javascript:',
            r'onerror\s*=',
            r'onclick\s*=',
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Query contains potentially unsafe content')
        
        return v 

class DocumentFragment(BaseModel):
    source: str
    content: str

class RetrieveResponse(BaseModel):
    query: str
    fragments: List[DocumentFragment]