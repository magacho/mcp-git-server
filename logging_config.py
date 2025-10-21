"""
Structured logging configuration
"""
import structlog
import logging
import sys


def setup_logging(log_level: str = "INFO"):
    """
    Configura logging estruturado com structlog
    
    Args:
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR)
    """
    # Configurar logging padrão
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )
    
    # Configurar structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None):
    """
    Retorna um logger estruturado
    
    Args:
        name: Nome do logger (opcional)
    
    Returns:
        Logger estruturado
    """
    if name:
        return structlog.get_logger(name)
    return structlog.get_logger()
