"""
Additional tests for repo_utils.py to increase coverage
"""
import os
import pytest
from unittest.mock import patch, MagicMock, call
from repo_utils import (
    detect_git_provider,
    get_git_credentials,
    clone_repo
)


class TestDetectGitProvider:
    """Tests for detect_git_provider function"""
    
    def test_detect_github(self):
        """Test detecting GitHub URLs"""
        assert detect_git_provider("https://github.com/user/repo.git") == "github"
        assert detect_git_provider("git@github.com:user/repo.git") == "github"
        assert detect_git_provider("HTTPS://GITHUB.COM/user/repo.git") == "github"
    
    def test_detect_bitbucket(self):
        """Test detecting Bitbucket URLs"""
        assert detect_git_provider("https://bitbucket.org/user/repo.git") == "bitbucket"
        assert detect_git_provider("git@bitbucket.org:user/repo.git") == "bitbucket"
        assert detect_git_provider("HTTPS://BITBUCKET.ORG/user/repo.git") == "bitbucket"
    
    def test_detect_gitlab(self):
        """Test detecting GitLab URLs"""
        assert detect_git_provider("https://gitlab.com/user/repo.git") == "gitlab"
        assert detect_git_provider("https://gitlab.example.com/user/repo.git") == "gitlab"
        assert detect_git_provider("git@gitlab.com:user/repo.git") == "gitlab"
    
    def test_detect_unknown(self):
        """Test detecting unknown providers"""
        assert detect_git_provider("https://example.com/user/repo.git") == "unknown"
        assert detect_git_provider("git@example.com:user/repo.git") == "unknown"


class TestGetGitCredentials:
    """Tests for get_git_credentials function"""
    
    def test_github_credentials_with_url(self):
        """Test getting GitHub credentials with URL"""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_test123"}):
            token, username = get_git_credentials("https://github.com/user/repo.git")
            assert token == "ghp_test123"
            assert username is None
    
    def test_bitbucket_credentials_with_url(self):
        """Test getting Bitbucket credentials with URL"""
        with patch.dict(os.environ, {
            "BITBUCKET_USERNAME": "testuser",
            "BITBUCKET_APP_PASSWORD": "app_pass123"
        }):
            token, username = get_git_credentials("https://bitbucket.org/user/repo.git")
            assert token == "app_pass123"
            assert username == "testuser"
    
    def test_gitlab_credentials_with_url(self):
        """Test getting GitLab credentials with URL"""
        with patch.dict(os.environ, {"GITLAB_TOKEN": "glpat_test123"}):
            token, username = get_git_credentials("https://gitlab.com/user/repo.git")
            assert token == "glpat_test123"
            assert username is None
    
    def test_fallback_to_github_token(self):
        """Test fallback to GitHub token without URL"""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_fallback"}):
            token, username = get_git_credentials(None)
            assert token == "ghp_fallback"
            assert username is None
    
    def test_fallback_to_bitbucket(self):
        """Test fallback to Bitbucket credentials"""
        with patch.dict(os.environ, {
            "BITBUCKET_USERNAME": "user",
            "BITBUCKET_APP_PASSWORD": "pass"
        }):
            token, username = get_git_credentials(None)
            assert token == "pass"
            assert username == "user"
    
    def test_fallback_to_gitlab(self):
        """Test fallback to GitLab token"""
        with patch.dict(os.environ, {"GITLAB_TOKEN": "glpat_fallback"}):
            token, username = get_git_credentials(None)
            assert token == "glpat_fallback"
            assert username is None
    
    def test_generic_git_credentials(self):
        """Test generic Git credentials"""
        with patch.dict(os.environ, {
            "GIT_TOKEN": "generic_token",
            "GIT_USERNAME": "generic_user"
        }):
            token, username = get_git_credentials(None)
            assert token == "generic_token"
            assert username == "generic_user"
    
    def test_generic_token_without_username(self):
        """Test generic token without username"""
        with patch.dict(os.environ, {"GIT_TOKEN": "generic_token"}):
            token, username = get_git_credentials(None)
            assert token == "generic_token"
            assert username is None
    
    def test_no_credentials(self):
        """Test when no credentials are available"""
        with patch.dict(os.environ, {}, clear=True):
            token, username = get_git_credentials(None)
            assert token is None
            assert username is None
    
    def test_incomplete_bitbucket_credentials(self):
        """Test with incomplete Bitbucket credentials"""
        with patch.dict(os.environ, {"BITBUCKET_USERNAME": "user"}):
            token, username = get_git_credentials("https://bitbucket.org/user/repo.git")
            assert token is None
            assert username is None
    
    def test_credential_priority(self):
        """Test credential priority order"""
        with patch.dict(os.environ, {
            "GITHUB_TOKEN": "github_token",
            "BITBUCKET_USERNAME": "bb_user",
            "BITBUCKET_APP_PASSWORD": "bb_pass",
            "GITLAB_TOKEN": "gitlab_token"
        }):
            # Without URL, should prefer GitHub
            token, username = get_git_credentials(None)
            assert token == "github_token"
            
            # With GitHub URL, should get GitHub token
            token, username = get_git_credentials("https://github.com/user/repo.git")
            assert token == "github_token"
            
            # With Bitbucket URL, should get Bitbucket credentials
            token, username = get_git_credentials("https://bitbucket.org/user/repo.git")
            assert token == "bb_pass"
            assert username == "bb_user"


class TestCloneRepo:
    """Tests for clone_repo function"""
    
    @patch('repo_utils.subprocess.Popen')
    @patch('repo_utils.os.path.exists')
    def test_clone_public_repo(self, mock_exists, mock_popen):
        """Test cloning public repository"""
        mock_exists.return_value = False
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stderr = []
        mock_popen.return_value.__enter__ = MagicMock(return_value=mock_process)
        mock_popen.return_value.__exit__ = MagicMock(return_value=False)
        
        with patch.dict(os.environ, {}, clear=True):
            clone_repo(
                "https://github.com/user/repo.git",
                "main",
                "/tmp/repo"
            )
        
        assert mock_popen.called
    
    @patch('repo_utils.subprocess.Popen')
    @patch('repo_utils.os.path.exists')
    def test_clone_with_github_token_param(self, mock_exists, mock_popen):
        """Test cloning with github_token parameter (backward compatibility)"""
        mock_exists.return_value = False
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stderr = []
        mock_popen.return_value.__enter__ = MagicMock(return_value=mock_process)
        mock_popen.return_value.__exit__ = MagicMock(return_value=False)
        
        clone_repo(
            "https://github.com/user/repo.git",
            "main",
            "/tmp/repo",
            github_token="ghp_test123"
        )
        
        # Should use the provided token
        call_args = mock_popen.call_args
        git_command = call_args[0][0]
        assert any("ghp_test123" in arg for arg in git_command)
    
    @patch('repo_utils.subprocess.Popen')
    @patch('repo_utils.os.path.exists')
    def test_clone_with_env_token(self, mock_exists, mock_popen):
        """Test cloning with environment token"""
        mock_exists.return_value = False
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stderr = []
        mock_popen.return_value.__enter__ = MagicMock(return_value=mock_process)
        mock_popen.return_value.__exit__ = MagicMock(return_value=False)
        
        with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_env123"}):
            clone_repo(
                "https://github.com/user/repo.git",
                "main",
                "/tmp/repo"
            )
        
        call_args = mock_popen.call_args
        git_command = call_args[0][0]
        assert any("ghp_env123" in arg for arg in git_command)
    
    @patch('repo_utils.os.path.exists')
    def test_skip_clone_if_exists(self, mock_exists):
        """Test that clone is skipped if directory exists"""
        mock_exists.return_value = True
        
        # Should return early without cloning
        clone_repo(
            "https://github.com/user/repo.git",
            "main",
            "/tmp/repo"
        )
        
        # Should only check existence
        assert mock_exists.called
    
    @patch('repo_utils.subprocess.Popen')
    @patch('repo_utils.os.path.exists')
    def test_clone_with_depth(self, mock_exists, mock_popen):
        """Test cloning with specific depth"""
        mock_exists.return_value = False
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stderr = []
        mock_popen.return_value.__enter__ = MagicMock(return_value=mock_process)
        mock_popen.return_value.__exit__ = MagicMock(return_value=False)
        
        clone_repo(
            "https://github.com/user/repo.git",
            "main",
            "/tmp/repo",
            depth=5
        )
        
        call_args = mock_popen.call_args
        git_command = call_args[0][0]
        assert "--depth" in git_command
        assert "5" in git_command
    
    @patch('repo_utils.subprocess.Popen')
    @patch('repo_utils.os.path.exists')
    def test_clone_ssh_url(self, mock_exists, mock_popen):
        """Test cloning SSH URL"""
        mock_exists.return_value = False
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stderr = []
        mock_popen.return_value.__enter__ = MagicMock(return_value=mock_process)
        mock_popen.return_value.__exit__ = MagicMock(return_value=False)
        
        clone_repo(
            "git@github.com:user/repo.git",
            "main",
            "/tmp/repo"
        )
        
        assert mock_popen.called
    
    @patch('repo_utils.subprocess.Popen')
    @patch('repo_utils.os.path.exists')
    def test_clone_failure_github(self, mock_exists, mock_popen):
        """Test handling clone failure for GitHub"""
        mock_exists.return_value = False
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stderr = []
        mock_popen.return_value.__enter__ = MagicMock(return_value=mock_process)
        mock_popen.return_value.__exit__ = MagicMock(return_value=False)
        
        with pytest.raises(Exception) as exc_info:
            clone_repo(
                "https://github.com/user/repo.git",
                "main",
                "/tmp/repo"
            )
        
        assert "Failed to clone" in str(exc_info.value)
        assert "GITHUB" in str(exc_info.value)
    
    @patch('repo_utils.subprocess.Popen')
    @patch('repo_utils.os.path.exists')
    def test_clone_failure_bitbucket(self, mock_exists, mock_popen):
        """Test handling clone failure for Bitbucket"""
        mock_exists.return_value = False
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stderr = []
        mock_popen.return_value.__enter__ = MagicMock(return_value=mock_process)
        mock_popen.return_value.__exit__ = MagicMock(return_value=False)
        
        with pytest.raises(Exception) as exc_info:
            clone_repo(
                "https://bitbucket.org/user/repo.git",
                "main",
                "/tmp/repo"
            )
        
        assert "Failed to clone" in str(exc_info.value)
        assert "BITBUCKET" in str(exc_info.value)
        assert "app password" in str(exc_info.value).lower()
    
    @patch('repo_utils.subprocess.Popen')
    @patch('repo_utils.os.path.exists')
    def test_clone_failure_gitlab(self, mock_exists, mock_popen):
        """Test handling clone failure for GitLab"""
        mock_exists.return_value = False
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stderr = []
        mock_popen.return_value.__enter__ = MagicMock(return_value=mock_process)
        mock_popen.return_value.__exit__ = MagicMock(return_value=False)
        
        with pytest.raises(Exception) as exc_info:
            clone_repo(
                "https://gitlab.com/user/repo.git",
                "main",
                "/tmp/repo"
            )
        
        assert "Failed to clone" in str(exc_info.value)
        assert "GITLAB" in str(exc_info.value)
    
    @patch('repo_utils.subprocess.Popen')
    @patch('repo_utils.os.path.exists')
    def test_clone_failure_unknown_provider(self, mock_exists, mock_popen):
        """Test handling clone failure for unknown provider"""
        mock_exists.return_value = False
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stderr = []
        mock_popen.return_value.__enter__ = MagicMock(return_value=mock_process)
        mock_popen.return_value.__exit__ = MagicMock(return_value=False)
        
        with pytest.raises(Exception) as exc_info:
            clone_repo(
                "https://custom.git.com/user/repo.git",
                "main",
                "/tmp/repo"
            )
        
        assert "Failed to clone" in str(exc_info.value)
    
    @patch('repo_utils.subprocess.Popen')
    @patch('repo_utils.os.path.exists')
    def test_clone_git_not_found(self, mock_exists, mock_popen):
        """Test handling when git command is not found"""
        mock_exists.return_value = False
        mock_popen.side_effect = FileNotFoundError("git not found")
        
        with pytest.raises(Exception):
            clone_repo(
                "https://github.com/user/repo.git",
                "main",
                "/tmp/repo"
            )
    
    @patch('repo_utils.subprocess.Popen')
    @patch('repo_utils.os.path.exists')
    def test_clone_with_bitbucket_credentials(self, mock_exists, mock_popen):
        """Test cloning Bitbucket with credentials"""
        mock_exists.return_value = False
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stderr = []
        mock_popen.return_value.__enter__ = MagicMock(return_value=mock_process)
        mock_popen.return_value.__exit__ = MagicMock(return_value=False)
        
        with patch.dict(os.environ, {
            "BITBUCKET_USERNAME": "testuser",
            "BITBUCKET_APP_PASSWORD": "testpass"
        }):
            clone_repo(
                "https://bitbucket.org/user/repo.git",
                "main",
                "/tmp/repo"
            )
        
        call_args = mock_popen.call_args
        git_command = call_args[0][0]
        # Should contain authentication
        assert any("testuser" in arg and "testpass" in arg for arg in git_command)
    
    @patch('repo_utils.subprocess.Popen')
    @patch('repo_utils.os.path.exists')
    def test_clone_stderr_output(self, mock_exists, mock_popen):
        """Test that stderr output is processed"""
        mock_exists.return_value = False
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stderr = ["Cloning into...\n", "Done\n"]
        mock_popen.return_value.__enter__ = MagicMock(return_value=mock_process)
        mock_popen.return_value.__exit__ = MagicMock(return_value=False)
        
        clone_repo(
            "https://github.com/user/repo.git",
            "main",
            "/tmp/repo"
        )
        
        # Should process stderr lines
        assert mock_process.wait.called
