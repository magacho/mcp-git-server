"""
Tests for Bitbucket repository support
"""
import pytest
from unittest.mock import patch, MagicMock
from repo_utils import (
    detect_git_provider,
    inject_token_in_url,
    get_git_credentials,
    get_authenticated_url,
    clone_repo
)


class TestGitProviderDetection:
    """Test Git provider detection"""
    
    def test_detect_github(self):
        """Test GitHub URL detection"""
        assert detect_git_provider("https://github.com/user/repo.git") == "github"
        assert detect_git_provider("git@github.com:user/repo.git") == "github"
    
    def test_detect_bitbucket(self):
        """Test Bitbucket URL detection"""
        assert detect_git_provider("https://bitbucket.org/workspace/repo.git") == "bitbucket"
        assert detect_git_provider("git@bitbucket.org:workspace/repo.git") == "bitbucket"
    
    def test_detect_gitlab(self):
        """Test GitLab URL detection"""
        assert detect_git_provider("https://gitlab.com/user/repo.git") == "gitlab"
        assert detect_git_provider("git@gitlab.com:user/repo.git") == "gitlab"
    
    def test_detect_unknown(self):
        """Test unknown provider detection"""
        assert detect_git_provider("https://example.com/repo.git") == "unknown"


class TestTokenInjection:
    """Test token injection into URLs"""
    
    def test_github_token_injection(self):
        """Test GitHub token injection (token as username)"""
        url = "https://github.com/user/repo.git"
        token = "ghp_test123"
        result = inject_token_in_url(url, token)
        assert result == "https://ghp_test123@github.com/user/repo.git"
    
    def test_bitbucket_token_injection(self):
        """Test Bitbucket token injection (username:password format)"""
        url = "https://bitbucket.org/workspace/repo.git"
        token = "app_password"
        username = "myuser"
        result = inject_token_in_url(url, token, username)
        assert result == "https://myuser:app_password@bitbucket.org/workspace/repo.git"
    
    def test_gitlab_token_injection(self):
        """Test GitLab token injection (token as username)"""
        url = "https://gitlab.com/user/repo.git"
        token = "glpat_test123"
        result = inject_token_in_url(url, token)
        assert result == "https://glpat_test123@gitlab.com/user/repo.git"
    
    def test_ssh_url_unchanged(self):
        """Test SSH URLs pass through unchanged"""
        ssh_url = "git@github.com:user/repo.git"
        result = inject_token_in_url(ssh_url, "token123")
        assert result == ssh_url


class TestGetGitCredentials:
    """Test credential retrieval from environment"""
    
    @patch.dict('os.environ', {'GITHUB_TOKEN': 'ghp_test'})
    def test_get_github_token(self):
        """Test GitHub token retrieval"""
        token, username = get_git_credentials()
        assert token == "ghp_test"
        assert username is None
    
    @patch.dict('os.environ', {
        'BITBUCKET_USERNAME': 'testuser',
        'BITBUCKET_APP_PASSWORD': 'testpass'
    })
    def test_get_bitbucket_credentials(self):
        """Test Bitbucket credentials retrieval"""
        token, username = get_git_credentials()
        assert token == "testpass"
        assert username == "testuser"
    
    @patch.dict('os.environ', {'GITLAB_TOKEN': 'glpat_test'})
    def test_get_gitlab_token(self):
        """Test GitLab token retrieval"""
        token, username = get_git_credentials()
        assert token == "glpat_test"
        assert username is None
    
    @patch.dict('os.environ', {
        'GIT_TOKEN': 'generic_token',
        'GIT_USERNAME': 'generic_user'
    })
    def test_get_generic_credentials(self):
        """Test generic Git credentials retrieval"""
        token, username = get_git_credentials()
        assert token == "generic_token"
        assert username == "generic_user"
    
    @patch.dict('os.environ', {}, clear=True)
    def test_no_credentials(self):
        """Test when no credentials are set"""
        token, username = get_git_credentials()
        assert token is None
        assert username is None


class TestGetAuthenticatedUrl:
    """Test authenticated URL generation"""
    
    @patch.dict('os.environ', {'GITHUB_TOKEN': 'ghp_test'})
    def test_github_authenticated_url(self):
        """Test GitHub authenticated URL"""
        url = "https://github.com/user/repo.git"
        result = get_authenticated_url(url)
        assert result == "https://ghp_test@github.com/user/repo.git"
    
    @patch.dict('os.environ', {
        'BITBUCKET_USERNAME': 'user',
        'BITBUCKET_APP_PASSWORD': 'pass'
    })
    def test_bitbucket_authenticated_url(self):
        """Test Bitbucket authenticated URL"""
        url = "https://bitbucket.org/workspace/repo.git"
        result = get_authenticated_url(url)
        assert result == "https://user:pass@bitbucket.org/workspace/repo.git"
    
    @patch.dict('os.environ', {}, clear=True)
    def test_public_repo_url(self):
        """Test public repository URL (no auth)"""
        url = "https://github.com/user/public-repo.git"
        result = get_authenticated_url(url)
        assert result == url
    
    def test_ssh_url_unchanged(self):
        """Test SSH URL passes through unchanged"""
        ssh_url = "git@bitbucket.org:workspace/repo.git"
        result = get_authenticated_url(ssh_url)
        assert result == ssh_url
    
    def test_explicit_credentials(self):
        """Test explicit credentials override environment"""
        url = "https://github.com/user/repo.git"
        result = get_authenticated_url(url, token="explicit_token")
        assert result == "https://explicit_token@github.com/user/repo.git"
    
    def test_bitbucket_explicit_credentials(self):
        """Test Bitbucket with explicit credentials"""
        url = "https://bitbucket.org/workspace/repo.git"
        result = get_authenticated_url(url, token="mypass", username="myuser")
        assert result == "https://myuser:mypass@bitbucket.org/workspace/repo.git"


class TestCloneRepo:
    """Test repository cloning with different providers"""
    
    @patch('repo_utils.subprocess.Popen')
    @patch('repo_utils.os.path.exists', return_value=False)
    def test_clone_public_github_repo(self, mock_exists, mock_popen):
        """Test cloning public GitHub repository"""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stderr = []
        mock_popen.return_value.__enter__.return_value = mock_process
        
        clone_repo(
            "https://github.com/user/repo.git",
            "main",
            "./test_repo"
        )
        
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        assert "git" in call_args
        assert "clone" in call_args
        assert "https://github.com/user/repo.git" in call_args
    
    @patch('repo_utils.subprocess.Popen')
    @patch('repo_utils.os.path.exists', return_value=False)
    @patch.dict('os.environ', {
        'BITBUCKET_USERNAME': 'testuser',
        'BITBUCKET_APP_PASSWORD': 'testpass'
    })
    def test_clone_private_bitbucket_repo(self, mock_exists, mock_popen):
        """Test cloning private Bitbucket repository"""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stderr = []
        mock_popen.return_value.__enter__.return_value = mock_process
        
        clone_repo(
            "https://bitbucket.org/workspace/repo.git",
            "main",
            "./test_repo"
        )
        
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        assert "git" in call_args
        assert "clone" in call_args
        # Check authenticated URL is used
        assert any("bitbucket.org" in arg for arg in call_args)
    
    @patch('repo_utils.os.path.exists', return_value=True)
    def test_clone_skips_existing_directory(self, mock_exists):
        """Test clone skips if directory already exists"""
        # Should not raise exception, just skip
        clone_repo(
            "https://github.com/user/repo.git",
            "main",
            "./existing_repo"
        )
        # No assertion needed - just verify it doesn't crash
    
    @patch('repo_utils.subprocess.Popen')
    @patch('repo_utils.os.path.exists', return_value=False)
    def test_clone_failure_shows_provider_specific_help(self, mock_exists, mock_popen):
        """Test clone failure shows provider-specific help"""
        mock_process = MagicMock()
        mock_process.returncode = 128  # Git error
        mock_process.stderr = []
        mock_popen.return_value.__enter__.return_value = mock_process
        
        with pytest.raises(Exception) as exc_info:
            clone_repo(
                "https://bitbucket.org/workspace/repo.git",
                "main",
                "./test_repo"
            )
        
        error_msg = str(exc_info.value)
        assert "BITBUCKET" in error_msg.upper()
        assert "BITBUCKET_USERNAME" in error_msg
        assert "BITBUCKET_APP_PASSWORD" in error_msg
        assert "app password" in error_msg.lower()


class TestIntegrationScenarios:
    """Test real-world integration scenarios"""
    
    @patch.dict('os.environ', {
        'GITHUB_TOKEN': 'ghp_github',
        'BITBUCKET_USERNAME': 'bbuser',
        'BITBUCKET_APP_PASSWORD': 'bbpass',
        'GITLAB_TOKEN': 'glpat_gitlab'
    })
    def test_multi_provider_credentials(self):
        """Test handling multiple provider credentials"""
        # GitHub should use GITHUB_TOKEN
        github_url = get_authenticated_url("https://github.com/user/repo.git")
        assert "ghp_github" in github_url
        
        # Bitbucket should use username:password
        bitbucket_url = get_authenticated_url("https://bitbucket.org/workspace/repo.git")
        assert "bbuser" in bitbucket_url
        assert "bbpass" in bitbucket_url
        
        # GitLab should use GITLAB_TOKEN
        gitlab_url = get_authenticated_url("https://gitlab.com/user/repo.git")
        assert "glpat_gitlab" in gitlab_url
    
    def test_credential_priority(self):
        """Test that explicit credentials override environment"""
        with patch.dict('os.environ', {'GITHUB_TOKEN': 'env_token'}):
            url = get_authenticated_url(
                "https://github.com/user/repo.git",
                token="explicit_token"
            )
            assert "explicit_token" in url
            assert "env_token" not in url


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
