import os
import re
import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Iterator
from langchain_core.documents import Document

# Importações do LangChain (com Chroma atualizado)
from langchain_community.document_loaders import DirectoryLoader
from langchain_chroma import Chroma
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

# Função auxiliar para carregar documentos de forma robusta e seletiva
def load_documents_robustly(path: str) -> Iterator[Document]:
    """
    Usa lazy_load para carregar seletivamente os arquivos de código e documentação, 
    pulando arquivos que possam causar erro.
    """
    # Define os padrões de arquivos que queremos incluir.
    glob_patterns = [
        "**/*.md",
        "**/*.ts",
        "**/*.js",
        "**/*.tsx",
        "**/*.jsx",
        "**/*.py",
        "**/*.html",
        "**/*.css",
        "**/*.txt",
    ]

    print("Iniciando carregamento seletivo de arquivos...")
    total_loaded = 0
    
    for pattern in glob_patterns:
        try:
            # silent_errors=True faz com que um arquivo que falhe não pare todo o processo.
            loader = DirectoryLoader(
                path, 
                glob=pattern, 
                recursive=True, 
                show_progress=True, 
                use_multithreading=True,
                silent_errors=True 
            )
            for doc in loader.lazy_load():
                total_loaded += 1
                yield doc
        except Exception as e:
            print(f"AVISO: Ocorreu um erro geral ao processar o padrão '{pattern}': {e}")
            continue
    
    print(f"Carregamento seletivo concluído. Total de documentos carregados: {total_loaded}")


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

        # --- ETAPA 1: CLONE E CARREGAMENTO ---
        print("\n--- ETAPA 1 de 3: Clonando e Carregando Repositório ---")
        
        if not os.path.exists(LOCAL_REPO_PATH):
            repo_url = os.getenv("REPO_URL")
            repo_branch = os.getenv("REPO_BRANCH", "main")
            print(f"Clonando de: {repo_url} (Branch: {repo_branch})")
            
            # Usamos --depth 1 para um clone superficial, muito mais rápido
            git_command = ["git", "clone", "--progress", "--depth", "1", "--branch", repo_branch, repo_url, LOCAL_REPO_PATH]
            
            with subprocess.Popen(git_command, stderr=subprocess.PIPE, text=True, bufsize=1) as process:
                for line in process.stderr:
                    print(f"  [git] {line.strip()}")
            
            if process.returncode != 0:
                raise Exception(f"Falha ao clonar o repositório. Código de saída: {process.returncode}")
        else:
            print(f"Diretório do repositório já existe em {LOCAL_REPO_PATH}. Pulando clone.")
        
        # Usa a nova função robusta para carregar os documentos
        documents = list(load_documents_robustly(LOCAL_REPO_PATH))

        if not documents:
            raise Exception("Nenhum documento foi carregado. Verifique os padrões de arquivo na função load_documents_robustly.")
        
        print(f">>> SUCESSO: Etapa 1 concluída.")

        # --- ETAPA 2: DIVISÃO ---
        print("\n--- ETAPA 2 de 3: Dividindo Documentos ---")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        print(f">>> SUCESSO: Documentos divididos em {len(chunks)} pedaços.")
        
        # --- ETAPA 3: EMBEDDINGS ---
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
            total_chars = sum(len(doc.page_content) for doc in batch)
            
            print(f"  -> Preparando lote {current_batch_num}/{total_batches} ({len(batch)} documentos, ~{total_chars} caracteres)...")
            print("     Enviando para a API da OpenAI e aguardando resposta (pode levar alguns minutos)...")
            
            vectorstore.add_documents(documents=batch)

            print(f"     Lote {current_batch_num} processado com sucesso!")
        
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