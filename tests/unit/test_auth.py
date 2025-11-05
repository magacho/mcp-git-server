"""
Tests for auth.py - Authentication system
"""
import os
import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
from auth import verify_api_key, is_auth_enabled


class TestVerifyApiKey:
    """Tests for verify_api_key function"""
    
    @pytest.mark.asyncio
    async def test_no_api_key_configured(self):
        """Test when API_KEY is not configured - should allow access"""
        with patch.dict(os.environ, {}, clear=True):
            result = await verify_api_key(None)
            assert result is None
    
    @pytest.mark.asyncio
    async def test_valid_api_key(self):
        """Test with valid API key"""
        test_key = "test_api_key_123"
        with patch.dict(os.environ, {"API_KEY": test_key}):
            result = await verify_api_key(test_key)
            assert result == test_key
    
    @pytest.mark.asyncio
    async def test_missing_api_key_when_required(self):
        """Test missing API key when authentication is enabled"""
        with patch.dict(os.environ, {"API_KEY": "test_key"}):
            with pytest.raises(HTTPException) as exc_info:
                await verify_api_key(None)
            assert exc_info.value.status_code == 403
            assert "Missing API key" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_invalid_api_key(self):
        """Test with invalid API key"""
        with patch.dict(os.environ, {"API_KEY": "correct_key"}):
            with pytest.raises(HTTPException) as exc_info:
                await verify_api_key("wrong_key")
            assert exc_info.value.status_code == 403
            assert "Invalid API key" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_empty_api_key_when_required(self):
        """Test with empty string API key when authentication is enabled"""
        with patch.dict(os.environ, {"API_KEY": "test_key"}):
            with pytest.raises(HTTPException) as exc_info:
                await verify_api_key("")
            assert exc_info.value.status_code == 403
    
    @pytest.mark.asyncio
    async def test_api_key_with_special_characters(self):
        """Test API key with special characters"""
        special_key = "test-key_123!@#"
        with patch.dict(os.environ, {"API_KEY": special_key}):
            result = await verify_api_key(special_key)
            assert result == special_key
    
    @pytest.mark.asyncio
    async def test_api_key_case_sensitive(self):
        """Test that API key comparison is case-sensitive"""
        with patch.dict(os.environ, {"API_KEY": "TestKey"}):
            with pytest.raises(HTTPException) as exc_info:
                await verify_api_key("testkey")
            assert exc_info.value.status_code == 403


class TestIsAuthEnabled:
    """Tests for is_auth_enabled function"""
    
    def test_auth_enabled_when_api_key_set(self):
        """Test returns True when API_KEY is set"""
        with patch.dict(os.environ, {"API_KEY": "test_key"}):
            assert is_auth_enabled() is True
    
    def test_auth_disabled_when_api_key_not_set(self):
        """Test returns False when API_KEY is not set"""
        with patch.dict(os.environ, {}, clear=True):
            assert is_auth_enabled() is False
    
    def test_auth_disabled_with_empty_api_key(self):
        """Test returns False when API_KEY is empty string"""
        with patch.dict(os.environ, {"API_KEY": ""}):
            assert is_auth_enabled() is False
    
    def test_auth_enabled_with_any_value(self):
        """Test returns True with any non-empty API_KEY value"""
        with patch.dict(os.environ, {"API_KEY": "any_value"}):
            assert is_auth_enabled() is True


class TestAuthenticationScenarios:
    """Integration-like tests for common authentication scenarios"""
    
    @pytest.mark.asyncio
    async def test_development_mode_no_auth(self):
        """Test development mode without authentication"""
        with patch.dict(os.environ, {}, clear=True):
            # Should work without providing key
            result = await verify_api_key(None)
            assert result is None
            assert is_auth_enabled() is False
    
    @pytest.mark.asyncio
    async def test_production_mode_with_auth(self):
        """Test production mode with authentication"""
        prod_key = "prod_secure_key_789"
        with patch.dict(os.environ, {"API_KEY": prod_key}):
            # Should require the key
            assert is_auth_enabled() is True
            
            # Valid key should work
            result = await verify_api_key(prod_key)
            assert result == prod_key
            
            # Invalid key should fail
            with pytest.raises(HTTPException):
                await verify_api_key("invalid")
    
    @pytest.mark.asyncio
    async def test_long_api_key(self):
        """Test with very long API key"""
        long_key = "x" * 500
        with patch.dict(os.environ, {"API_KEY": long_key}):
            result = await verify_api_key(long_key)
            assert result == long_key
