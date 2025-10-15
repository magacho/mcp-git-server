import os
from langchain_community.document_loaders import DirectoryLoader, JSONLoader, UnstructuredFileLoader

EXTENSOES_SUPORTADAS = [
    ".md", ".ts", ".js", ".tsx", ".jsx", ".py", ".html", ".css", ".txt", ".json", ".pdf"
]

def load_documents_robustly(path: str, extensoes_processadas, extensoes_descartadas):
    for root, _, files in os.walk(path):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            full_path = os.path.abspath(os.path.join(root, fname))
            if ext not in EXTENSOES_SUPORTADAS:
                extensoes_descartadas[ext] += 1
                continue
            try:
                if ext == ".json":
                    loader = JSONLoader(full_path)
                else:
                    loader = UnstructuredFileLoader(full_path)
                for doc in loader.lazy_load():
                    extensoes_processadas[ext] += 1
                    yield doc
            except Exception as e:
                print(f"AVISO: Erro ao processar '{full_path}': {e}")