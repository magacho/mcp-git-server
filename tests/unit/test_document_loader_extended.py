"""
Additional tests for document_loader.py to increase coverage
"""
import os
import pytest
import tempfile
import json
from unittest.mock import patch, MagicMock, mock_open
from collections import defaultdict
from document_loader import (
    process_file,
    load_documents_robustly,
    EXTENSOES_SUPORTADAS,
    SPECIAL_FILES
)


class TestProcessFile:
    """Tests for process_file function"""
    
    def test_process_json_file_with_jsonloader(self):
        """Test processing JSON file with JSONLoader"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"key": "value", "number": 42}, f)
            f.flush()
            temp_path = f.name
        
        try:
            ext, docs, error = process_file(temp_path, ".json")
            
            assert ext == ".json"
            assert len(docs) > 0
            assert error is None
        finally:
            os.unlink(temp_path)
    
    def test_process_json_file_fallback(self):
        """Test JSON file processing with fallback"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"data": "test", "items": [1, 2, 3]}, f)
            f.flush()
            temp_path = f.name
        
        try:
            # Mock JSONLoader to fail, forcing fallback
            with patch('document_loader.JSONLoader') as mock_loader:
                mock_loader.side_effect = Exception("JSONLoader failed")
                
                ext, docs, error = process_file(temp_path, ".json")
                
                assert ext == ".json"
                assert len(docs) == 1
                assert error is None
                assert docs[0].metadata["type"] == "json"
        finally:
            os.unlink(temp_path)
    
    def test_process_invalid_json_file(self):
        """Test processing invalid JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            f.flush()
            temp_path = f.name
        
        try:
            with patch('document_loader.JSONLoader') as mock_loader:
                mock_loader.side_effect = Exception("Invalid JSON")
                
                ext, docs, error = process_file(temp_path, ".json")
                
                assert ext == ".json"
                assert len(docs) == 1
                assert error is None
                assert docs[0].metadata["type"] == "json_text"
        finally:
            os.unlink(temp_path)
    
    def test_process_pdf_file(self):
        """Test processing PDF file"""
        with patch('document_loader.PyPDFLoader') as mock_loader:
            mock_doc = MagicMock()
            mock_doc.page_content = "PDF content"
            mock_loader.return_value.lazy_load.return_value = [mock_doc]
            
            ext, docs, error = process_file("/path/to/file.pdf", ".pdf")
            
            assert ext == ".pdf"
            assert len(docs) == 1
            assert error is None
    
    def test_process_text_file(self):
        """Test processing text file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is test content")
            f.flush()
            temp_path = f.name
        
        try:
            ext, docs, error = process_file(temp_path, ".txt")
            
            assert ext == ".txt"
            assert len(docs) == 1
            assert error is None
            assert docs[0].page_content == "This is test content"
            assert docs[0].metadata["source"] == temp_path
        finally:
            os.unlink(temp_path)
    
    def test_process_python_file(self):
        """Test processing Python file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("def test():\n    pass")
            f.flush()
            temp_path = f.name
        
        try:
            ext, docs, error = process_file(temp_path, ".py")
            
            assert ext == ".py"
            assert len(docs) == 1
            assert error is None
            assert "def test()" in docs[0].page_content
        finally:
            os.unlink(temp_path)
    
    def test_process_file_error_handling(self):
        """Test error handling in process_file"""
        ext, docs, error = process_file("/nonexistent/file.txt", ".txt")
        
        assert ext == ".txt"
        assert len(docs) == 0
        assert error is not None
        assert "AVISO" in error
    
    def test_process_markdown_file(self):
        """Test processing Markdown file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Heading\n\nContent")
            f.flush()
            temp_path = f.name
        
        try:
            ext, docs, error = process_file(temp_path, ".md")
            
            assert ext == ".md"
            assert len(docs) == 1
            assert "Heading" in docs[0].page_content
        finally:
            os.unlink(temp_path)


class TestLoadDocumentsRobustly:
    """Tests for load_documents_robustly function"""
    
    def test_load_supported_files(self):
        """Test loading supported file extensions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            for ext in [".py", ".txt", ".md"]:
                filepath = os.path.join(tmpdir, f"test{ext}")
                with open(filepath, 'w') as f:
                    f.write(f"Content for {ext}")
            
            processed = defaultdict(int)
            discarded = defaultdict(int)
            
            docs = list(load_documents_robustly(tmpdir, processed, discarded))
            
            assert len(docs) == 3
            assert processed[".py"] == 1
            assert processed[".txt"] == 1
            assert processed[".md"] == 1
    
    def test_discard_unsupported_files(self):
        """Test that unsupported files are discarded"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create unsupported file
            filepath = os.path.join(tmpdir, "test.xyz")
            with open(filepath, 'w') as f:
                f.write("Unsupported content")
            
            processed = defaultdict(int)
            discarded = defaultdict(int)
            
            docs = list(load_documents_robustly(tmpdir, processed, discarded))
            
            assert len(docs) == 0
            assert discarded[".xyz"] == 1
    
    def test_load_special_files(self):
        """Test loading special files without extension"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create README file
            filepath = os.path.join(tmpdir, "README")
            with open(filepath, 'w') as f:
                f.write("This is README content")
            
            processed = defaultdict(int)
            discarded = defaultdict(int)
            
            docs = list(load_documents_robustly(tmpdir, processed, discarded))
            
            assert len(docs) == 1
            assert processed[""] >= 1
    
    def test_skip_too_large_files(self):
        """Test that files larger than 5MB are skipped"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "large.txt")
            
            # Mock getsize to return large size
            with patch('os.path.getsize') as mock_size:
                mock_size.return_value = 6 * 1024 * 1024  # 6MB
                
                with open(filepath, 'w') as f:
                    f.write("Content")
                
                processed = defaultdict(int)
                discarded = defaultdict(int)
                
                docs = list(load_documents_robustly(tmpdir, processed, discarded))
                
                assert discarded[".txt_too_large"] >= 1
    
    def test_skip_too_small_files(self):
        """Test that files smaller than 10 bytes are skipped"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "tiny.txt")
            
            with open(filepath, 'w') as f:
                f.write("x")  # 1 byte
            
            processed = defaultdict(int)
            discarded = defaultdict(int)
            
            docs = list(load_documents_robustly(tmpdir, processed, discarded))
            
            assert discarded[".txt_too_small"] >= 1
    
    def test_skip_special_file_too_large(self):
        """Test that special files larger than 10MB are skipped"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "README")
            
            with patch('os.path.getsize') as mock_size:
                mock_size.return_value = 11 * 1024 * 1024  # 11MB
                
                with open(filepath, 'w') as f:
                    f.write("Content")
                
                processed = defaultdict(int)
                discarded = defaultdict(int)
                
                docs = list(load_documents_robustly(tmpdir, processed, discarded))
                
                assert discarded["_too_large"] >= 1
    
    def test_handle_oserror_gracefully(self):
        """Test handling of OSError during file processing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.txt")
            
            with open(filepath, 'w') as f:
                f.write("Content")
            
            # Mock getsize to raise OSError
            with patch('os.path.getsize') as mock_size:
                mock_size.side_effect = OSError("Permission denied")
                
                processed = defaultdict(int)
                discarded = defaultdict(int)
                
                # Should not crash
                docs = list(load_documents_robustly(tmpdir, processed, discarded))
                
                # No documents should be processed
                assert len(docs) == 0
    
    def test_custom_max_workers(self):
        """Test with custom max_workers parameter"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.txt")
            with open(filepath, 'w') as f:
                f.write("Content for testing")
            
            processed = defaultdict(int)
            discarded = defaultdict(int)
            
            docs = list(load_documents_robustly(
                tmpdir, 
                processed, 
                discarded, 
                max_load_workers=2
            ))
            
            assert len(docs) == 1
    
    def test_default_max_workers(self):
        """Test default max_workers calculation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.txt")
            with open(filepath, 'w') as f:
                f.write("Content with enough text to pass minimum size")
            
            processed = defaultdict(int)
            discarded = defaultdict(int)
            
            with patch('os.cpu_count') as mock_cpu:
                mock_cpu.return_value = 4
                
                docs = list(load_documents_robustly(
                    tmpdir, 
                    processed, 
                    discarded
                ))
                
                assert len(docs) == 1
    
    def test_cpu_count_none(self):
        """Test when cpu_count returns None"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.txt")
            with open(filepath, 'w') as f:
                f.write("Content with enough text to pass minimum size")
            
            processed = defaultdict(int)
            discarded = defaultdict(int)
            
            with patch('os.cpu_count') as mock_cpu:
                mock_cpu.return_value = None
                
                docs = list(load_documents_robustly(
                    tmpdir, 
                    processed, 
                    discarded
                ))
                
                assert len(docs) == 1
    
    def test_nested_directories(self):
        """Test loading files from nested directories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested structure
            subdir = os.path.join(tmpdir, "subdir")
            os.makedirs(subdir)
            
            with open(os.path.join(tmpdir, "root.txt"), 'w') as f:
                f.write("Root content")
            
            with open(os.path.join(subdir, "nested.txt"), 'w') as f:
                f.write("Nested content")
            
            processed = defaultdict(int)
            discarded = defaultdict(int)
            
            docs = list(load_documents_robustly(tmpdir, processed, discarded))
            
            assert len(docs) == 2
            assert processed[".txt"] == 2
    
    def test_multiple_file_types(self):
        """Test loading multiple different file types"""
        with tempfile.TemporaryDirectory() as tmpdir:
            files = {
                "test.py": "print('hello world')",
                "test.js": "console.log('hello world')",
                "test.md": "# Title\n\nContent here",
                "test.json": '{"key": "value", "data": "test"}',
                "README": "README content with enough text"
            }
            
            for filename, content in files.items():
                with open(os.path.join(tmpdir, filename), 'w') as f:
                    f.write(content)
            
            processed = defaultdict(int)
            discarded = defaultdict(int)
            
            docs = list(load_documents_robustly(tmpdir, processed, discarded))
            
            assert len(docs) == 5


class TestExtensionsAndSpecialFiles:
    """Tests for extension and special file constants"""
    
    def test_supported_extensions_not_empty(self):
        """Test that EXTENSOES_SUPORTADAS is not empty"""
        assert len(EXTENSOES_SUPORTADAS) > 0
    
    def test_special_files_not_empty(self):
        """Test that SPECIAL_FILES is not empty"""
        assert len(SPECIAL_FILES) > 0
    
    def test_common_extensions_included(self):
        """Test that common extensions are included"""
        common = [".py", ".js", ".md", ".json", ".txt"]
        for ext in common:
            assert ext in EXTENSOES_SUPORTADAS
    
    def test_terraform_extensions_included(self):
        """Test that Terraform extensions are included"""
        terraform = [".tf", ".tfvars", ".hcl"]
        for ext in terraform:
            assert ext in EXTENSOES_SUPORTADAS
    
    def test_readme_in_special_files(self):
        """Test that README is in special files"""
        assert "README" in SPECIAL_FILES
    
    def test_license_in_special_files(self):
        """Test that LICENSE is in special files"""
        assert "LICENSE" in SPECIAL_FILES
