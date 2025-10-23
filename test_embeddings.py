#!/usr/bin/env python3
"""
Script para testar e comparar diferentes provedores de embedding
"""
import os
import time
from embedding_config import EmbeddingProvider
from token_utils import count_tokens, estimate_embedding_cost

def test_embedding_providers():
    """Tests all available providers"""
    
    # Texto de teste
    test_text = """
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    
    # Este é um exemplo de código Python
    # que implementa a sequência de Fibonacci
    """
    
    print("=== TESTE DE PROVEDORES DE EMBEDDING ===\n")
    
    providers = EmbeddingProvider.get_available_providers()
    
    for provider_name, info in providers.items():
        print(f"--- {provider_name.upper()} ---")
        
        if not info.get("available", False):
            print(f"❌ Not available: {info.get('reason', 'Unknown reason')}")
            print()
            continue
        
        try:
            print(f"✅ Available")
            print(f"   Cost: {info.get('cost', 'N/A')}")
            print(f"   Quality: {info.get('quality', 'N/A')}")
            print(f"   Speed: {info.get('speed', 'N/A')}")
            
            if 'model' in info:
                print(f"   Model: {info['model']}")
            
            # Embedding test
            start_time = time.time()
            embeddings = EmbeddingProvider.get_embeddings(provider_name)
            
            # Test with small text
            result = embeddings.embed_query("quick test")
            end_time = time.time()
            
            print(f"   Vector dimensions: {len(result)}")
            print(f"   Time for embedding: {end_time - start_time:.2f}s")
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
        
        print()

def test_token_counting():
    """Tests different token counting methods"""
    
    test_texts = [
        "Short text for testing",
        "This is a medium text that contains several words and should have a reasonable token count for comparison between methods.",
        """
        def example_code():
            # This is a Python code example
            for i in range(10):
                print(f"Number: {i}")
                if i % 2 == 0:
                    continue
                else:
                    break
        """ * 10  # Texto longo
    ]
    
    print("=== TESTE DE CONTAGEM DE TOKENS ===\n")
    
    for i, text in enumerate(test_texts, 1):
        print(f"--- TEXT {i} ({len(text)} characters) ---")
        
        # Test different methods
        methods = ["local", "tiktoken"]
        
        for method in methods:
            try:
                start_time = time.time()
                tokens = count_tokens(text, method)
                end_time = time.time()
                
                print(f"{method:>10}: {tokens:>6} tokens ({end_time - start_time:.4f}s)")
                
            except Exception as e:
                print(f"{method:>10}: Error - {e}")
        
        print()

def test_cost_estimation():
    """Tests cost estimation"""
    
    print("=== COST ESTIMATION ===\n")
    
    token_amounts = [1000, 10000, 100000, 1000000]
    
    for tokens in token_amounts:
        print(f"--- {tokens:,} tokens ---")
        
        # OpenAI
        openai_cost = estimate_embedding_cost(tokens, "openai")
        print(f"OpenAI: ${openai_cost['cost_usd']:.4f} USD / R${openai_cost['cost_brl']:.2f} BRL")
        
        # Local
        local_cost = estimate_embedding_cost(tokens, "sentence-transformers")
        print(f"Local:  {local_cost['note']}")
        
        print()

if __name__ == "__main__":
    print("🧪 STARTING EMBEDDING AND TOKENIZATION TESTS\n")
    
    try:
        test_embedding_providers()
        test_token_counting()
        test_cost_estimation()
        
        print("✅ All tests completed!")
        
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during tests: {e}")