from pydantic import BaseModel, Field, field_validator
from typing import List
import re

class RetrieveRequest(BaseModel):
    query: str = Field(
        ..., 
        min_length=3, 
        max_length=1000, 
        description="Query string for document retrieval (3-1000 characters)"
    )
    top_k: int = Field(
        default=5, 
        ge=1, 
        le=50, 
        description="Number of top documents to retrieve (1-50)"
    )
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and sanitize query string"""
        # Remove leading/trailing whitespace
        v = v.strip()
        
        # Check if empty after stripping
        if not v:
            raise ValueError('Query cannot be empty or only whitespace')
        
        # Check minimum length
        if len(v) < 3:
            raise ValueError('Query must be at least 3 characters long')
        
        # Check for dangerous characters that might indicate injection attempts
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'onerror=',
            r'onclick=',
            r'\x00',  # null bytes
        ]
        
        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, v_lower):
                raise ValueError(f'Query contains potentially dangerous content')
        
        # Remove excessive whitespace
        v = re.sub(r'\s+', ' ', v)
        
        return v 

class DocumentFragment(BaseModel):
    source: str
    content: str

class RetrieveResponse(BaseModel):
    query: str
    fragments: List[DocumentFragment]