import os
import re
import subprocess

def get_repo_name_from_url(url):
    try:
        repo_name = url.split('/')[-1]
        repo_name = re.sub(r'\.git$', '', repo_name)
        safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', repo_name)
        return safe_name
    except Exception:
        return "default_repo"

def clone_repo(repo_url, repo_branch, local_path):
    if not os.path.exists(local_path):
        print(f"Clonando de: {repo_url} (Branch: {repo_branch})")
        git_command = [
            "git", "clone", "--progress", "--depth", "1",
            "--branch", repo_branch, repo_url, local_path
        ]
        with subprocess.Popen(git_command, stderr=subprocess.PIPE, text=True, bufsize=1) as process:
            for line in process.stderr:
                print(f"  [git] {line.strip()}")
        if process.returncode != 0:
            raise Exception(f"Failed to clone repository. Exit code: {process.returncode}")
    else:
        print(f"Repository directory already exists at {local_path}. Skipping clone.")