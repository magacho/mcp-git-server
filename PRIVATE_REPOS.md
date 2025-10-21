# Private Repository Support

## Overview

The MCP Git Server now supports cloning private GitHub repositories using two authentication methods:

1. **GitHub Personal Access Token (PAT)** - HTTPS authentication
2. **SSH Keys** - SSH authentication

## Authentication Methods

### Method 1: GitHub Personal Access Token (Recommended)

Personal Access Tokens (PAT) are the recommended way to authenticate with private repositories over HTTPS.

#### Step 1: Create a GitHub Personal Access Token

1. Go to GitHub Settings: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a descriptive name (e.g., "MCP Git Server")
4. Select scopes:
   - ✅ `repo` - Full control of private repositories (required)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)

#### Step 2: Configure the Server

**Option A: Environment Variable**

```bash
export GITHUB_TOKEN=ghp_your_personal_access_token_here
export REPO_URL=https://github.com/your-username/private-repo.git
export REPO_BRANCH=main
```

**Option B: .env File**

```env
GITHUB_TOKEN=ghp_your_personal_access_token_here
REPO_URL=https://github.com/your-username/private-repo.git
REPO_BRANCH=main
```

**Option C: Docker Run**

```bash
docker run -d \
  -e REPO_URL=https://github.com/your-username/private-repo.git \
  -e REPO_BRANCH=main \
  -e GITHUB_TOKEN=ghp_your_personal_access_token_here \
  -e EMBEDDING_PROVIDER=sentence-transformers \
  -p 8000:8000 \
  mcp-git-server
```

#### Step 3: Verify

The server will log:
```
>>> GitHub token detected - will use for authentication
Cloning from: https://***@github.com/your-username/private-repo.git [Authenticated]
```

### Method 2: SSH Keys

SSH keys allow authentication without storing tokens in environment variables.

#### Step 1: Set up SSH Keys

If you don't have SSH keys configured:

```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -C "your-email@example.com"

# Start SSH agent
eval "$(ssh-agent -s)"

# Add your key
ssh-add ~/.ssh/id_ed25519

# Copy public key to clipboard
cat ~/.ssh/id_ed25519.pub
```

#### Step 2: Add SSH Key to GitHub

1. Go to GitHub Settings: https://github.com/settings/keys
2. Click "New SSH key"
3. Paste your public key
4. Click "Add SSH key"

#### Step 3: Configure the Server

Use SSH URL format:

```bash
export REPO_URL=git@github.com:your-username/private-repo.git
export REPO_BRANCH=main
```

**Docker with SSH Keys:**

```bash
docker run -d \
  -e REPO_URL=git@github.com:your-username/private-repo.git \
  -e REPO_BRANCH=main \
  -e EMBEDDING_PROVIDER=sentence-transformers \
  -v ~/.ssh:/root/.ssh:ro \
  -p 8000:8000 \
  mcp-git-server
```

## Organization Repositories

For organization private repositories, ensure your PAT or SSH key has access:

### With PAT:
```bash
export GITHUB_TOKEN=ghp_your_token_with_org_access
export REPO_URL=https://github.com/your-org/private-project.git
```

### With SSH:
```bash
export REPO_URL=git@github.com:your-org/private-project.git
```

## Security Best Practices

### 1. Token Security

✅ **DO:**
- Store tokens in environment variables
- Use `.env` files (add to `.gitignore`)
- Rotate tokens regularly (e.g., every 90 days)
- Use tokens with minimal required scopes
- Delete tokens when no longer needed

❌ **DON'T:**
- Commit tokens to Git repositories
- Share tokens in plain text
- Use tokens with excessive permissions
- Leave unused tokens active

### 2. Token Scopes

Minimum required scopes:
- `repo` - For private repository access

Optional scopes:
- `read:org` - If accessing organization repositories

### 3. SSH Key Security

✅ **DO:**
- Use passphrase-protected keys
- Use ed25519 or RSA 4096-bit keys
- Keep private keys secure (chmod 600)
- Use different keys for different purposes

❌ **DON'T:**
- Share private keys
- Use keys without passphrases in production
- Commit private keys to repositories

## Troubleshooting

### Error: "Authentication failed"

**Cause:** Invalid or expired token

**Solution:**
1. Verify token is correct (no extra spaces)
2. Check token hasn't expired
3. Verify token has `repo` scope
4. Generate a new token if needed

### Error: "Repository not found"

**Cause:** Wrong URL or missing permissions

**Solution:**
1. Verify repository URL is correct
2. Check you have access to the repository
3. For organizations, verify token has org access
4. Check repository visibility settings

### Error: "Permission denied (publickey)"

**Cause:** SSH key not configured or not added to GitHub

**Solution:**
1. Verify SSH key is added to GitHub
2. Test SSH connection: `ssh -T git@github.com`
3. Check SSH agent is running
4. Verify private key permissions (chmod 600)

### Token Not Being Used

**Symptoms:** Public repository clones work, private fail

**Solution:**
1. Verify `GITHUB_TOKEN` environment variable is set
2. Check for typos in variable name
3. Restart server after setting token
4. Check server logs for "GitHub token detected"

## Testing Authentication

### Test HTTPS with PAT:

```bash
# Set token
export GITHUB_TOKEN=ghp_your_token

# Test clone (replace with your private repo)
git clone https://$GITHUB_TOKEN@github.com/your-username/private-repo.git test-clone

# Cleanup
rm -rf test-clone
```

### Test SSH:

```bash
# Test GitHub connection
ssh -T git@github.com

# Expected output:
# Hi username! You've successfully authenticated, but GitHub does not provide shell access.

# Test clone
git clone git@github.com:your-username/private-repo.git test-clone

# Cleanup
rm -rf test-clone
```

## Examples

### Example 1: Private Personal Repository

```bash
# Using PAT
export GITHUB_TOKEN=ghp_abc123xyz789
export REPO_URL=https://github.com/johndoe/my-private-app.git
export REPO_BRANCH=main

# Start server
docker run -d \
  -e GITHUB_TOKEN=$GITHUB_TOKEN \
  -e REPO_URL=$REPO_URL \
  -e REPO_BRANCH=$REPO_BRANCH \
  -p 8000:8000 \
  mcp-git-server
```

### Example 2: Organization Repository

```bash
# Using PAT with org access
export GITHUB_TOKEN=ghp_def456uvw012
export REPO_URL=https://github.com/acme-corp/internal-tools.git
export REPO_BRANCH=develop

python main.py
```

### Example 3: SSH Authentication

```bash
# Using SSH
export REPO_URL=git@github.com:startup-xyz/backend-api.git
export REPO_BRANCH=production

# Run with SSH keys mounted
docker run -d \
  -e REPO_URL=$REPO_URL \
  -e REPO_BRANCH=$REPO_BRANCH \
  -v ~/.ssh:/root/.ssh:ro \
  -p 8000:8000 \
  mcp-git-server
```

## Advanced Configuration

### Custom Git Configuration

For advanced Git configuration (e.g., custom SSH config, multiple keys):

1. Create `.ssh/config`:
```
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_work
    IdentitiesOnly yes
```

2. Mount in Docker:
```bash
docker run -d \
  -v ~/.ssh:/root/.ssh:ro \
  -e REPO_URL=git@github.com:your-org/repo.git \
  -p 8000:8000 \
  mcp-git-server
```

### Token Rotation

To rotate tokens without downtime:

1. Generate new token
2. Update environment variable
3. Restart server

```bash
# Update token
export GITHUB_TOKEN=ghp_new_token_here

# Restart Docker container
docker restart mcp-git-server
```

## API Changes

No API changes. The authentication is transparent to API consumers.

All endpoints (`/`, `/health`, `/retrieve`, `/embedding-info`) work the same way regardless of authentication method.

## References

- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub SSH Keys](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [Git Credential Storage](https://git-scm.com/book/en/v2/Git-Tools-Credential-Storage)

## Support

For issues with private repository authentication:

1. Check this documentation first
2. Review troubleshooting section
3. Test authentication outside the server
4. Open an issue with:
   - Authentication method used (PAT/SSH)
   - Error message (hide sensitive data)
   - Steps to reproduce
