import os
from fastapi import FastAPI, HTTPException
from collections import defaultdict
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from models import RetrieveRequest, DocumentFragment, RetrieveResponse
from repo_utils import get_repo_name_from_url, clone_repo
from document_loader import load_documents_robustly, EXTENSOES_SUPORTADAS
from token_utils import contar_tokens_openai
from report_utils import gerar_relatorio_extensoes, gerar_relatorio_tokens

# --- CONFIGURAÇÃO A PARTIR DE VARIÁVEIS DE AMBIENTE ---
REPO_URL = os.environ.get("REPO_URL")
if not REPO_URL:
    raise ValueError("A variável de ambiente REPO_URL não foi definida.")

if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("A variável de ambiente OPENAI_API_KEY não foi definida.")

REPO_NAME = get_repo_name_from_url(REPO_URL)
LOCAL_REPO_PATH = f"/app/repos/{REPO_NAME}" 
DB_PATH = f"/app/chroma_db/{REPO_NAME}"

# --- INICIALIZAÇÃO DA API ---
app = FastAPI(
    title="Servidor de Recuperação de Contexto (MCP)",
    description="Uma API que recebe uma pergunta e retorna trechos relevantes de um repositório GitHub.",
    version="1.0.0",
)

vectorstore = None
retriever = None

extensoes_processadas = defaultdict(int)
extensoes_descartadas = defaultdict(int)
total_tokens_gerados = 0

server_ready = False  # Flag global

def index_repository():
    global vectorstore, retriever, total_tokens_gerados, server_ready
    embeddings = OpenAIEmbeddings()

    if not os.path.exists(DB_PATH):
        print("\n" + "="*60, flush=True)
        print("INICIANDO PROCESSO DE INDEXAÇÃO (PRIMEIRA EXECUÇÃO)", flush=True)
        print(f"Repositório: {REPO_NAME}", flush=True)
        print("="*60, flush=True)

        print("\n--- ETAPA 1 de 3: Clonando e Carregando Repositório ---", flush=True)
        repo_branch = os.getenv("REPO_BRANCH", "main")
        clone_repo(REPO_URL, repo_branch, LOCAL_REPO_PATH)

        documents = list(load_documents_robustly(LOCAL_REPO_PATH, extensoes_processadas, extensoes_descartadas))
        if not documents:
            raise Exception("Nenhum documento foi carregado. Verifique os padrões de arquivo.")

        print(f">>> SUCESSO: Etapa 1 concluída.", flush=True)

        print("\n--- ETAPA 2 de 3: Dividindo Documentos ---", flush=True)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        print(f">>> SUCESSO: Documentos divididos em {len(chunks)} pedaços.", flush=True)

        total_tokens_gerados = sum(contar_tokens_openai(doc.page_content) for doc in chunks)
        print(f">>> Total estimado de tokens para embeddings: {total_tokens_gerados}", flush=True)

        print("\n--- ETAPA 3 de 3: Gerando e Armazenando Embeddings ---", flush=True)
        vectorstore = Chroma(
            persist_directory=DB_PATH,
            embedding_function=embeddings
        )

        batch_size = 500
        total_batches = (len(chunks) - 1) // batch_size + 1

        def send_batch(batch, batch_num, total_batches, total_chars):
            print(f"  -> Preparando lote {batch_num}/{total_batches} ({len(batch)} documentos, ~{total_chars} caracteres)...", flush=True)
            print("     Enviando para a API da OpenAI e aguardando resposta (pode levar alguns minutos)...", flush=True)
            try:
                vectorstore.add_documents(documents=batch)
                print(f"     Lote {batch_num} processado com sucesso!", flush=True)
                return len(batch)
            except Exception as e:
                print(f"     ERRO no lote {batch_num}: {e}", flush=True)
                return 0

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                current_batch_num = i // batch_size + 1
                total_chars = sum(len(doc.page_content) for doc in batch)
                futures.append(executor.submit(send_batch, batch, current_batch_num, total_batches, total_chars))
            for future in as_completed(futures):
                # O próprio send_batch já faz o print, então aqui pode ser omitido ou usado para controle
                pass

        print("\n" + "="*60, flush=True)
        print("INDEXAÇÃO CONCLUÍDA COM SUCESSO!", flush=True)
        print("="*60 + "\n", flush=True)

        gerar_relatorio_extensoes(extensoes_processadas, extensoes_descartadas)
        gerar_relatorio_tokens(total_tokens_gerados)
    else:
        print("\n" + "="*60, flush=True)
        print(f"Carregando base de dados vetorial existente para '{REPO_NAME}'...", flush=True)
        vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
        print(">>> SUCESSO: Base de dados carregada da memória.", flush=True)
        print("="*60 + "\n", flush=True)
        gerar_relatorio_extensoes(extensoes_processadas, extensoes_descartadas)

    retriever = vectorstore.as_retriever()
    print(f"Servidor pronto. Repositório '{REPO_NAME}' está carregado e pronto para consultas.", flush=True)
    server_ready = True
    print(">>> Servidor ACEITANDO conexões HTTP na porta 8000.", flush=True)

@app.on_event("startup")
def startup_event():
    threading.Thread(target=index_repository, daemon=True).start()

@app.get("/", summary="Verificação de Status")
def read_root():
    if not server_ready:
        return {"status": "Servidor inicializando, aguarde..."}
    return {"status": f"MCP Server online para o repositório: {REPO_NAME}"}

@app.post("/retrieve", response_model=RetrieveResponse, summary="Busca fragmentos de contexto")
def retrieve_context(request: RetrieveRequest):
    if not server_ready:
        raise HTTPException(status_code=503, detail="O servidor ainda está inicializando. Tente novamente em alguns segundos.")

    print(f"Recebida busca por: '{request.query}' com top_k={request.top_k}", flush=True)
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