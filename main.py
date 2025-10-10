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

    if not os.path.exists(DB_PATH):
        print(f"Base de dados não encontrada para '{REPO_NAME}'. Iniciando indexação...")
        
        print(f"Clonando repositório de {REPO_URL}...")
        loader = GitLoader(
            clone_url=REPO_URL,
            repo_path=REPO_PATH,
            file_filter=lambda file_path: file_path.endswith((".ts", ".md", ".json", ".js", ".py", ".java", ".go", "Dockerfile"))
        )
        documents = loader.load()

        if not documents:
            raise Exception("Nenhum documento foi carregado. Verifique a URL do repositório.")

        print(f"Dividindo {len(documents)} documentos em pedaços...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)

        print(f"Criando embeddings e armazenando no ChromaDB para {len(chunks)} pedaços...")
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=DB_PATH
        )
        print("Indexação concluída.")
    else:
        print(f"Carregando base de dados vetorial existente para '{REPO_NAME}'...")
        vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

    retriever = vectorstore.as_retriever()
    print(f"Servidor pronto. Repositório '{REPO_NAME}' está carregado e pronto para consultas.")

# --- ENDPOINTS DA API ---
@app.get("/", summary="Verificação de Status")
def read_root():
    """Endpoint para verificar se o servidor está online."""
    return {"status": f"MCP Server online para o repositório: {REPO_NAME}"}

@app.post("/retrieve", response_model=RetrieveResponse, summary="Busca fragmentos de contexto")
def retrieve_context(request: RetrieveRequest):
    """
    Recebe uma query (pergunta) e retorna os fragmentos de texto mais relevantes
    encontrados no banco de dados vetorial do repositório.
    """
    if not retriever:
        raise HTTPException(status_code=503, detail="O servidor ainda está inicializando. Tente novamente em alguns segundos.")

    print(f"Recebida busca por: '{request.query}' com top_k={request.top_k}")
    
    # Configura o retriever para buscar a quantidade de documentos solicitada
    retriever.search_kwargs['k'] = request.top_k
    
    # Realiza a busca por similaridade
    relevant_docs = retriever.invoke(request.query)

    # Formata a resposta para ser limpa e estruturada
    response_fragments = [
        DocumentFragment(
            source=doc.metadata.get('source', 'N/A'), 
            content=doc.page_content
        ) 
        for doc in relevant_docs
    ]

    return RetrieveResponse(query=request.query, fragments=response_fragments)