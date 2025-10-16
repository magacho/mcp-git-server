import os
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from collections import defaultdict
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import asyncio

from models import RetrieveRequest, DocumentFragment, RetrieveResponse
from repo_utils import get_repo_name_from_url, clone_repo
from document_loader import load_documents_robustly, EXTENSOES_SUPORTADAS
from token_utils import contar_tokens, estimar_custo_embeddings
from report_utils import gerar_relatorio_extensoes, gerar_relatorio_tokens
from embedding_config import EmbeddingProvider

# --- CONFIGURAÇÃO A PARTIR DE VARIÁVEIS DE AMBIENTE ---
REPO_URL = os.environ.get("REPO_URL")
if not REPO_URL:
    raise ValueError("A variável de ambiente REPO_URL não foi definida.")

# Configuração flexível de embeddings - padrão local (gratuito)
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "sentence-transformers")
TOKEN_COUNT_METHOD = os.getenv("TOKENIZER_MODE", os.getenv("TOKEN_COUNT_METHOD", "local"))

REPO_NAME = get_repo_name_from_url(REPO_URL)
LOCAL_REPO_PATH = f"/app/repos/{REPO_NAME}" 
DB_PATH = f"/app/chroma_db/{REPO_NAME}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await asyncio.to_thread(index_repository)
    yield
    # Shutdown - cleanup se necessário
    pass

# --- INICIALIZAÇÃO DA API ---
app = FastAPI(
    title="Servidor de Recuperação de Contexto (MCP)",
    description="Uma API que recebe uma pergunta e retorna trechos relevantes de um repositório GitHub.",
    version="1.0.0",
    lifespan=lifespan
)

vectorstore = None
retriever = None

extensoes_processadas = defaultdict(int)
extensoes_descartadas = defaultdict(int)
total_tokens_gerados = 0

server_ready = False  # Flag global

def index_repository():
    global vectorstore, retriever, total_tokens_gerados, server_ready
    
    # Configurar embeddings baseado na configuração
    try:
        embeddings = EmbeddingProvider.get_embeddings(EMBEDDING_PROVIDER)
        providers_info = EmbeddingProvider.get_available_providers()
        
        # Log da configuração escolhida
        current_provider = EMBEDDING_PROVIDER if EMBEDDING_PROVIDER != "auto" else "auto-detectado"
        print(f">>> Usando embeddings: {current_provider}", flush=True)
        
        if EMBEDDING_PROVIDER in providers_info:
            info = providers_info[EMBEDDING_PROVIDER]
            if info.get("available"):
                print(f">>> Custo: {info.get('cost', 'N/A')}, Qualidade: {info.get('quality', 'N/A')}", flush=True)
    
    except Exception as e:
        print(f"Erro ao configurar embeddings: {e}", flush=True)
        print("Tentando fallback para sentence-transformers...", flush=True)
        embeddings = EmbeddingProvider.get_embeddings("sentence-transformers")

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

        # Contagem eficiente de tokens
        print(">>> Calculando tokens...", flush=True)
        total_tokens_gerados = sum(contar_tokens(doc.page_content, TOKEN_COUNT_METHOD) for doc in chunks)
        
        # Estimativa de custo
        custo_info = estimar_custo_embeddings(total_tokens_gerados, EMBEDDING_PROVIDER)
        print(f">>> Total estimado de tokens: {total_tokens_gerados}", flush=True)
        print(f">>> Custo estimado: {custo_info}", flush=True)

        print("\n--- ETAPA 3 de 3: Gerando e Armazenando Embeddings ---", flush=True)
        vectorstore = Chroma(
            persist_directory=DB_PATH,
            embedding_function=embeddings
        )

        batch_size = 500
        total_batches = (len(chunks) - 1) // batch_size + 1

        # Controle de tokens por minuto
        TOKEN_LIMIT_PER_MINUTE = 900000
        tokens_this_minute = 0
        minute_start = time.time()

        def send_batch(batch, batch_num, total_batches, total_chars):
            nonlocal tokens_this_minute, minute_start
            batch_tokens = sum(contar_tokens(doc.page_content, "local") for doc in batch)

            # Aguarda se passar do limite de tokens por minuto
            while tokens_this_minute + batch_tokens > TOKEN_LIMIT_PER_MINUTE:
                elapsed = time.time() - minute_start
                if elapsed < 60:
                    wait_time = 60 - elapsed
                    print(f"     Aguardando {wait_time:.1f}s para respeitar o limite de {TOKEN_LIMIT_PER_MINUTE} tokens/minuto...", flush=True)
                    time.sleep(wait_time)
                tokens_this_minute = 0
                minute_start = time.time()

            print(f"  -> Preparando lote {batch_num}/{total_batches} ({len(batch)} documentos, ~{total_chars} caracteres)...", flush=True)
            print("     Enviando para a API da OpenAI e aguardando resposta (pode levar alguns minutos)...", flush=True)
            try:
                vectorstore.add_documents(documents=batch)
                tokens_this_minute += batch_tokens
                print(f"     Lote {batch_num} processado com sucesso! ({batch_tokens} tokens)", flush=True)
                return len(batch)
            except Exception as e:
                print(f"     ERRO no lote {batch_num}: {e}", flush=True)
                return 0

        # Usar número otimizado de workers baseado no CPU
        max_workers = min(4, os.cpu_count() or 1)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                current_batch_num = i // batch_size + 1
                total_chars = sum(len(doc.page_content) for doc in batch)
                futures.append(executor.submit(send_batch, batch, current_batch_num, total_batches, total_chars))
            for future in as_completed(futures):
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

# Event handler removido - agora usando lifespan

@app.get("/", summary="Verificação de Status")
def read_root():
    if not server_ready:
        return {"status": "Servidor inicializando, aguarde..."}
    return {"status": f"MCP Server online para o repositório: {REPO_NAME}"}

@app.get("/health", summary="Health Check")
def health_check():
    return {
        "status": "healthy" if server_ready else "initializing",
        "repository": REPO_NAME,
        "ready": server_ready
    }

@app.get("/embedding-info", summary="Informações sobre Embeddings")
def embedding_info():
    """Retorna informações sobre os provedores de embedding disponíveis"""
    providers = EmbeddingProvider.get_available_providers()
    return {
        "current_provider": EMBEDDING_PROVIDER,
        "token_count_method": TOKEN_COUNT_METHOD,
        "available_providers": providers,
        "total_tokens_processed": total_tokens_gerados if server_ready else 0
    }

@app.post("/retrieve", response_model=RetrieveResponse, summary="Busca fragmentos de contexto")
def retrieve_context(request: RetrieveRequest):
    if not server_ready:
        raise HTTPException(status_code=503, detail="O servidor ainda está inicializando. Tente novamente em alguns segundos.")

    try:
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
    
    except Exception as e:
        print(f"Erro durante a busca: {e}", flush=True)
        raise HTTPException(status_code=500, detail=f"Erro interno durante a busca: {str(e)}")