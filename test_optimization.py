#!/usr/bin/env python3
"""
Teste das otimizações de embedding
"""
from embedding_optimizer import get_optimal_config, get_processing_strategy, estimate_processing_time

def test_optimizations():
    """Testa as otimizações para diferentes cenários"""
    
    providers = ["openai", "sentence-transformers", "huggingface"]
    document_counts = [100, 1000, 5000, 10000]
    
    print("🧪 Testando Otimizações de Embedding")
    print("=" * 60)
    
    for provider in providers:
        print(f"\n🤖 Provedor: {provider.upper()}")
        print("-" * 40)
        
        strategy = get_processing_strategy(provider)
        print(f"Rate Limiting: {strategy['rate_limiting']}")
        print(f"Parallel Safe: {strategy['parallel_safe']}")
        
        for doc_count in document_counts:
            batch_size, max_workers = get_optimal_config(provider, doc_count)
            time_est = estimate_processing_time(provider, doc_count, 2000)  # 2KB avg doc
            
            print(f"\n  📊 {doc_count:,} documentos:")
            print(f"     Batch Size: {batch_size}")
            print(f"     Workers: {max_workers}")
            print(f"     Tempo Estimado: {time_est['estimated_time_str']}")

if __name__ == "__main__":
    test_optimizations()