from pydantic import BaseModel, Field, validator
from typing import List

class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Query string for document retrieval")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of top documents to retrieve")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty or only whitespace')
        return v.strip() 

class DocumentFragment(BaseModel):
    source: str
    content: str

class RetrieveResponse(BaseModel):
    query: str
    fragments: List[DocumentFragment]