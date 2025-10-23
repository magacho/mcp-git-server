"""
Embedding optimizer based on provider
"""
import os
import psutil
from typing import Tuple

def get_optimal_config(provider: str, total_documents: int) -> Tuple[int, int]:
    """
    Returns optimized configuration based on provider and available resources
    
    Args:
        provider: Embedding provider ('openai', 'sentence-transformers', etc.)
        total_documents: Total number of documents to process
    
    Returns:
        Tuple[batch_size, max_workers]
    """
    
    # Detect system resources
    cpu_count = os.cpu_count() or 1
    memory_gb = psutil.virtual_memory().total / (1024**3)
    
    if provider == "openai":
        # OpenAI: Conservative due to rate limits
        batch_size = min(500, max(50, total_documents // 10))
        max_workers = min(2, cpu_count)
        
    elif provider in ["sentence-transformers", "huggingface"]:
        # Local embeddings: Optimize based on resources
        
        # Batch size based on available memory
        if memory_gb >= 16:
            batch_size = min(2000, max(200, total_documents // 5))
        elif memory_gb >= 8:
            batch_size = min(1000, max(100, total_documents // 8))
        else:
            batch_size = min(500, max(50, total_documents // 10))
        
        # Workers based on CPU
        if cpu_count >= 8:
            max_workers = min(8, cpu_count)
        elif cpu_count >= 4:
            max_workers = min(6, cpu_count + 2)
        else:
            max_workers = min(4, cpu_count + 1)
            
        # Adjust for small documents
        if total_documents < 100:
            batch_size = min(batch_size, total_documents)
            max_workers = min(max_workers, 2)
    
    else:
        # Fallback for other providers
        batch_size = min(1000, max(100, total_documents // 8))
        max_workers = min(4, cpu_count)
    
    return batch_size, max_workers

def get_processing_strategy(provider: str) -> dict:
    """
    Returns processing strategy based on provider
    
    Args:
        provider: Embedding provider
        
    Returns:
        Dict with strategy configurations
    """
    
    if provider == "openai":
        return {
            "rate_limiting": True,
            "token_limit_per_minute": 900000,
            "retry_attempts": 3,
            "retry_delay": 5,
            "progress_frequency": "per_batch",
            "parallel_safe": False
        }
    
    elif provider in ["sentence-transformers", "huggingface"]:
        return {
            "rate_limiting": False,
            "token_limit_per_minute": None,
            "retry_attempts": 2,
            "retry_delay": 1,
            "progress_frequency": "per_10_batches",
            "parallel_safe": True
        }
    
    else:
        return {
            "rate_limiting": False,
            "token_limit_per_minute": None,
            "retry_attempts": 2,
            "retry_delay": 2,
            "progress_frequency": "per_batch",
            "parallel_safe": True
        }

def estimate_processing_time(provider: str, total_documents: int, avg_doc_size: int) -> dict:
    """
    Estimates processing time based on provider and data
    
    Args:
        provider: Embedding provider
        total_documents: Number of documents
        avg_doc_size: Average document size in characters
        
    Returns:
        Dict with time estimates
    """
    
    if provider == "openai":
        # OpenAI: ~1-2 seconds per document (including rate limiting)
        time_per_doc = 1.5
        estimated_seconds = total_documents * time_per_doc
        
    elif provider == "sentence-transformers":
        # Local: ~0.1-0.5 seconds per document (depending on hardware)
        cpu_count = os.cpu_count() or 1
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        # Performance factor based on resources
        if memory_gb >= 16 and cpu_count >= 8:
            time_per_doc = 0.1  # Powerful hardware
        elif memory_gb >= 8 and cpu_count >= 4:
            time_per_doc = 0.2  # Medium hardware
        else:
            time_per_doc = 0.4  # Basic hardware
            
        # Adjust based on document size
        if avg_doc_size > 5000:
            time_per_doc *= 1.5
        elif avg_doc_size > 10000:
            time_per_doc *= 2
            
        estimated_seconds = total_documents * time_per_doc
        
    else:
        # Other providers: conservative estimate
        estimated_seconds = total_documents * 0.3
    
    # Convert to readable format
    if estimated_seconds < 60:
        time_str = f"{estimated_seconds:.0f} seconds"
    elif estimated_seconds < 3600:
        minutes = estimated_seconds / 60
        time_str = f"{minutes:.1f} minutes"
    else:
        hours = estimated_seconds / 3600
        time_str = f"{hours:.1f} hours"
    
    return {
        "estimated_seconds": estimated_seconds,
        "estimated_time_str": time_str,
        "provider": provider,
        "total_documents": total_documents
    }