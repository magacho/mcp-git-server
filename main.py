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
from token_utils import count_tokens, estimate_embedding_cost
from report_utils import generate_extensions_report, generate_tokens_report
from embedding_config import EmbeddingProvider
from embedding_optimizer import get_optimal_config, get_processing_strategy, estimate_processing_time

# --- CONFIGURAÇÃO A PARTIR DE VARIÁVEIS DE AMBIENTE ---
REPO_URL = os.environ.get("REPO_URL")
if not REPO_URL:
    raise ValueError("A variável de ambiente REPO_URL não foi definida.")

# Configuration flexível de embeddings - padrão local (gratuito)
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
    title="Context Retrieval Server (MCP)",
    description="An API that receives a question and returns relevant snippets from a GitHub repository.",
    version="1.0.0",
    lifespan=lifespan
)

vectorstore = None
retriever = None

processed_extensions = defaultdict(int)
discarded_extensions = defaultdict(int)
total_tokens_generated = 0

server_ready = False  # Flag global

def index_repository():
    global vectorstore, retriever, total_tokens_generated, server_ready
    
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
        print("STARTING INDEXATION PROCESS (FIRST RUN)", flush=True)
        print(f"Repository: {REPO_NAME}", flush=True)
        print("="*60, flush=True)

        print("\n--- STEP 1 of 3: Cloning and Loading Repository ---", flush=True)
        repo_branch = os.getenv("REPO_BRANCH", "main")
        github_token = os.getenv("GITHUB_TOKEN")  # Support for private repositories
        
        if github_token:
            print(">>> GitHub token detected - will use for authentication", flush=True)
        
        clone_repo(REPO_URL, repo_branch, LOCAL_REPO_PATH, github_token=github_token)

        documents = list(load_documents_robustly(LOCAL_REPO_PATH, processed_extensions, discarded_extensions))
        if not documents:
            raise Exception("No documents loaded. Check file patterns.")

        print(f">>> SUCCESS: Step 1 completed.", flush=True)

        print("\n--- STEP 2 of 3: Splitting Documents ---", flush=True)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        print(f">>> SUCCESS: Documents split into {len(chunks)} chunks.", flush=True)

        # Efficient counting de tokens
        print(">>> Calculating tokens...", flush=True)
        total_tokens_generated = sum(count_tokens(doc.page_content, TOKEN_COUNT_METHOD) for doc in chunks)
        
        # Cost estimation
        cost_info = estimate_embedding_cost(total_tokens_generated, EMBEDDING_PROVIDER)
        print(f">>> Total estimated tokens: {total_tokens_generated}", flush=True)
        print(f">>> Estimated cost: {cost_info}", flush=True)

        print("\n--- STEP 3 of 3: Generating and Storing Embeddings ---", flush=True)
        vectorstore = Chroma(
            persist_directory=DB_PATH,
            embedding_function=embeddings
        )

        # Configuration otimizada baseada no provedor e recursos
        batch_size, max_workers = get_optimal_config(EMBEDDING_PROVIDER, len(chunks))
        strategy = get_processing_strategy(EMBEDDING_PROVIDER)
        
        # Estimar tempo de processamento
        avg_doc_size = sum(len(doc.page_content) for doc in chunks) // len(chunks)
        time_estimate = estimate_processing_time(EMBEDDING_PROVIDER, len(chunks), avg_doc_size)
        
        print(f">>> Configuração otimizada: batch_size={batch_size}, workers={max_workers}", flush=True)
        print(f">>> Tempo estimado: {time_estimate['estimated_time_str']}", flush=True)
        
        is_openai = EMBEDDING_PROVIDER == "openai"
        TOKEN_LIMIT_PER_MINUTE = strategy.get("token_limit_per_minute")

        total_batches = (len(chunks) - 1) // batch_size + 1
        tokens_this_minute = 0
        minute_start = time.time()

        def send_batch_openai(batch, batch_num, total_batches, total_chars):
            """Versão com rate limiting para OpenAI"""
            nonlocal tokens_this_minute, minute_start
            batch_tokens = sum(count_tokens(doc.page_content, "local") for doc in batch)

            # Aguarda se passar do limite de tokens por minuto
            while tokens_this_minute + batch_tokens > TOKEN_LIMIT_PER_MINUTE:
                elapsed = time.time() - minute_start
                if elapsed < 60:
                    wait_time = 60 - elapsed
                    print(f"     Aguardando {wait_time:.1f}s para respeitar o limite de {TOKEN_LIMIT_PER_MINUTE} tokens/minuto...", flush=True)
                    time.sleep(wait_time)
                tokens_this_minute = 0
                minute_start = time.time()

            print(f"  -> Lote {batch_num}/{total_batches} ({len(batch)} docs, ~{total_chars} chars)...", flush=True)
            print("     Enviando para OpenAI API...", flush=True)
            try:
                vectorstore.add_documents(documents=batch)
                tokens_this_minute += batch_tokens
                print(f"     ✅ Lote {batch_num} processado! ({batch_tokens} tokens)", flush=True)
                return len(batch)
            except Exception as e:
                print(f"     ❌ ERRO no lote {batch_num}: {e}", flush=True)
                return 0

        def send_batch_local(batch, batch_num, total_batches, total_chars):
            """Versão otimizada para embeddings locais"""
            print(f"  -> Lote {batch_num}/{total_batches} ({len(batch)} docs, ~{total_chars} chars)...", flush=True)
            try:
                vectorstore.add_documents(documents=batch)
                print(f"     ✅ Lote {batch_num} processado!", flush=True)
                return len(batch)
            except Exception as e:
                print(f"     ❌ ERRO no lote {batch_num}: {e}", flush=True)
                return 0

        # Escolher função de processamento
        send_batch = send_batch_openai if is_openai else send_batch_local

        print(f">>> Processing {len(chunks)} documents in {total_batches} batches (batch_size={batch_size}, workers={max_workers})", flush=True)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                current_batch_num = i // batch_size + 1
                total_chars = sum(len(doc.page_content) for doc in batch)
                futures.append(executor.submit(send_batch, batch, current_batch_num, total_batches, total_chars))
            
            # Aguardar conclusão
            for future in as_completed(futures):
                pass

        print("\n" + "="*60, flush=True)
        print("INDEXATION COMPLETED SUCCESSFULLY!", flush=True)
        print("="*60 + "\n", flush=True)

        generate_extensions_report(processed_extensions, discarded_extensions)
        generate_tokens_report(total_tokens_generated)
    else:
        print("\n" + "="*60, flush=True)
        print(f"Carregando base de dados vetorial existente para '{REPO_NAME}'...", flush=True)
        vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
        print(">>> SUCCESS: Database loaded from memory.", flush=True)
        print("="*60 + "\n", flush=True)
        generate_extensions_report(processed_extensions, discarded_extensions)

    retriever = vectorstore.as_retriever()
    print(f"Server ready. Repository '{REPO_NAME}' is loaded and ready for queries.", flush=True)
    server_ready = True
    print(">>> Server ACCEPTING HTTP connections on port 8000.", flush=True)

# Event handler removido - agora usando lifespan

@app.get("/", summary="Verificação de Status")
def read_root():
    if not server_ready:
        return {"status": "Server initializing, please wait..."}
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
        "total_tokens_processed": total_tokens_generated if server_ready else 0
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