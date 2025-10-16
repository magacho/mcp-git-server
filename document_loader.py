import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_community.document_loaders import JSONLoader, PyPDFLoader

EXTENSOES_SUPORTADAS = [
    ".md", ".ts", ".js", ".tsx", ".jsx", ".py", ".java", ".html", ".css", ".txt", ".json", ".pdf", 
    ".yml", ".yaml", ".xml", ".sql", ".sh", ".bash", ".dockerfile", ".env", ".gitignore", 
    ".vue", ".svelte", ".go", ".rs", ".cpp", ".c", ".h", ".cs", ".php", ".rb", ".swift", ""
]

# Arquivos especiais sem extensão que devem ser processados
ARQUIVOS_ESPECIAIS = [
    "README", "LICENSE", "CHANGELOG", "CONTRIBUTING", "AUTHORS", "COPYING", 
    "INSTALL", "NEWS", "TODO", "HISTORY", "CREDITS", "MAINTAINERS", "DOCKERFILE",
    "MAKEFILE", "RAKEFILE", "GEMFILE", "PROCFILE"
]

def process_file(full_path, ext):
    try:
        if ext == ".json":
            # Tentar JSONLoader primeiro, se falhar usar processamento manual
            try:
                loader = JSONLoader(full_path, jq_schema='.', text_content=False)
                docs = list(loader.lazy_load())
                if docs:
                    return ext, docs, None
            except Exception:
                # Fallback: processar JSON manualmente
                import json
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    try:
                        json_data = json.load(f)
                        # Converter JSON para texto legível
                        content = json.dumps(json_data, indent=2, ensure_ascii=False)
                        from langchain_core.documents import Document
                        doc = Document(page_content=content, metadata={"source": full_path, "type": "json"})
                        return ext, [doc], None
                    except json.JSONDecodeError:
                        # Se não for JSON válido, tratar como texto
                        f.seek(0)
                        content = f.read()
                        from langchain_core.documents import Document
                        doc = Document(page_content=content, metadata={"source": full_path, "type": "json_text"})
                        return ext, [doc], None
        elif ext == ".pdf":
            loader = PyPDFLoader(full_path)
            docs = list(loader.lazy_load())
            return ext, docs, None
        else:
            # Use um loader simples para texto, markdown, código, etc.
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            # Simule um objeto Document do LangChain
            from langchain_core.documents import Document
            doc = Document(page_content=content, metadata={"source": full_path})
            return ext, [doc], None
    except Exception as e:
        return ext, [], f"AVISO: Erro ao processar '{full_path}': {e}"

def load_documents_robustly(
    path: str,
    extensoes_processadas,
    extensoes_descartadas,
    max_load_workers=None
):
    if max_load_workers is None:
        max_load_workers = min(8, (os.cpu_count() or 1) + 4)
    files_to_process = []
    for root, _, files in os.walk(path):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            full_path = os.path.abspath(os.path.join(root, fname))
            
            # Verificar se é arquivo especial sem extensão
            if ext == "" and fname.upper() in ARQUIVOS_ESPECIAIS:
                # Verificar tamanho do arquivo (máximo 10MB)
                try:
                    if os.path.getsize(full_path) > 10 * 1024 * 1024:
                        extensoes_descartadas[f"{ext}_too_large"] += 1
                        continue
                except OSError:
                    continue
                files_to_process.append((full_path, ext))
                continue
            
            if ext not in EXTENSOES_SUPORTADAS:
                extensoes_descartadas[ext] += 1
                continue
            
            # Verificar tamanho do arquivo (máximo 5MB para arquivos com extensão)
            try:
                file_size = os.path.getsize(full_path)
                if file_size > 5 * 1024 * 1024:
                    extensoes_descartadas[f"{ext}_too_large"] += 1
                    continue
                # Pular arquivos muito pequenos (provavelmente vazios)
                if file_size < 10:
                    extensoes_descartadas[f"{ext}_too_small"] += 1
                    continue
            except OSError:
                continue
                
            files_to_process.append((full_path, ext))

    with ThreadPoolExecutor(max_workers=max_load_workers) as load_executor:
        load_futures = [load_executor.submit(process_file, fp, ext) for fp, ext in files_to_process]
        for future in as_completed(load_futures):
            ext, docs, error = future.result()
            if error:
                print(error, flush=True)
            else:
                extensoes_processadas[ext] += len(docs)
                for doc in docs:
                    yield doc