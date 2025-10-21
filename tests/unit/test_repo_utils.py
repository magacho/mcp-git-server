"""
Tests for private repository support in repo_utils
"""
import pytest
from repo_utils import (
    get_repo_name_from_url,
    inject_token_in_url,
    get_authenticated_url,
)


class TestGetRepoName:
    def test_https_url(self):
        """Test extracting name from HTTPS URL"""
        url = "https://github.com/user/repo.git"
        assert get_repo_name_from_url(url) == "repo"
    
    def test_ssh_url(self):
        """Test extracting name from SSH URL"""
        url = "git@github.com:user/repo.git"
        assert get_repo_name_from_url(url) == "repo"
    
    def test_url_without_git_extension(self):
        """Test URL without .git extension"""
        url = "https://github.com/user/my-repo"
        assert get_repo_name_from_url(url) == "my-repo"


class TestInjectToken:
    def test_inject_token_https(self):
        """Test injecting token into HTTPS URL"""
        url = "https://github.com/user/repo.git"
        token = "ghp_test123"
        result = inject_token_in_url(url, token)
        assert result == "https://ghp_test123@github.com/user/repo.git"
    
    def test_inject_token_http(self):
        """Test injecting token into HTTP URL"""
        url = "http://github.com/user/repo.git"
        token = "ghp_test123"
        result = inject_token_in_url(url, token)
        assert result == "http://ghp_test123@github.com/user/repo.git"
    
    def test_inject_token_ssh_unchanged(self):
        """Test SSH URL remains unchanged"""
        url = "git@github.com:user/repo.git"
        token = "ghp_test123"
        result = inject_token_in_url(url, token)
        assert result == url
    
    def test_inject_token_with_port(self):
        """Test injecting token with port in URL"""
        url = "https://github.com:443/user/repo.git"
        token = "ghp_test123"
        result = inject_token_in_url(url, token)
        assert result == "https://ghp_test123@github.com:443/user/repo.git"


class TestGetAuthenticatedUrl:
    def test_public_repo_no_token(self):
        """Test public repository without token"""
        url = "https://github.com/user/repo.git"
        result = get_authenticated_url(url)
        assert result == url
    
    def test_public_repo_with_token(self):
        """Test public repository with token (should add auth)"""
        url = "https://github.com/user/repo.git"
        token = "ghp_test123"
        result = get_authenticated_url(url, token)
        assert result == "https://ghp_test123@github.com/user/repo.git"
    
    def test_ssh_url_with_token(self):
        """Test SSH URL with token (should remain unchanged)"""
        url = "git@github.com:user/repo.git"
        token = "ghp_test123"
        result = get_authenticated_url(url, token)
        assert result == url
    
    def test_ssh_protocol_url(self):
        """Test SSH protocol URL"""
        url = "ssh://git@github.com/user/repo.git"
        token = "ghp_test123"
        result = get_authenticated_url(url, token)
        assert result == url
    
    def test_none_token(self):
        """Test with None token"""
        url = "https://github.com/user/repo.git"
        result = get_authenticated_url(url, None)
        assert result == url
    
    def test_empty_token(self):
        """Test with empty string token"""
        url = "https://github.com/user/repo.git"
        result = get_authenticated_url(url, "")
        assert result == url


class TestRepoNameSafety:
    def test_special_characters_replaced(self):
        """Test special characters are replaced"""
        url = "https://github.com/user/my-special@repo#test.git"
        name = get_repo_name_from_url(url)
        # Should replace @ and # with _
        assert "@" not in name
        assert "#" not in name
    
    def test_fallback_on_error(self):
        """Test fallback when URL parsing fails"""
        url = ""
        name = get_repo_name_from_url(url)
        assert name == "default_repo"


class TestPrivateRepoScenarios:
    """Integration-like tests for common scenarios"""
    
    def test_private_repo_https_with_pat(self):
        """Test private repository with PAT via HTTPS"""
        url = "https://github.com/user/private-repo.git"
        token = "ghp_abcdef123456"
        result = get_authenticated_url(url, token)
        assert "ghp_abcdef123456@github.com" in result
        assert "private-repo.git" in result
    
    def test_private_repo_ssh(self):
        """Test private repository via SSH (no token needed)"""
        url = "git@github.com:user/private-repo.git"
        result = get_authenticated_url(url)
        assert result == url
    
    def test_organization_private_repo(self):
        """Test organization private repository"""
        url = "https://github.com/my-org/private-project.git"
        token = "ghp_orgtoken123"
        result = get_authenticated_url(url, token)
        assert "ghp_orgtoken123@github.com" in result
        assert "my-org/private-project.git" in result
