"""
Tests for embedding_optimizer.py - Optimization logic
"""
import pytest
from unittest.mock import patch, MagicMock
from embedding_optimizer import (
    get_optimal_config,
    get_processing_strategy,
    estimate_processing_time
)


class TestGetOptimalConfig:
    """Tests for get_optimal_config function"""
    
    def test_openai_config_small_dataset(self):
        """Test OpenAI config with small dataset"""
        batch_size, max_workers = get_optimal_config("openai", 100)
        
        assert batch_size >= 50
        assert batch_size <= 500
        assert max_workers <= 2
    
    def test_openai_config_large_dataset(self):
        """Test OpenAI config with large dataset"""
        batch_size, max_workers = get_optimal_config("openai", 10000)
        
        assert batch_size <= 500
        assert max_workers <= 2
    
    @patch('psutil.virtual_memory')
    @patch('os.cpu_count')
    def test_sentence_transformers_high_resources(self, mock_cpu, mock_memory):
        """Test sentence-transformers with high resources"""
        mock_cpu.return_value = 16
        mock_memory.return_value = MagicMock(total=16 * 1024**3)  # 16GB
        
        batch_size, max_workers = get_optimal_config("sentence-transformers", 5000)
        
        assert batch_size >= 200
        assert batch_size <= 2000
        assert max_workers <= 8
    
    @patch('psutil.virtual_memory')
    @patch('os.cpu_count')
    def test_sentence_transformers_medium_resources(self, mock_cpu, mock_memory):
        """Test sentence-transformers with medium resources"""
        mock_cpu.return_value = 4
        mock_memory.return_value = MagicMock(total=8 * 1024**3)  # 8GB
        
        batch_size, max_workers = get_optimal_config("sentence-transformers", 5000)
        
        assert batch_size >= 100
        assert batch_size <= 1000
        assert max_workers <= 6
    
    @patch('psutil.virtual_memory')
    @patch('os.cpu_count')
    def test_sentence_transformers_low_resources(self, mock_cpu, mock_memory):
        """Test sentence-transformers with low resources"""
        mock_cpu.return_value = 2
        mock_memory.return_value = MagicMock(total=4 * 1024**3)  # 4GB
        
        batch_size, max_workers = get_optimal_config("sentence-transformers", 5000)
        
        assert batch_size >= 50
        assert batch_size <= 500
        assert max_workers <= 4
    
    def test_sentence_transformers_very_small_dataset(self):
        """Test sentence-transformers with very small dataset"""
        batch_size, max_workers = get_optimal_config("sentence-transformers", 50)
        
        assert batch_size <= 50
        assert max_workers <= 2
    
    def test_huggingface_provider(self):
        """Test huggingface provider (should behave like sentence-transformers)"""
        batch_size, max_workers = get_optimal_config("huggingface", 1000)
        
        assert batch_size > 0
        assert max_workers > 0
    
    def test_unknown_provider_fallback(self):
        """Test unknown provider uses fallback config"""
        batch_size, max_workers = get_optimal_config("unknown-provider", 1000)
        
        assert batch_size >= 100
        assert batch_size <= 1000
        assert max_workers > 0
    
    @patch('os.cpu_count')
    def test_single_cpu_system(self, mock_cpu):
        """Test on system with single CPU"""
        mock_cpu.return_value = 1
        
        batch_size, max_workers = get_optimal_config("sentence-transformers", 500)
        
        assert max_workers >= 1
    
    @patch('os.cpu_count')
    def test_cpu_count_none(self, mock_cpu):
        """Test when cpu_count returns None"""
        mock_cpu.return_value = None
        
        batch_size, max_workers = get_optimal_config("openai", 500)
        
        assert batch_size > 0
        assert max_workers > 0


class TestGetProcessingStrategy:
    """Tests for get_processing_strategy function"""
    
    def test_openai_strategy(self):
        """Test OpenAI processing strategy"""
        strategy = get_processing_strategy("openai")
        
        assert strategy["rate_limiting"] is True
        assert strategy["token_limit_per_minute"] == 900000
        assert strategy["retry_attempts"] == 3
        assert strategy["retry_delay"] == 5
        assert strategy["parallel_safe"] is False
    
    def test_sentence_transformers_strategy(self):
        """Test sentence-transformers strategy"""
        strategy = get_processing_strategy("sentence-transformers")
        
        assert strategy["rate_limiting"] is False
        assert strategy["token_limit_per_minute"] is None
        assert strategy["retry_attempts"] == 2
        assert strategy["retry_delay"] == 1
        assert strategy["parallel_safe"] is True
    
    def test_huggingface_strategy(self):
        """Test huggingface strategy"""
        strategy = get_processing_strategy("huggingface")
        
        assert strategy["rate_limiting"] is False
        assert strategy["parallel_safe"] is True
    
    def test_unknown_provider_strategy(self):
        """Test unknown provider strategy"""
        strategy = get_processing_strategy("custom-provider")
        
        assert "rate_limiting" in strategy
        assert "retry_attempts" in strategy
        assert "parallel_safe" in strategy
    
    def test_strategy_has_all_keys(self):
        """Test that all strategies have required keys"""
        required_keys = [
            "rate_limiting",
            "token_limit_per_minute",
            "retry_attempts",
            "retry_delay",
            "progress_frequency",
            "parallel_safe"
        ]
        
        for provider in ["openai", "sentence-transformers", "unknown"]:
            strategy = get_processing_strategy(provider)
            for key in required_keys:
                assert key in strategy, f"Missing key {key} for provider {provider}"


class TestEstimateProcessingTime:
    """Tests for estimate_processing_time function"""
    
    def test_openai_time_estimate_small(self):
        """Test OpenAI time estimate for small dataset"""
        result = estimate_processing_time("openai", 100, 1000)
        
        assert result["estimated_seconds"] > 0
        assert result["provider"] == "openai"
        assert result["total_documents"] == 100
        assert "estimated_time_str" in result
    
    def test_openai_time_estimate_large(self):
        """Test OpenAI time estimate for large dataset"""
        MIN_SECONDS_PER_DOCUMENT = 1.0  # Minimum processing time per document
        result = estimate_processing_time("openai", 5000, 1000)
        
        # Should take longer for more documents
        assert result["estimated_seconds"] >= 5000 * MIN_SECONDS_PER_DOCUMENT
    
    @patch('psutil.virtual_memory')
    @patch('os.cpu_count')
    def test_sentence_transformers_powerful_hardware(self, mock_cpu, mock_memory):
        """Test sentence-transformers on powerful hardware"""
        mock_cpu.return_value = 16
        mock_memory.return_value = MagicMock(total=32 * 1024**3)  # 32GB
        
        result = estimate_processing_time("sentence-transformers", 1000, 1000)
        
        assert result["estimated_seconds"] > 0
        assert result["estimated_seconds"] < 1000  # Should be faster
    
    @patch('psutil.virtual_memory')
    @patch('os.cpu_count')
    def test_sentence_transformers_basic_hardware(self, mock_cpu, mock_memory):
        """Test sentence-transformers on basic hardware"""
        mock_cpu.return_value = 2
        mock_memory.return_value = MagicMock(total=4 * 1024**3)  # 4GB
        
        result = estimate_processing_time("sentence-transformers", 1000, 1000)
        
        assert result["estimated_seconds"] > 0
    
    def test_large_document_adjustment(self):
        """Test time adjustment for large documents"""
        result_small = estimate_processing_time("sentence-transformers", 100, 1000)
        result_large = estimate_processing_time("sentence-transformers", 100, 8000)
        
        # Large documents should take more time
        assert result_large["estimated_seconds"] >= result_small["estimated_seconds"]
    
    def test_very_large_document_adjustment(self):
        """Test time adjustment for very large documents"""
        result = estimate_processing_time("sentence-transformers", 100, 12000)
        
        # Should have significant time increase
        assert result["estimated_seconds"] > 0
    
    def test_time_format_seconds(self):
        """Test time format for short durations (seconds)"""
        result = estimate_processing_time("openai", 10, 1000)
        
        assert "seconds" in result["estimated_time_str"]
    
    def test_time_format_minutes(self):
        """Test time format for medium durations (minutes)"""
        result = estimate_processing_time("openai", 100, 1000)
        
        # Should be formatted as minutes
        if result["estimated_seconds"] >= 60:
            assert "minute" in result["estimated_time_str"]
    
    def test_time_format_hours(self):
        """Test time format for long durations (hours)"""
        result = estimate_processing_time("openai", 5000, 1000)
        
        # Should be formatted as hours
        if result["estimated_seconds"] >= 3600:
            assert "hour" in result["estimated_time_str"]
    
    def test_unknown_provider_estimate(self):
        """Test time estimate for unknown provider"""
        result = estimate_processing_time("custom-provider", 1000, 1000)
        
        assert result["estimated_seconds"] > 0
        assert result["provider"] == "custom-provider"
    
    def test_zero_documents(self):
        """Test with zero documents"""
        result = estimate_processing_time("openai", 0, 1000)
        
        assert result["estimated_seconds"] == 0
        assert "0 seconds" in result["estimated_time_str"]
    
    def test_single_document(self):
        """Test with single document"""
        result = estimate_processing_time("sentence-transformers", 1, 1000)
        
        assert result["estimated_seconds"] > 0
        assert result["total_documents"] == 1


class TestOptimizationScenarios:
    """Integration-like tests for optimization scenarios"""
    
    @patch('psutil.virtual_memory')
    @patch('os.cpu_count')
    def test_full_optimization_pipeline_openai(self, mock_cpu, mock_memory):
        """Test complete optimization pipeline for OpenAI"""
        mock_cpu.return_value = 8
        mock_memory.return_value = MagicMock(total=16 * 1024**3)
        
        total_docs = 5000
        avg_size = 2000
        
        # Get config
        batch_size, max_workers = get_optimal_config("openai", total_docs)
        
        # Get strategy
        strategy = get_processing_strategy("openai")
        
        # Get time estimate
        time_info = estimate_processing_time("openai", total_docs, avg_size)
        
        # Verify reasonable configuration
        assert batch_size > 0
        assert max_workers > 0
        assert strategy["rate_limiting"] is True
        assert time_info["estimated_seconds"] > 0
    
    @patch('psutil.virtual_memory')
    @patch('os.cpu_count')
    def test_full_optimization_pipeline_local(self, mock_cpu, mock_memory):
        """Test complete optimization pipeline for local embeddings"""
        mock_cpu.return_value = 16
        mock_memory.return_value = MagicMock(total=32 * 1024**3)
        
        total_docs = 10000
        avg_size = 1500
        
        # Get config
        batch_size, max_workers = get_optimal_config("sentence-transformers", total_docs)
        
        # Get strategy
        strategy = get_processing_strategy("sentence-transformers")
        
        # Get time estimate
        time_info = estimate_processing_time("sentence-transformers", total_docs, avg_size)
        
        # Verify aggressive optimization for local
        assert batch_size >= 200
        assert max_workers >= 4
        assert strategy["rate_limiting"] is False
        assert time_info["estimated_seconds"] < total_docs  # Should be fast
