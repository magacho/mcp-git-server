import tiktoken
import os
from typing import Optional

def contar_tokens_local(texto: str) -> int:
    """
    Contagem rápida de tokens usando aproximação baseada em caracteres
    Muito mais rápido que tiktoken para estimativas
    """
    # Aproximação: ~4 caracteres por token para texto em inglês/português
    # Mais conservador para código (mais tokens por caractere)
    if any(ext in texto.lower() for ext in ['.py', '.js', '.ts', '.java', '.cpp']):
        # Código tem mais tokens por caractere
        return len(texto) // 3
    else:
        # Texto natural
        return len(texto) // 4

def contar_tokens_openai(texto: str, model: str = "text-embedding-ada-002") -> int:
    """
    Contagem precisa usando tiktoken (mais lenta)
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except Exception:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(texto))

def contar_tokens(texto: str, metodo: str = "auto", model: Optional[str] = None) -> int:
    """
    Conta tokens usando diferentes métodos
    
    Args:
        texto: Texto para contar tokens
        metodo: 'local' (rápido), 'tiktoken' (preciso), 'auto' (escolhe baseado no contexto)
        model: Modelo para tiktoken (se aplicável)
    
    Returns:
        Número estimado de tokens
    """
    metodo = metodo or os.getenv("TOKEN_COUNT_METHOD", "auto")
    
    if metodo == "auto":
        # Para textos pequenos, usar tiktoken. Para grandes, usar aproximação local
        if len(texto) < 10000:
            metodo = "tiktoken"
        else:
            metodo = "local"
    
    if metodo == "local":
        return contar_tokens_local(texto)
    elif metodo == "tiktoken":
        return contar_tokens_openai(texto, model or "text-embedding-ada-002")
    else:
        raise ValueError(f"Token counting method not supported: {metodo}")

def estimar_custo_embeddings(total_tokens: int, provider: str = "openai") -> dict:
    """
    Estima o custo de embeddings baseado no número de tokens
    """
    if provider == "openai":
        # Preço aproximado da OpenAI para text-embedding-ada-002
        custo_por_1k_tokens = 0.0001  # USD
        custo_total = (total_tokens / 1000) * custo_por_1k_tokens
        return {
            "provider": "OpenAI",
            "total_tokens": total_tokens,
            "custo_usd": round(custo_total, 4),
            "custo_brl": round(custo_total * 5.5, 4)  # Aproximação USD->BRL
        }
    else:
        return {
            "provider": provider,
            "total_tokens": total_tokens,
            "custo_usd": 0.0,
            "custo_brl": 0.0,
            "nota": "Local embedding - no costs"
        }