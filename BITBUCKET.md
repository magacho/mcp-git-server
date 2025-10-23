# Bitbucket Repository Support

This document explains how to use MCP Git Server with Bitbucket repositories (both public and private).

## 🌐 Public Repositories

Public Bitbucket repositories work without any authentication:

```bash
docker run -p 8000:8000 \
  -e REPO_URL="https://bitbucket.org/workspace/public-repo.git" \
  -e REPO_BRANCH="main" \
  -v ./data:/app/chroma_db \
  flaviomagacho/mcp-git-server:latest
```

## 🔐 Private Repositories

Bitbucket requires **App Passwords** for HTTPS authentication (personal passwords don't work with Git).

### Option 1: HTTPS with App Password (Recommended)

#### Step 1: Create an App Password

1. Go to [Bitbucket App Passwords](https://bitbucket.org/account/settings/app-passwords/)
2. Click **Create app password**
3. Give it a label (e.g., "MCP Git Server")
4. Select permissions:
   - ✅ **Repositories: Read** (minimum required)
   - ✅ **Repositories: Write** (if you need to push changes)
5. Click **Create**
6. **Copy the password immediately** (you won't see it again!)

#### Step 2: Run with Docker

```bash
docker run -p 8000:8000 \
  -e REPO_URL="https://bitbucket.org/workspace/private-repo.git" \
  -e REPO_BRANCH="main" \
  -e BITBUCKET_USERNAME="your_username" \
  -e BITBUCKET_APP_PASSWORD="your_app_password" \
  -v ./data:/app/chroma_db \
  flaviomagacho/mcp-git-server:latest
```

**Important Notes:**
- Use your **Bitbucket username**, not email
- Use the **app password**, not your account password
- App password must have `repository:read` permission

### Option 2: SSH with SSH Keys

If you prefer SSH authentication:

#### Step 1: Generate SSH Key (if you don't have one)

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

#### Step 2: Add SSH Key to Bitbucket

1. Copy your public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

2. Go to [Bitbucket SSH Keys](https://bitbucket.org/account/settings/ssh-keys/)
3. Click **Add key**
4. Paste your public key and save

#### Step 3: Run with Docker

```bash
docker run -p 8000:8000 \
  -e REPO_URL="git@bitbucket.org:workspace/private-repo.git" \
  -e REPO_BRANCH="main" \
  -v ~/.ssh:/root/.ssh:ro \
  -v ./data:/app/chroma_db \
  flaviomagacho/mcp-git-server:latest
```

**Note:** This mounts your SSH keys into the container (read-only for security).

## 🔄 Switching from GitHub to Bitbucket

If you're migrating from GitHub, just update your environment variables:

**Before (GitHub):**
```bash
-e REPO_URL="https://github.com/user/repo.git"
-e GITHUB_TOKEN="ghp_xxxxx"
```

**After (Bitbucket):**
```bash
-e REPO_URL="https://bitbucket.org/workspace/repo.git"
-e BITBUCKET_USERNAME="your_username"
-e BITBUCKET_APP_PASSWORD="xxxxx"
```

The server automatically detects the Git provider and uses the correct authentication method.

## 🧪 Testing Your Setup

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

Expected output:
```json
{
  "status": "healthy",
  "repository": {
    "url": "https://bitbucket.org/workspace/repo.git",
    "provider": "bitbucket",
    "authenticated": true
  }
}
```

### Test 2: Query the Repository

```bash
curl -X POST http://localhost:8000/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication", "top_k": 3}'
```

## ⚠️ Common Issues

### Issue 1: "Authentication failed"

**Cause:** Wrong username or app password

**Solution:**
- Verify your Bitbucket username (not email)
- Regenerate app password if needed
- Ensure app password has `repository:read` permission

### Issue 2: "Repository not found"

**Cause:** Wrong URL format or repository name

**Solution:**
```bash
# Correct format:
https://bitbucket.org/workspace/repository.git

# NOT:
https://bitbucket.org/workspace/repository  # Missing .git
https://bitbucket.org/user/repo.git         # Use workspace, not user
```

### Issue 3: "Permission denied"

**Cause:** App password lacks required permissions

**Solution:**
- Go to [App Passwords](https://bitbucket.org/account/settings/app-passwords/)
- Edit or recreate with `repository:read` permission

## 📊 Bitbucket vs GitHub

| Feature | Bitbucket | GitHub |
|---------|-----------|--------|
| **Public repos** | ✅ Works | ✅ Works |
| **Private repos (HTTPS)** | ✅ App password + username | ✅ Personal Access Token |
| **Private repos (SSH)** | ✅ SSH keys | ✅ SSH keys |
| **Authentication format** | `username:password@url` | `token@url` |
| **Token permissions** | `repository:read` | `repo` scope |

## 🔗 Useful Links

- [Bitbucket App Passwords](https://bitbucket.org/account/settings/app-passwords/)
- [Bitbucket SSH Keys](https://bitbucket.org/account/settings/ssh-keys/)
- [Bitbucket API Documentation](https://developer.atlassian.com/cloud/bitbucket/)

## 💡 Pro Tips

1. **Use App Passwords, not account password** - Account passwords don't work with Git over HTTPS
2. **One app password per application** - Create separate passwords for different tools
3. **Rotate passwords regularly** - Delete old passwords you're not using
4. **Use SSH for better security** - No passwords stored in environment variables
5. **Test with public repo first** - Verify setup before using private repos

## 🤝 Need Help?

- Check logs: `docker logs <container_name>`
- Open an issue: [GitHub Issues](https://github.com/magacho/mcp-git-server/issues)
- Read main docs: [README.md](README.md)

---

**Last Updated:** October 23, 2025
