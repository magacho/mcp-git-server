"""
Tests for document_loader.py - File extension support
"""
import os
import tempfile
import pytest
from document_loader import EXTENSOES_SUPORTADAS, process_file


class TestSupportedExtensions:
    """Test supported file extensions"""
    
    def test_terraform_extensions_supported(self):
        """Test that Terraform extensions are in supported list"""
        terraform_extensions = [".tf", ".tfvars", ".hcl"]
        
        for ext in terraform_extensions:
            assert ext in EXTENSOES_SUPORTADAS, f"{ext} should be in EXTENSOES_SUPORTADAS"
    
    def test_common_code_extensions_supported(self):
        """Test that common code extensions are supported"""
        common_extensions = [".py", ".js", ".ts", ".go", ".rs", ".java"]
        
        for ext in common_extensions:
            assert ext in EXTENSOES_SUPORTADAS, f"{ext} should be in EXTENSOES_SUPORTADAS"
    
    def test_config_extensions_supported(self):
        """Test that config file extensions are supported"""
        config_extensions = [".yml", ".yaml", ".json", ".xml", ".env"]
        
        for ext in config_extensions:
            assert ext in EXTENSOES_SUPORTADAS, f"{ext} should be in EXTENSOES_SUPORTADAS"


class TestTerraformFileProcessing:
    """Test Terraform file processing"""
    
    def test_process_tf_file(self):
        """Test processing a .tf file"""
        # Create temporary .tf file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tf', delete=False) as f:
            f.write("""
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = "main-vpc"
  }
}
""")
            temp_file = f.name
        
        try:
            ext, docs, error = process_file(temp_file, ".tf")
            
            # Should not have errors
            assert error is None, f"Should not have error: {error}"
            
            # Should return documents
            assert len(docs) > 0, "Should return at least one document"
            
            # Content should be captured
            doc = docs[0]
            content = doc.page_content
            assert "aws_vpc" in content, "Should contain aws_vpc"
            assert "main" in content, "Should contain resource name"
            assert "cidr_block" in content, "Should contain cidr_block"
            
        finally:
            os.unlink(temp_file)
    
    def test_process_tfvars_file(self):
        """Test processing a .tfvars file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tfvars', delete=False) as f:
            f.write("""
region = "us-east-1"
instance_type = "t2.micro"
vpc_cidr = "10.0.0.0/16"
""")
            temp_file = f.name
        
        try:
            ext, docs, error = process_file(temp_file, ".tfvars")
            
            assert error is None
            assert len(docs) > 0
            
            content = docs[0].page_content
            assert "region" in content
            assert "us-east-1" in content
            assert "instance_type" in content
            
        finally:
            os.unlink(temp_file)
    
    def test_process_hcl_file(self):
        """Test processing a .hcl file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.hcl', delete=False) as f:
            f.write("""
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}
""")
            temp_file = f.name
        
        try:
            ext, docs, error = process_file(temp_file, ".hcl")
            
            assert error is None
            assert len(docs) > 0
            
            content = docs[0].page_content
            assert "variable" in content
            assert "environment" in content
            assert "description" in content
            
        finally:
            os.unlink(temp_file)


class TestFileMetadata:
    """Test file metadata handling"""
    
    def test_tf_file_has_source_metadata(self):
        """Test that processed .tf file has source in metadata"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tf', delete=False) as f:
            f.write("resource \"aws_s3_bucket\" \"example\" {}")
            temp_file = f.name
        
        try:
            ext, docs, error = process_file(temp_file, ".tf")
            
            assert error is None
            assert len(docs) > 0
            
            doc = docs[0]
            assert hasattr(doc, 'metadata'), "Document should have metadata"
            assert 'source' in doc.metadata, "Metadata should contain source"
            assert doc.metadata['source'] == temp_file
            
        finally:
            os.unlink(temp_file)


class TestExtensionCount:
    """Test that we have a reasonable number of supported extensions"""
    
    def test_has_infrastructure_extensions(self):
        """Test that infrastructure extensions are present"""
        # Should have at least Terraform extensions
        infrastructure_exts = [".tf", ".tfvars", ".hcl"]
        for ext in infrastructure_exts:
            assert ext in EXTENSOES_SUPORTADAS
    
    def test_has_minimum_extensions(self):
        """Test that we support a reasonable number of file types"""
        # Should have at least 20 different file types
        assert len(EXTENSOES_SUPORTADAS) >= 20, "Should support at least 20 file types"
