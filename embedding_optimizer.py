"""
Otimizador de embeddings baseado no provedor
"""
import os
import psutil
from typing import Tuple

def get_optimal_config(provider: str, total_documents: int) -> Tuple[int, int]:
    """
    Retorna configuração otimizada baseada no provedor e recursos disponíveis
    
    Args:
        provider: Provedor de embeddings ('openai', 'sentence-transformers', etc.)
        total_documents: Número total de documentos a processar
    
    Returns:
        Tuple[batch_size, max_workers]
    """
    
    # Detectar recursos do sistema
    cpu_count = os.cpu_count() or 1
    memory_gb = psutil.virtual_memory().total / (1024**3)
    
    if provider == "openai":
        # OpenAI: Conservador devido a rate limits
        batch_size = min(500, max(50, total_documents // 10))
        max_workers = min(2, cpu_count)
        
    elif provider in ["sentence-transformers", "huggingface"]:
        # Embeddings locais: Otimizar baseado em recursos
        
        # Batch size baseado na memória disponível
        if memory_gb >= 16:
            batch_size = min(2000, max(200, total_documents // 5))
        elif memory_gb >= 8:
            batch_size = min(1000, max(100, total_documents // 8))
        else:
            batch_size = min(500, max(50, total_documents // 10))
        
        # Workers baseado em CPU
        if cpu_count >= 8:
            max_workers = min(8, cpu_count)
        elif cpu_count >= 4:
            max_workers = min(6, cpu_count + 2)
        else:
            max_workers = min(4, cpu_count + 1)
            
        # Ajustar para documentos pequenos
        if total_documents < 100:
            batch_size = min(batch_size, total_documents)
            max_workers = min(max_workers, 2)
    
    else:
        # Fallback para outros provedores
        batch_size = min(1000, max(100, total_documents // 8))
        max_workers = min(4, cpu_count)
    
    return batch_size, max_workers

def get_processing_strategy(provider: str) -> dict:
    """
    Retorna estratégia de processamento baseada no provedor
    
    Args:
        provider: Provedor de embeddings
        
    Returns:
        Dict com configurações de estratégia
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
    Estima tempo de processamento baseado no provedor e dados
    
    Args:
        provider: Provedor de embeddings
        total_documents: Número de documentos
        avg_doc_size: Tamanho médio dos documentos em caracteres
        
    Returns:
        Dict com estimativas de tempo
    """
    
    if provider == "openai":
        # OpenAI: ~1-2 segundos por documento (incluindo rate limiting)
        time_per_doc = 1.5
        estimated_seconds = total_documents * time_per_doc
        
    elif provider == "sentence-transformers":
        # Local: ~0.1-0.5 segundos por documento (dependendo do hardware)
        cpu_count = os.cpu_count() or 1
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        # Fator de performance baseado em recursos
        if memory_gb >= 16 and cpu_count >= 8:
            time_per_doc = 0.1  # Hardware potente
        elif memory_gb >= 8 and cpu_count >= 4:
            time_per_doc = 0.2  # Hardware médio
        else:
            time_per_doc = 0.4  # Hardware básico
            
        # Ajustar baseado no tamanho dos documentos
        if avg_doc_size > 5000:
            time_per_doc *= 1.5
        elif avg_doc_size > 10000:
            time_per_doc *= 2
            
        estimated_seconds = total_documents * time_per_doc
        
    else:
        # Outros provedores: estimativa conservadora
        estimated_seconds = total_documents * 0.3
    
    # Converter para formato legível
    if estimated_seconds < 60:
        time_str = f"{estimated_seconds:.0f} segundos"
    elif estimated_seconds < 3600:
        minutes = estimated_seconds / 60
        time_str = f"{minutes:.1f} minutos"
    else:
        hours = estimated_seconds / 3600
        time_str = f"{hours:.1f} horas"
    
    return {
        "estimated_seconds": estimated_seconds,
        "estimated_time_str": time_str,
        "provider": provider,
        "total_documents": total_documents
    }