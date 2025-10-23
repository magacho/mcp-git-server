"""
Git repository utilities with support for private repositories
Supports: GitHub, Bitbucket, GitLab
"""
import os
import re
import subprocess
from typing import Optional, Tuple
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


def detect_git_provider(repo_url: str) -> str:
    """
    Detect Git provider from repository URL
    
    Args:
        repo_url: Repository URL
        
    Returns:
        Provider name: 'github', 'bitbucket', 'gitlab', or 'unknown'
    """
    url_lower = repo_url.lower()
    
    if 'github.com' in url_lower:
        return 'github'
    elif 'bitbucket.org' in url_lower:
        return 'bitbucket'
    elif 'gitlab.com' in url_lower or 'gitlab' in url_lower:
        return 'gitlab'
    else:
        return 'unknown'


def inject_token_in_url(repo_url: str, token: str, username: Optional[str] = None) -> str:
    """
    Inject authentication token into HTTPS URL
    
    Supports:
    - GitHub: token as username (PAT)
    - Bitbucket: username:app_password format
    - GitLab: token as username (PAT)
    
    Args:
        repo_url: Original repository URL
        token: Access token or app password
        username: Username (required for Bitbucket)
        
    Returns:
        URL with embedded credentials
        
    Examples:
        GitHub:
        https://github.com/user/repo.git
        -> https://token@github.com/user/repo.git
        
        Bitbucket:
        https://bitbucket.org/workspace/repo.git
        -> https://username:app_password@bitbucket.org/workspace/repo.git
    """
    parsed = urlparse(repo_url)
    
    # Only inject token for HTTPS URLs
    if parsed.scheme not in ('http', 'https'):
        return repo_url
    
    provider = detect_git_provider(repo_url)
    
    # Bitbucket requires username:app_password format
    if provider == 'bitbucket' and username:
        netloc_with_auth = f"{username}:{token}@{parsed.netloc}"
    else:
        # GitHub and GitLab use token as username
        netloc_with_auth = f"{token}@{parsed.netloc}"
    
    # Reconstruct URL
    authenticated_url = urlunparse((
        parsed.scheme,
        netloc_with_auth,
        parsed.path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))
    
    return authenticated_url


def get_git_credentials(repo_url: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """
    Get Git credentials from environment variables
    
    Supports:
    - GitHub: GITHUB_TOKEN
    - Bitbucket: BITBUCKET_USERNAME + BITBUCKET_APP_PASSWORD
    - GitLab: GITLAB_TOKEN
    - Generic: GIT_TOKEN + GIT_USERNAME
    
    Args:
        repo_url: Optional repository URL to detect provider
    
    Returns:
        Tuple of (token, username) - username is None for GitHub/GitLab
    """
    # If URL is provided, try provider-specific credentials first
    if repo_url:
        provider = detect_git_provider(repo_url)
        
        if provider == 'github':
            github_token = os.getenv('GITHUB_TOKEN')
            if github_token:
                return (github_token, None)
        
        elif provider == 'bitbucket':
            bitbucket_username = os.getenv('BITBUCKET_USERNAME')
            bitbucket_password = os.getenv('BITBUCKET_APP_PASSWORD')
            if bitbucket_username and bitbucket_password:
                return (bitbucket_password, bitbucket_username)
        
        elif provider == 'gitlab':
            gitlab_token = os.getenv('GITLAB_TOKEN')
            if gitlab_token:
                return (gitlab_token, None)
    
    # Fallback: try all providers in order (GitHub > Bitbucket > GitLab > Generic)
    github_token = os.getenv('GITHUB_TOKEN')
    if github_token:
        return (github_token, None)
    
    bitbucket_username = os.getenv('BITBUCKET_USERNAME')
    bitbucket_password = os.getenv('BITBUCKET_APP_PASSWORD')
    if bitbucket_username and bitbucket_password:
        return (bitbucket_password, bitbucket_username)
    
    gitlab_token = os.getenv('GITLAB_TOKEN')
    if gitlab_token:
        return (gitlab_token, None)
    
    # Generic credentials as last resort
    git_token = os.getenv('GIT_TOKEN')
    git_username = os.getenv('GIT_USERNAME')
    if git_token:
        return (git_token, git_username)
    
    return (None, None)


def get_authenticated_url(repo_url: str, token: Optional[str] = None, username: Optional[str] = None) -> str:
    """
    Get authenticated URL for repository cloning
    
    Supports:
    - GitHub (public/private via PAT)
    - Bitbucket (public/private via app password)
    - GitLab (public/private via PAT)
    - SSH repositories (assumes SSH keys configured)
    
    Args:
        repo_url: Repository URL (HTTPS or SSH)
        token: Optional access token/app password
        username: Optional username (required for Bitbucket)
        
    Returns:
        Authenticated URL ready for cloning
    """
    # SSH URLs pass through unchanged (assumes SSH keys are configured)
    if repo_url.startswith('git@') or repo_url.startswith('ssh://'):
        return repo_url
    
    # Auto-detect credentials if not provided
    if not token:
        token, username = get_git_credentials(repo_url)
    
    # HTTPS URLs with authentication
    if token and (repo_url.startswith('http://') or repo_url.startswith('https://')):
        return inject_token_in_url(repo_url, token, username)
    
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
    - GitHub (public/private via PAT)
    - Bitbucket (public/private via app password)
    - GitLab (public/private via PAT)
    - SSH (requires SSH keys configured)
    
    Args:
        repo_url: Repository URL (HTTPS or SSH format)
        repo_branch: Branch to clone
        local_path: Local path to clone into
        github_token: Optional token for backward compatibility (deprecated, use env vars)
        depth: Clone depth (1 = shallow clone, 0 = full history)
        
    Environment Variables:
        GitHub:
            GITHUB_TOKEN=ghp_xxxxxxxxxxxx
        
        Bitbucket:
            BITBUCKET_USERNAME=your_username
            BITBUCKET_APP_PASSWORD=your_app_password
        
        GitLab:
            GITLAB_TOKEN=glpat-xxxxxxxxxxxx
        
        Generic:
            GIT_TOKEN=your_token
            GIT_USERNAME=your_username (optional)
        
    Raises:
        Exception: If clone fails
        
    Examples:
        # Public repository
        clone_repo("https://github.com/user/repo.git", "main", "./repos/repo")
        
        # Private GitHub repository (env: GITHUB_TOKEN)
        clone_repo("https://github.com/user/private-repo.git", "main", "./repos/private")
        
        # Private Bitbucket repository (env: BITBUCKET_USERNAME + BITBUCKET_APP_PASSWORD)
        clone_repo("https://bitbucket.org/workspace/repo.git", "main", "./repos/repo")
        
        # SSH repository
        clone_repo("git@bitbucket.org:workspace/repo.git", "main", "./repos/repo")
    """
    if os.path.exists(local_path):
        print(f"Repository directory already exists at {local_path}. Skipping clone.")
        return
    
    provider = detect_git_provider(repo_url)
    
    # Get authenticated URL (supports backward compatibility with github_token param)
    if github_token:
        auth_url = inject_token_in_url(repo_url, github_token)
    else:
        auth_url = get_authenticated_url(repo_url)
    
    # Determine if URL has embedded credentials (for logging purposes)
    has_credentials = '@' in auth_url and not auth_url.startswith('git@')
    
    # Log safely (hide credentials)
    if has_credentials:
        safe_url = re.sub(r'://[^@]+@', '://***@', auth_url)
        print(f"Cloning from {provider.upper()}: {safe_url} (Branch: {repo_branch}) [Authenticated]")
    else:
        print(f"Cloning from {provider.upper()}: {auth_url} (Branch: {repo_branch})")
    
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
                error_msg = f"Failed to clone {provider.upper()} repository. Exit code: {process.returncode}\n"
                
                if provider == 'bitbucket':
                    error_msg += (
                        "Check: 1) URL is correct, 2) Branch exists, "
                        "3) BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD are set correctly, "
                        "4) App password has 'repository:read' permission, "
                        "5) SSH keys are configured (if using SSH)\n"
                        "Create app password at: https://bitbucket.org/account/settings/app-passwords/"
                    )
                elif provider == 'github':
                    error_msg += (
                        "Check: 1) URL is correct, 2) Branch exists, "
                        "3) GITHUB_TOKEN has correct permissions (if private), "
                        "4) SSH keys are configured (if using SSH)"
                    )
                elif provider == 'gitlab':
                    error_msg += (
                        "Check: 1) URL is correct, 2) Branch exists, "
                        "3) GITLAB_TOKEN has correct permissions (if private), "
                        "4) SSH keys are configured (if using SSH)"
                    )
                else:
                    error_msg += (
                        "Check: 1) URL is correct, 2) Branch exists, "
                        "3) GIT_TOKEN/GIT_USERNAME are set correctly, "
                        "4) SSH keys are configured (if using SSH)"
                    )
                
                raise Exception(error_msg)
    except FileNotFoundError:
        raise Exception(
            "Git is not installed or not found in PATH. "
            "Please install git: https://git-scm.com/downloads"
        )