import os
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# Importações do LangChain
from langchain_community.document_loaders import GitLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- CONFIGURAÇÃO A PARTIR DE VARIÁVEIS DE AMBIENTE ---
REPO_URL = os.environ.get("REPO_URL")
if not REPO_URL:
    raise ValueError("A variável de ambiente REPO_URL não foi definida.")

if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("A variável de ambiente OPENAI_API_KEY não foi definida.")

# Função para criar um nome de pasta seguro a partir da URL do repo
def get_repo_name_from_url(url):
    try:
        repo_name = url.split('/')[-1]
        repo_name = re.sub(r'\.git$', '', repo_name)
        safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', repo_name)
        return safe_name
    except Exception:
        return "default_repo"

REPO_NAME = get_repo_name_from_url(REPO_URL)
REPO_PATH = f"/app/repos/{REPO_NAME}"
DB_PATH = f"/app/chroma_db/{REPO_NAME}"

# --- INICIALIZAÇÃO DA API ---
app = FastAPI(
    title="Servidor de Recuperação de Contexto (MCP)",
    description="Uma API que recebe uma pergunta e retorna trechos relevantes de um repositório GitHub.",
    version="1.0.0",
)

# --- MODELOS DE DADOS PARA A API ---
class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 5 # Quantidade de documentos a retornar

class DocumentFragment(BaseModel):
    source: str
    content: str

class RetrieveResponse(BaseModel):
    query: str
    fragments: List[DocumentFragment]

# --- LÓGICA DO SERVIDOR ---
vectorstore = None
retriever = None

@app.on_event("startup")
def startup_event():
    """
    Função executada na inicialização. Clona e indexa o repositório se ainda não foi feito.
    """
    global vectorstore, retriever
    
    embeddings = OpenAIEmbeddings()

    # ESTA LÓGICA É O QUE FAZ O VOLUME FUNCIONAR CORRETAMENTE
    if not os.path.exists(DB_PATH):
        print(f"Base de dados não encontrada para '{REPO_NAME}'. Iniciando indexação...")
        
        print(f"Clonando repositório de {REPO_URL}...")
        repo_url = os.getenv("REPO_URL")
        repo_branch = os.getenv("REPO_BRANCH", "main")
    
        loader = GitLoader(
            repo_path="./repo_temp", 
            clone_url=repo_url,
            branch=repo_branch
        )

        documents = loader.load()

        if not documents:
            raise Exception("Nenhum documento foi carregado. Verifique a URL do repositório.")

        print(f"Dividindo {len(documents)} documentos em pedaços...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)

        print(f"Criando embeddings e armazenando no ChromaDB para {len(chunks)} pedaços...")
        
        # Inicializa o ChromaDB vazio, que será pre