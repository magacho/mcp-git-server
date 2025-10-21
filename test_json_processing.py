#!/usr/bin/env python3
"""
Script para testar o processamento de arquivos JSON
"""
import os
import json
from document_loader import process_file

def test_json_files():
    """Tests different types of JSON files"""
    
    # Create test files
    test_files = {
        "test_simple.json": {"name": "test", "value": 123},
        "test_complex.json": {
            "users": [
                {"id": 1, "name": "John", "email": "john@test.com"},
                {"id": 2, "name": "Mary", "email": "mary@test.com"}
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
    
    # Create test directory
    test_dir = "test_json_files"
    os.makedirs(test_dir, exist_ok=True)
    
    try:
        # Create test files
        for filename, content in test_files.items():
            filepath = os.path.join(test_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                if isinstance(content, str):
                    f.write(content)
                else:
                    json.dump(content, f, indent=2, ensure_ascii=False)
        
        print("🧪 Testing JSON file processing...")
        print("=" * 50)
        
        # Test each file
        for filename in test_files.keys():
            filepath = os.path.join(test_dir, filename)
            print(f"\n📄 Testing: {filename}")
            
            try:
                ext, docs, error = process_file(filepath, ".json")
                
                if error:
                    print(f"❌ Error: {error}")
                elif docs:
                    print(f"✅ Processed successfully!")
                    print(f"   Generated documents: {len(docs)}")
                    for i, doc in enumerate(docs):
                        content_preview = doc.page_content[:100].replace('\n', ' ')
                        print(f"   Doc {i+1}: {content_preview}...")
                        print(f"   Metadata: {doc.metadata}")
                else:
                    print("⚠️  No documents generated")
                    
            except Exception as e:
                print(f"💥 Exception: {e}")
    
    finally:
        # Clean up test files
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        print(f"\n🧹 Cleanup completed: {test_dir} removed")

if __name__ == "__main__":
    test_json_files()