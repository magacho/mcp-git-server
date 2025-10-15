import tiktoken

def contar_tokens_openai(texto: str, model: str = "text-embedding-ada-002") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except Exception:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(texto))