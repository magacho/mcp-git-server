#!/usr/bin/env python3
"""
Script para testar e comparar diferentes provedores de embedding
"""
import os
import time
from embedding_config import EmbeddingProvider
from token_utils import contar_tokens, estimar_custo_embeddings

def test_embedding_providers():
    """Testa todos os provedores disponíveis"""
    
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
            print(f"❌ Não disponível: {info.get('reason', 'Motivo desconhecido')}")
            print()
            continue
        
        try:
            print(f"✅ Disponível")
            print(f"   Custo: {info.get('cost', 'N/A')}")
            print(f"   Qualidade: {info.get('quality', 'N/A')}")
            print(f"   Velocidade: {info.get('speed', 'N/A')}")
            
            if 'model' in info:
                print(f"   Modelo: {info['model']}")
            
            # Teste de embedding
            start_time = time.time()
            embeddings = EmbeddingProvider.get_embeddings(provider_name)
            
            # Teste com texto pequeno
            result = embeddings.embed_query("teste rápido")
            end_time = time.time()
            
            print(f"   Dimensões do vetor: {len(result)}")
            print(f"   Tempo para embedding: {end_time - start_time:.2f}s")
            
        except Exception as e:
            print(f"❌ Erro ao testar: {e}")
        
        print()

def test_token_counting():
    """Testa diferentes métodos de contagem de tokens"""
    
    test_texts = [
        "Texto curto para teste",
        "Este é um texto médio que contém várias palavras e deveria ter uma contagem de tokens razoável para comparação entre métodos.",
        """
        def exemplo_codigo():
            # Este é um exemplo de código Python
            for i in range(10):
                print(f"Número: {i}")
                if i % 2 == 0:
                    continue
                else:
                    break
        """ * 10  # Texto longo
    ]
    
    print("=== TESTE DE CONTAGEM DE TOKENS ===\n")
    
    for i, text in enumerate(test_texts, 1):
        print(f"--- TEXTO {i} ({len(text)} caracteres) ---")
        
        # Teste diferentes métodos
        methods = ["local", "tiktoken"]
        
        for method in methods:
            try:
                start_time = time.time()
                tokens = contar_tokens(text, method)
                end_time = time.time()
                
                print(f"{method:>10}: {tokens:>6} tokens ({end_time - start_time:.4f}s)")
                
            except Exception as e:
                print(f"{method:>10}: Erro - {e}")
        
        print()

def test_cost_estimation():
    """Testa estimativa de custos"""
    
    print("=== ESTIMATIVA DE CUSTOS ===\n")
    
    token_amounts = [1000, 10000, 100000, 1000000]
    
    for tokens in token_amounts:
        print(f"--- {tokens:,} tokens ---")
        
        # OpenAI
        openai_cost = estimar_custo_embeddings(tokens, "openai")
        print(f"OpenAI: ${openai_cost['custo_usd']:.4f} USD / R${openai_cost['custo_brl']:.2f} BRL")
        
        # Local
        local_cost = estimar_custo_embeddings(tokens, "sentence-transformers")
        print(f"Local:  {local_cost['nota']}")
        
        print()

if __name__ == "__main__":
    print("🧪 INICIANDO TESTES DE EMBEDDING E TOKENIZAÇÃO\n")
    
    try:
        test_embedding_providers()
        test_token_counting()
        test_cost_estimation()
        
        print("✅ Todos os testes concluídos!")
        
    except KeyboardInterrupt:
        print("\n❌ Testes interrompidos pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")