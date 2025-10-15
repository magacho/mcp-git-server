import os
from langchain_community.document_loaders import DirectoryLoader

EXTENSOES_SUPORTADAS = [
    ".md", ".ts", ".js", ".tsx", ".jsx", ".py", ".html", ".css", ".txt"
]

def load_documents_robustly(path: str, extensoes_processadas, extensoes_descartadas):
    glob_patterns = [
        "**/*.md", "**/*.ts", "**/*.js", "**/*.tsx", "**/*.jsx",
        "**/*.py", "**/*.html", "**/*.css", "**/*.txt"
    ]
    arquivos_verificados = set()
    for pattern in glob_patterns:
        try:
            loader = DirectoryLoader(
                path, glob=pattern, recursive=True, show_progress=True,
                use_multithreading=True, silent_errors=True
            )
            for doc in loader.lazy_load():
                ext = os.path.splitext(doc.metadata.get("source", ""))[1].lower()
                extensoes_processadas[ext] += 1
                arquivos_verificados.add(os.path.abspath(doc.metadata.get("source", "")))
                yield doc
        except Exception as e:
            print(f"AVISO: Erro ao processar '{pattern}': {e}")
            continue
    for root, _, files in os.walk(path):
        for fname in files:
            full_path = os.path.abspath(os.path.join(root, fname))
            if full_path in arquivos_verificados:
                continue
            ext = os.path.splitext(fname)[1].lower()
            if ext not in EXTENSOES_SUPORTADAS:
                extensoes_descartadas[ext] += 1