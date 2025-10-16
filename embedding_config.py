"""
Configuração de embeddings com suporte a modelos locais e externos
"""
import os
from typing import Union
from langchain_openai import OpenAIEmbeddings
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_community.embeddings import SentenceTransformerEmbeddings

class EmbeddingProvider:
    """Factory para diferentes provedores de embedding"""
    
    @staticmethod
    def get_embeddings(provider: str = None) -> Union[OpenAIEmbeddings, HuggingFaceEmbeddings, SentenceTransformerEmbeddings]:
        """
        Retorna o provedor de embeddings configurado
        
        Args:
            provider: 'openai', 'huggingface', 'sentence-transformers', ou None (auto-detect)
        """
        if provider is None:
            provider = os.getenv("EMBEDDING_PROVIDER", "auto")
        
        if provider == "auto":
            # Priorizar embeddings locais por padrão (gratuito)
            provider = "sentence-transformers"
        
        if provider == "openai":
            if "OPENAI_API_KEY" not in os.environ:
                raise ValueError("OPENAI_API_KEY não encontrada para usar embeddings OpenAI")
            return OpenAIEmbeddings()
        
        elif provider == "huggingface":
            # Modelo multilíngue e eficiente
            model_name = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
            return HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={'device': 'cpu'},  # Usar GPU se disponível: 'cuda'
                encode_kwargs={'normalize_embeddings': True}
            )
        
        elif provider == "sentence-transformers":
            # Modelo local rápido e gratuito
            model_name = os.getenv("ST_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            return SentenceTransformerEmbeddings(
                model_name=model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        
        else:
            raise ValueError(f"Provedor de embedding não suportado: {provider}")

    @staticmethod
    def get_available_providers() -> dict:
        """Retorna os provedores disponíveis e suas configurações"""
        providers = {}
        
        # OpenAI
        if "OPENAI_API_KEY" in os.environ:
            providers["openai"] = {
                "available": True,
                "cost": "Pago por token",
                "quality": "Alta",
                "speed": "Rápida (API)"
            }
        else:
            providers["openai"] = {
                "available": False,
                "reason": "OPENAI_API_KEY não configurada"
            }
        
        # Sentence Transformers (sempre disponível)
        providers["sentence-transformers"] = {
            "available": True,
            "cost": "Gratuito",
            "quality": "Boa",
            "speed": "Média (local)",
            "model": os.getenv("ST_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        }
        
        # HuggingFace
        providers["huggingface"] = {
            "available": True,
            "cost": "Gratuito",
            "quality": "Boa",
            "speed": "Média (local)",
            "model": os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        }
        
        return providers