import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_community.document_loaders import JSONLoader, PyPDFLoader

SUPPORTED_EXTENSIONS = [
    ".md", ".ts", ".js", ".tsx", ".jsx", ".py", ".java", ".html", ".css", ".txt", ".json", ".pdf", 
    ".yml", ".yaml", ".xml", ".sql", ".sh", ".bash", ".dockerfile", ".env", ".gitignore", 
    ".vue", ".svelte", ".go", ".rs", ".cpp", ".c", ".h", ".cs", ".php", ".rb", ".swift", ""
]

# Special files without extension that should be processed
SPECIAL_FILES = [
    "README", "LICENSE", "CHANGELOG", "CONTRIBUTING", "AUTHORS", "COPYING", 
    "INSTALL", "NEWS", "TODO", "HISTORY", "CREDITS", "MAINTAINERS", "DOCKERFILE",
    "MAKEFILE", "RAKEFILE", "GEMFILE", "PROCFILE"
]

def process_file(full_path, ext):
    """
    Process a single file and return its content as a document
    
    Args:
        full_path: Full path to the file
        ext: File extension
        
    Returns:
        Tuple of (extension, documents, error)
    """
    try:
        if ext == ".json":
            # Try JSONLoader first, fallback to manual processing if it fails
            try:
                loader = JSONLoader(full_path, jq_schema='.', text_content=False)
                docs = list(loader.lazy_load())
                if docs:
                    return ext, docs, None
            except Exception:
                # Fallback: process JSON manually
                import json
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    try:
                        json_data = json.load(f)
                        # Convert JSON to readable text
                        content = json.dumps(json_data, indent=2, ensure_ascii=False)
                        from langchain_core.documents import Document
                        doc = Document(page_content=content, metadata={"source": full_path, "type": "json"})
                        return ext, [doc], None
                    except json.JSONDecodeError:
                        # If not valid JSON, treat as text
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
            # Use simple loader for text, markdown, code, etc.
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            # Simulate a LangChain Document object
            from langchain_core.documents import Document
            doc = Document(page_content=content, metadata={"source": full_path})
            return ext, [doc], None
    except Exception as e:
        return ext, [], f"WARNING: Error processing '{full_path}': {e}"

def load_documents_robustly(
    path: str,
    processed_extensions,
    discarded_extensions,
    max_load_workers=None
):
    """
    Load documents from a directory robustly with parallel processing
    
    Args:
        path: Directory path to load documents from
        processed_extensions: Dictionary to track processed file extensions
        discarded_extensions: Dictionary to track discarded file extensions
        max_load_workers: Maximum number of worker threads
        
    Yields:
        Loaded documents
    """
    if max_load_workers is None:
        max_load_workers = min(8, (os.cpu_count() or 1) + 4)
    files_to_process = []
    for root, _, files in os.walk(path):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            full_path = os.path.abspath(os.path.join(root, fname))
            
            # Check if it's a special file without extension
            if ext == "" and fname.upper() in SPECIAL_FILES:
                # Check file size (max 10MB)
                try:
                    if os.path.getsize(full_path) > 10 * 1024 * 1024:
                        discarded_extensions[f"{ext}_too_large"] += 1
                        continue
                except OSError:
                    continue
                files_to_process.append((full_path, ext))
                continue
            
            if ext not in SUPPORTED_EXTENSIONS:
                discarded_extensions[ext] += 1
                continue
            
            # Check file size (max 5MB for files with extension)
            try:
                file_size = os.path.getsize(full_path)
                if file_size > 5 * 1024 * 1024:
                    discarded_extensions[f"{ext}_too_large"] += 1
                    continue
                # Skip very small files (probably empty)
                if file_size < 10:
                    discarded_extensions[f"{ext}_too_small"] += 1
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
                processed_extensions[ext] += len(docs)
                for doc in docs:
                    yield doc