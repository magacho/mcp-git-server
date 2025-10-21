"""
Git repository utilities with support for private repositories
"""
import os
import re
import subprocess
from typing import Optional
from urllib.parse import urlparse, urlunparse


def get_repo_name_from_url(url: str) -> str:
    """
    Extract repository name from URL
    
    Args:
        url: Repository URL
        
    Returns:
        Safe repository name
    """
    try:
        if not url:  # Handle empty URL
            return "default_repo"
        repo_name = url.split('/')[-1]
        repo_name = re.sub(r'\.git$', '', repo_name)
        safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', repo_name)
        return safe_name if safe_name else "default_repo"
    except Exception:
        return "default_repo"


def inject_token_in_url(repo_url: str, token: str) -> str:
    """
    Inject GitHub token into HTTPS URL for authentication
    
    Args:
        repo_url: Original repository URL
        token: GitHub Personal Access Token
        
    Returns:
        URL with embedded token
        
    Example:
        https://github.com/user/repo.git
        -> https://token@github.com/user/repo.git
    """
    parsed = urlparse(repo_url)
    
    # Only inject token for HTTPS URLs
    if parsed.scheme not in ('http', 'https'):
        return repo_url
    
    # Inject token as username
    netloc_with_token = f"{token}@{parsed.netloc}"
    
    # Reconstruct URL
    authenticated_url = urlunparse((
        parsed.scheme,
        netloc_with_token,
        parsed.path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))
    
    return authenticated_url


def get_authenticated_url(repo_url: str, github_token: Optional[str] = None) -> str:
    """
    Get authenticated URL for repository cloning
    
    Supports:
    - Public repositories (no token needed)
    - Private repositories via GitHub PAT (HTTPS)
    - SSH repositories (assumes SSH keys configured)
    
    Args:
        repo_url: Repository URL (HTTPS or SSH)
        github_token: Optional GitHub Personal Access Token
        
    Returns:
        Authenticated URL ready for cloning
    """
    # SSH URLs pass through unchanged (assumes SSH keys are configured)
    if repo_url.startswith('git@') or repo_url.startswith('ssh://'):
        return repo_url
    
    # HTTPS URLs with token
    if github_token and (repo_url.startswith('http://') or repo_url.startswith('https://')):
        return inject_token_in_url(repo_url, github_token)
    
    # Public repository or no auth needed
    return repo_url


def clone_repo(
    repo_url: str, 
    repo_branch: str, 
    local_path: str,
    github_token: Optional[str] = None,
    depth: int = 1
) -> None:
    """
    Clone a Git repository with support for private repositories
    
    Supports:
    - Public repositories (HTTPS, no auth)
    - Private repositories via GitHub PAT (HTTPS)
    - Private repositories via SSH (requires SSH keys configured)
    
    Args:
        repo_url: Repository URL (HTTPS or SSH format)
        repo_branch: Branch to clone
        local_path: Local path to clone into
        github_token: Optional GitHub Personal Access Token for private repos
        depth: Clone depth (1 = shallow clone, 0 = full history)
        
    Raises:
        Exception: If clone fails
        
    Examples:
        # Public repository
        clone_repo("https://github.com/user/repo.git", "main", "./repos/repo")
        
        # Private repository with PAT
        clone_repo(
            "https://github.com/user/private-repo.git",
            "main",
            "./repos/private",
            github_token="ghp_xxxxxxxxxxxx"
        )
        
        # Private repository with SSH
        clone_repo("git@github.com:user/private-repo.git", "main", "./repos/private")
    """
    if os.path.exists(local_path):
        print(f"Repository directory already exists at {local_path}. Skipping clone.")
        return
    
    # Get authenticated URL
    auth_url = get_authenticated_url(repo_url, github_token)
    
    # Determine if URL has embedded credentials (for logging purposes)
    has_credentials = '@' in auth_url and not auth_url.startswith('git@')
    
    # Log safely (hide credentials)
    if has_credentials:
        safe_url = re.sub(r'://[^@]+@', '://***@', auth_url)
        print(f"Cloning from: {safe_url} (Branch: {repo_branch}) [Authenticated]")
    else:
        print(f"Cloning from: {auth_url} (Branch: {repo_branch})")
    
    # Build git command
    git_command = ["git", "clone", "--progress"]
    
    if depth > 0:
        git_command.extend(["--depth", str(depth)])
    
    git_command.extend(["--branch", repo_branch, auth_url, local_path])
    
    # Execute clone
    try:
        with subprocess.Popen(
            git_command, 
            stderr=subprocess.PIPE, 
            text=True, 
            bufsize=1,
            env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'}  # Disable interactive prompts
        ) as process:
            for line in process.stderr:
                # Hide credentials in output
                safe_line = re.sub(r'://[^@]+@', '://***@', line.strip())
                print(f"  [git] {safe_line}")
            
            process.wait()
            
            if process.returncode != 0:
                raise Exception(
                    f"Failed to clone repository. Exit code: {process.returncode}\n"
                    f"Check: 1) URL is correct, 2) Branch exists, "
                    f"3) GitHub token has correct permissions (if private), "
                    f"4) SSH keys are configured (if using SSH)"
                )
    except FileNotFoundError:
        raise Exception(
            "Git is not installed or not found in PATH. "
            "Please install git: https://git-scm.com/downloads"
        )