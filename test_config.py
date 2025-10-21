#!/usr/bin/env python3
"""
Quick test of default configuration
"""
import os
from embedding_config import EmbeddingProvider

def test_default_config():
    print("🧪 Testing default configuration...")
    
    # Remover OPENAI_API_KEY se existir para testar padrão
    original_key = os.environ.pop('OPENAI_API_KEY', None)
    
    try:
        # Test default configuration (should be sentence-transformers)
        embeddings = EmbeddingProvider.get_embeddings()
        print("✅ Default configuration: sentence-transformers")
        
        # Testar auto-detect
        embeddings_auto = EmbeddingProvider.get_embeddings('auto')
        print("✅ Auto-detect: sentence-transformers")
        
        # Mostrar provedores disponíveis
        providers = EmbeddingProvider.get_available_providers()
        print("\n📋 Provedores disponíveis:")
        for name, info in providers.items():
            status = "✅" if info.get('available') else "❌"
            cost = info.get('cost', 'N/A')
            print(f"  {status} {name}: {cost}")
        
        print("\n🎯 Default configuration is correct!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Restaurar chave se existia
        if original_key:
            os.environ['OPENAI_API_KEY'] = original_key

if __name__ == "__main__":
    test_default_config()