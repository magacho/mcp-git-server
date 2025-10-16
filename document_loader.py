import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_community.document_loaders import JSONLoader, PyPDFLoader

EXTENSOES_SUPORTADAS = [
    ".md", ".ts", ".js", ".tsx", ".jsx", ".py", ".html", ".css", ".txt", ".json", ".pdf"
]

def process_file(full_path, ext):
    try:
        if ext == ".json":
            loader = JSONLoader(full_path)
        elif ext == ".pdf":
            loader = PyPDFLoader(full_path)
        else:
            # Use um loader simples para texto, markdown, código, etc.
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            # Simule um objeto Document do LangChain
            from langchain_core.documents import Document
            doc = Document(page_content=content, metadata={"source": full_path})
            return ext, [doc], None
        docs = list(loader.lazy_load())
        return ext, docs, None
    except Exception as e:
        return ext, [], f"AVISO: Erro ao processar '{full_path}': {e}"

def load_documents_robustly(
    path: str,
    extensoes_processadas,
    extensoes_descartadas,
    max_load_workers=8
):
    import os
    files_to_process = []
    for root, _, files in os.walk(path):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            full_path = os.path.abspath(os.path.join(root, fname))
            if ext not in EXTENSOES_SUPORTADAS:
                extensoes_descartadas[ext] += 1
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