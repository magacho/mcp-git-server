# Dockerfile otimizado para embeddings locais
FROM python:3.12-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    git \
    libmagic1 \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Configurar diretório de trabalho
WORKDIR /app

# Criar usuário não-root
RUN useradd --create-home --shell /bin/bash --uid 1000 app \
    && chown -R app:app /app

RUN mkdir -p /home/app/.ssh \
      && chmod 700 /home/app/.ssh \
      && chown app:app /home/app/.ssh


# Copiar requirements primeiro para cache
COPY requirements.txt ./

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

# Criar diretórios necessários
RUN mkdir -p /app/repos /app/chroma_db \
    && chown -R app:app /app/repos /app/chroma_db

# Mudar para usuário não-root
USER app

# Copiar código da aplicação
COPY --chown=app:app *.py ./

# Configuração padrão para embeddings locais
ENV EMBEDDING_PROVIDER=sentence-transformers
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
# Método de contagem de tokens (local/tiktoken)
ENV TOKENIZER_MODE=local

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5)" || exit 1

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--access-log"]