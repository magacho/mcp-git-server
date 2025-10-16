# Use uma imagem base do Python mais recente
FROM python:3.12-slim

# Instalar dependências do sistema em uma única camada
RUN apt-get update && apt-get install -y \
    git \
    libmagic-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Defina o diretório de trabalho dentro do container
WORKDIR /app

# Criar usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Copie o arquivo de dependências primeiro para aproveitar o cache do Docker
COPY --chown=app:app requirements.txt .

# Instale as dependências com pip atualizado
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copie o resto do código da aplicação
COPY --chown=app:app *.py .

# Criar diretórios necessários
RUN mkdir -p /app/repos /app/chroma_db

# Exponha a porta em que a API vai rodar
EXPOSE 8000

# Configurações de produção para uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--access-log"]