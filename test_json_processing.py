#!/usr/bin/env python3
"""
Script para testar o processamento de arquivos JSON
"""
import os
import json
from document_loader import process_file

def test_json_files():
    """Testa diferentes tipos de arquivos JSON"""
    
    # Criar arquivos de teste
    test_files = {
        "test_simple.json": {"name": "test", "value": 123},
        "test_complex.json": {
            "users": [
                {"id": 1, "name": "João", "email": "joao@test.com"},
                {"id": 2, "name": "Maria", "email": "maria@test.com"}
            ],
            "config": {
                "debug": True,
                "timeout": 30,
                "features": ["auth", "logging", "cache"]
            }
        },
        "test_invalid.json": "{ invalid json content",
        "test_large.json": {"data": [i for i in range(1000)]}
    }
    
    # Criar diretório de teste
    test_dir = "test_json_files"
    os.makedirs(test_dir, exist_ok=True)
    
    try:
        # Criar arquivos de teste
        for filename, content in test_files.items():
            filepath = os.path.join(test_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                if isinstance(content, str):
                    f.write(content)
                else:
                    json.dump(content, f, indent=2, ensure_ascii=False)
        
        print("🧪 Testando processamento de arquivos JSON...")
        print("=" * 50)
        
        # Test each file
        for filename in test_files.keys():
            filepath = os.path.join(test_dir, filename)
            print(f"\n📄 Testando: {filename}")
            
            try:
                ext, docs, error = process_file(filepath, ".json")
                
                if error:
                    print(f"❌ Error: {error}")
                elif docs:
                    print(f"✅ Processed successfully!")
                    print(f"   Documents generated: {len(docs)}")
                    for i, doc in enumerate(docs):
                        content_preview = doc.page_content[:100].replace('\n', ' ')
                        print(f"   Doc {i+1}: {content_preview}...")
                        print(f"   Metadata: {doc.metadata}")
                else:
                    print("⚠️  Nenhum documento gerado")
                    
            except Exception as e:
                print(f"💥 Exceção: {e}")
    
    finally:
        # Limpar arquivos de teste
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        print(f"\n🧹 Limpeza concluída: {test_dir} removido")

if __name__ == "__main__":
    test_json_files()