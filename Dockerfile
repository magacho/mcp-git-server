# Use uma imagem base do Python leve
FROM python:3.11-slim

RUN apt-get update && apt-get install -y git libmagic-dev pkg-config

# Defina o diretório de trabalho dentro do container
WORKDIR /app

# Copie o arquivo de dependências primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copie o resto do código da aplicação
COPY *.py .

# Exponha a porta em que a API vai rodar
EXPOSE 8000

# O comando para iniciar a aplicação quando o container rodar
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]