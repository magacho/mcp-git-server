from pydantic import BaseModel
from typing import List

class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 5 

class DocumentFragment(BaseModel):
    source: str
    content: str

class RetrieveResponse(BaseModel):
    query: str
    fragments: List[DocumentFragment]