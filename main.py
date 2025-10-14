import os
import re
import subprocess # <- NOVA IMPORTAÇÃO
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# Importações do LangChain
# GitLoader foi substituído por DirectoryLoader
from langchain_community.document_loaders import DirectoryLoader 
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
# O repositório clonado agora ficará persistido também
LOCAL_REPO_PATH = f"/app/repos/{REPO_NAME}" 
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
    top_k: int = 5 

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
        print("\n" + "="*60)
        print("INICIANDO PROCESSO DE INDEXAÇÃO (PRIMEIRA EXECUÇÃO)")
        print(f"Repositório: {REPO_NAME}")
        print("="*60)

        # --- ETAPA 1: CLONE COM SAÍDA DETALHADA ---
        print("\n--- ETAPA 1 de 3: Clonando Repositório ---")
        repo_url = os.getenv("REPO_URL")
        repo_branch = os.getenv("REPO_BRANCH", "main")
        print(f"Clonando de: {repo_url} (Branch: {repo_branch})")
        
        # Comando git clone com a flag --progress para forçar a saída de status
        git_command = ["git", "clone", "--progress", "--branch", repo_branch, repo_url, LOCAL_REPO_PATH]
        
        # Executa o comando e captura a saída em tempo real
        with subprocess.Popen(git_command, stderr=subprocess.PIPE, text=True, bufsize=1) as process:
            for line in process.stderr:
                print(f"  [git] {line.strip()}") # Imprime a saída do git
        
        if process.returncode != 0:
            raise Exception(f"Falha ao clonar o repositório. Código de saída: {process.returncode}")

        # Agora, carrega os documentos do diretório local que acabamos de clonar
        loader = DirectoryLoader(LOCAL_REPO_PATH, recursive=True, show_progress=True)
        documents = loader.load()
        print(f">>> SUCESSO: Clone concluído. {len(documents)} documentos encontrados no diretório local.")
        # --- FIM DA ETAPA 1 ---

        if not documents:
            raise Exception("Nenhum documento foi carregado.")

        # --- ETAPA 2: DIVISÃO ---
        print("\n--- ETAPA 2 de 3: Dividindo Documentos ---")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        print(f">>> SUCESSO: Documentos divididos em {len(chunks)} pedaços.")
        # --- FIM DA ETAPA 2 ---

        # --- ETAPA 3: EMBEDDINGS COM SAÍDA DETALHADA ---
        print("\n--- ETAPA 3 de 3: Gerando e Armazenando Embeddings ---")
        
        vectorstore = Chroma(
            persist_directory=DB_PATH,
            embedding_function=embeddings
        )

        batch_size = 500
        total_batches = (len(chunks) - 1) // batch_size + 1

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            current_batch_num = i // batch_size + 1
            
            # Calcula o total de caracteres no lote para dar uma noção de tamanho
            total_chars = sum(len(doc.page_content) for doc in batch)
            
            print(f"  -> Processando lote {current_batch_num}/{total_batches} ({len(batch)} documentos, ~{total_chars} caracteres)...")
            vectorstore.add_documents(documents=batch)
        
        print("\n" + "="*60)
        print("INDEXAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60 + "\n")
    else:
        print("\n" + "="*60)
        print(f"Carregando base de dados vetorial existente para '{REPO_NAME}'...")
        vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
        print(">>> SUCESSO: Base de dados carregada da memória.")
        print("="*60 + "\n")

    retriever = vectorstore.as_retriever()
    print(f"Servidor pronto. Repositório '{REPO_NAME}' está carregado e pronto para consultas.")

# --- ENDPOINTS DA API ---
# (O resto do arquivo continua exatamente igual)
@app.get("/", summary="Verificação de Status")
def read_root():
    return {"status": f"MCP Server online para o repositório: {REPO_NAME}"}

@app.post("/retrieve", response_model=RetrieveResponse, summary="Busca fragmentos de contexto")
def retrieve_context(request: RetrieveRequest):
    if not retriever:
        raise HTTPException(status_code=503, detail="O servidor ainda está inicializando. Tente novamente em alguns segundos.")

    print(f"Recebida busca por: '{request.query}' com top_k={request.top_k}")
    
    retriever.search_kwargs['k'] = request.top_k
    
    relevant_docs = retriever.invoke(request.query)

    response_fragments = [
        DocumentFragment(
            source=doc.metadata.get('source', 'N/A'), 
            content=doc.page_content
        ) 
        for doc in relevant_docs
    ]

    return RetrieveResponse(query=request.query, fragments=response_fragments)