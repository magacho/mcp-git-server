"""
Sistema de autenticação para API
"""
import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from logging_config import get_logger

logger = get_logger(__name__)

# Header para API key
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """
    Verifica se a API key é válida
    
    Args:
        api_key: API key fornecida no header
    
    Returns:
        API key válida
    
    Raises:
        HTTPException: Se a API key for inválida ou ausente
    """
    # Se API_KEY não estiver configurada, não requer autenticação
    expected_key = os.getenv("API_KEY")
    
    if not expected_key:
        # Modo desenvolvimento - sem autenticação
        logger.warning(
            "api_auth_disabled",
            message="API_KEY não configurada - autenticação desabilitada"
        )
        return None
    
    # Verificar se API key foi fornecida
    if not api_key:
        logger.warning(
            "api_auth_missing",
            message="Tentativa de acesso sem API key"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key ausente. Forneça X-API-Key no header."
        )
    
    # Verificar se API key é válida
    if api_key != expected_key:
        logger.warning(
            "api_auth_invalid",
            message="Tentativa de acesso com API key inválida"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key inválida"
        )
    
    logger.debug("api_auth_success", message="Autenticação bem-sucedida")
    return api_key


def is_auth_enabled() -> bool:
    """
    Verifica se autenticação está habilitada
    
    Returns:
        True se API_KEY estiver configurada
    """
    return bool(os.getenv("API_KEY"))
