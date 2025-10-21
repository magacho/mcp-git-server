import tiktoken
import os
from typing import Optional

def count_tokens_local(text: str) -> int:
    """
    Fast token counting using character-based approximation
    Much faster than tiktoken for estimates
    
    Args:
        text: Text to count tokens for
        
    Returns:
        Approximate token count
    """
    # Approximation: ~4 characters per token for English/Portuguese text
    # More conservative for code (more tokens per character)
    if any(ext in text.lower() for ext in ['.py', '.js', '.ts', '.java', '.cpp']):
        # Code has more tokens per character
        return len(text) // 3
    else:
        # Natural language text
        return len(text) // 4

def count_tokens_openai(text: str, model: str = "text-embedding-ada-002") -> int:
    """
    Accurate token counting using tiktoken (slower)
    
    Args:
        text: Text to count tokens for
        model: Model name for tiktoken encoding
        
    Returns:
        Precise token count
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except Exception:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def count_tokens(text: str, method: str = "auto", model: Optional[str] = None) -> int:
    """
    Count tokens using different methods
    
    Args:
        text: Text to count tokens for
        method: 'local' (fast), 'tiktoken' (accurate), 'auto' (chooses based on context)
        model: Model for tiktoken (if applicable)
    
    Returns:
        Estimated number of tokens
    """
    method = method or os.getenv("TOKEN_COUNT_METHOD", "auto")
    
    if method == "auto":
        # For small texts, use tiktoken. For large texts, use local approximation
        if len(text) < 10000:
            method = "tiktoken"
        else:
            method = "local"
    
    if method == "local":
        return count_tokens_local(text)
    elif method == "tiktoken":
        return count_tokens_openai(text, model or "text-embedding-ada-002")
    else:
        raise ValueError(f"Unsupported counting method: {method}")

def estimate_embedding_cost(total_tokens: int, provider: str = "openai") -> dict:
    """
    Estimate embedding cost based on number of tokens
    
    Args:
        total_tokens: Total number of tokens
        provider: Embedding provider name
        
    Returns:
        Dictionary with cost information
    """
    if provider == "openai":
        # OpenAI approximate pricing for text-embedding-ada-002
        cost_per_1k_tokens = 0.0001  # USD
        total_cost = (total_tokens / 1000) * cost_per_1k_tokens
        return {
            "provider": "OpenAI",
            "total_tokens": total_tokens,
            "cost_usd": round(total_cost, 4),
            "cost_brl": round(total_cost * 5.5, 4)  # Approximation USD->BRL
        }
    else:
        return {
            "provider": provider,
            "total_tokens": total_tokens,
            "cost_usd": 0.0,
            "cost_brl": 0.0,
            "note": "Local embedding - no costs"
        }