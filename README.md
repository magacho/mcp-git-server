# Git Repository Context Retrieval Server (MCP Server)

This project provides a self-contained Docker API server that clones a Git repository, indexes it using embedding models, and exposes an endpoint to retrieve relevant code and documentation snippets for natural language questions.

It's the "Retrieval" piece for a RAG (Retrieval-Augmented Generation) system, designed to feed an external AI agent (like an n8n workflow) with the necessary context to answer questions about a codebase.

### ✨ Features

-   **Flexible Embeddings:** Support for free local embeddings (Sentence Transformers) or OpenAI (paid)
-   **Zero Configuration:** Works without API keys - local embeddings by default
-   **🔐 Private Repositories:** Full support for GitHub, Bitbucket, and GitLab (PAT or SSH)
-   **Multi-Provider Support:** GitHub, Bitbucket, GitLab - auto-detected from URL
-   **Configurable via Environment Variables:** Point to any public or private Git repository without changing code
-   **Persistent Cache:** Vector database is created on first run and reused
-   **Simple API:** REST endpoints for search and monitoring
-   **Production Ready:** Optimized Docker container with non-root user
-   **Cost Estimation:** Shows estimated costs for different providers

### 🚀 How to Use

#### Prerequisites

1.  **Docker** installed and running on your machine.
2.  (Optional) An **OpenAI API Key** for paid embeddings. You can get one at [platform.openai.com/api-keys](https://platform.openai.com/api-keys).

#### Running with Docker

**Free Mode (Default - Local Embeddings):**
```bash
docker run -p 8000:8000 \
  -e REPO_URL="https://github.com/n8n-io/n8n.git" \
  -e REPO_BRANCH="master" \
  -v ./mcp_data/chroma_db:/app/chroma_db \
  --name mcp-server \
  flaviomagacho/mcp-git-server:latest
```

**OpenAI Mode (Paid - High Quality):**
```bash
docker run -p 8000:8000 \
  -e REPO_URL="https://github.com/n8n-io/n8n.git" \
  -e REPO_BRANCH="master" \
  -e EMBEDDING_PROVIDER="openai" \
  -e OPENAI_API_KEY="YOUR_SECURE_API_KEY" \
  -v ./mcp_data/chroma_db:/app/chroma_db \
  --name mcp-server \
  flaviomagacho/mcp-git-server:latest
```

**🔐 Private GitHub Repository:**
```bash
docker run -p 8000:8000 \
  -e REPO_URL="https://github.com/your-username/private-repo.git" \
  -e REPO_BRANCH="main" \
  -e GITHUB_TOKEN="ghp_your_personal_token_here" \
  -v ./mcp_data/chroma_db:/app/chroma_db \
  --name mcp-server \
  flaviomagacho/mcp-git-server:latest
```

**🔐 Private Bitbucket Repository:**
```bash
docker run -p 8000:8000 \
  -e REPO_URL="https://bitbucket.org/workspace/private-repo.git" \
  -e REPO_BRANCH="main" \
  -e BITBUCKET_USERNAME="your_username" \
  -e BITBUCKET_APP_PASSWORD="your_app_password" \
  -v ./mcp_data/chroma_db:/app/chroma_db \
  --name mcp-server \
  flaviomagacho/mcp-git-server:latest
```

> 📖 **Documentation:**
> - GitHub: [PRIVATE_REPOS.md](PRIVATE_REPOS.md)
> - Bitbucket: [BITBUCKET.md](BITBUCKET.md)

#### Build and Local Testing

```bash
# Clone the repository
git clone https://github.com/magacho/mcp-git-server.git
cd mcp-git-server

# Build the image
docker build -t mcp-git-server .

# Run locally
docker run -p 8000:8000 \
  -e REPO_URL="https://github.com/n8n-io/n8n.git" \
  -e REPO_BRANCH="master" \
  -v ./chroma_db:/app/chroma_db \
  mcp-git-server
```

### 📡 API Endpoints

#### Health Check
```bash
GET /health
```

Returns server status:
```json
{
  "status": "ready"
}
```

#### Retrieve Context
```bash
POST /retrieve
Content-Type: application/json

{
  "query": "How does authentication work in the application?",
  "top_k": 5
}
```

Returns relevant code snippets:
```json
{
  "results": [
    {
      "content": "Code snippet content...",
      "metadata": {
        "source": "path/to/file.py"
      },
      "relevance_score": 0.95
    }
  ],
  "total_results": 5
}
```

#### Embedding Provider Info
```bash
GET /embedding-info
```

Returns information about the current embedding provider:
```json
{
  "provider": "sentence-transformers",
  "available_providers": {
    "sentence-transformers": {
      "available": true,
      "cost": "Free",
      "quality": "Good"
    },
    "openai": {
      "available": true,
      "cost": "$0.0001 per 1K tokens",
      "quality": "Excellent"
    }
  }
}
```

### ⚙️ Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REPO_URL` | Git repository URL (HTTPS or SSH) | - | ✅ Yes |
| `REPO_BRANCH` | Branch to clone | `main` | No |
| `GITHUB_TOKEN` | GitHub PAT for private repos | - | No |
| `EMBEDDING_PROVIDER` | Embedding provider (`sentence-transformers`, `openai`, `huggingface`, `auto`) | `sentence-transformers` | No |
| `OPENAI_API_KEY` | OpenAI API key (required if provider is openai) | - | Conditional |
| `TOKEN_COUNT_METHOD` | Token counting method (`local`, `tiktoken`, `auto`) | `auto` | No |

### 🔐 Private Repository Support

Supports two authentication methods:

1. **GitHub Personal Access Token (PAT)** - HTTPS
   ```bash
   export GITHUB_TOKEN=ghp_your_token
   export REPO_URL=https://github.com/user/private-repo.git
   ```

2. **SSH Keys**
   ```bash
   export REPO_URL=git@github.com:user/private-repo.git
   docker run -v ~/.ssh:/root/.ssh:ro ...
   ```

See [PRIVATE_REPOS.md](PRIVATE_REPOS.md) for complete documentation.

### 📊 Embedding Providers

| Provider | Cost | Quality | Speed | Use Case |
|----------|------|---------|-------|----------|
| `sentence-transformers` | Free | Good | Fast | Development, testing, personal projects |
| `openai` | $0.0001/1K tokens | Excellent | Medium | Production, high quality requirements |
| `huggingface` | Free | Variable | Medium | Experimentation, custom models |

### 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│  FastAPI     │────▶│   Vector    │
│  (n8n, etc) │     │   Server     │     │  Database   │
└─────────────┘     └──────────────┘     │  (Chroma)   │
                            │             └─────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │  Embeddings  │
                    │  (Local/API) │
                    └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │ Git Repo     │
                    │ (Cloned)     │
                    └──────────────┘
```

### 🔍 Supported File Types

- **Code:** `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.java`, `.cpp`, `.c`, `.h`, `.cs`, `.php`, `.rb`, `.swift`, `.go`, `.rs`
- **Web:** `.html`, `.css`, `.vue`, `.svelte`
- **Config:** `.json`, `.yml`, `.yaml`, `.xml`, `.env`
- **Scripts:** `.sh`, `.bash`, `.sql`
- **Docs:** `.md`, `.txt`, `.pdf`
- **Special:** `README`, `LICENSE`, `DOCKERFILE`, `MAKEFILE`, etc.

### 🎯 Use Cases

1. **AI-Powered Code Assistance**
   - Answer questions about your codebase
   - Generate documentation from code
   - Code review assistance

2. **Knowledge Base**
   - Internal documentation search
   - Onboarding new developers
   - Project knowledge retention

3. **CI/CD Integration**
   - Automated code analysis
   - Documentation generation
   - Change impact analysis

4. **Private Projects**
   - Secure company codebases
   - Client projects
   - Proprietary software

### 📚 Documentation

- [PRIVATE_REPOS.md](PRIVATE_REPOS.md) - Private repository setup
- [QUICK_WINS_IMPLEMENTED.md](QUICK_WINS_IMPLEMENTED.md) - Recent improvements
- [ROADMAP.md](ROADMAP.md) - Future plans
- [CHANGELOG.md](CHANGELOG.md) - Version history

### 🧪 Testing

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py -v
```

### 🛠️ Development

```bash
# Clone repository
git clone https://github.com/magacho/mcp-git-server.git
cd mcp-git-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run locally
export REPO_URL=https://github.com/example/repo.git
python main.py

# Access API
curl http://localhost:8000/health
```

### 🐛 Troubleshooting

**Problem:** Server is slow to start
- **Solution:** First indexing takes time. Subsequent starts are faster (uses cached database).

**Problem:** Out of memory errors
- **Solution:** Reduce repository size or increase Docker memory limit.

**Problem:** Authentication failed for private repo
- **Solution:** Check GitHub token has correct permissions (`repo` scope) and is not expired.

**Problem:** Embedding errors
- **Solution:** Check OPENAI_API_KEY is valid or switch to local embeddings.

### 📄 License

MIT License - See [LICENSE](LICENSE) for details.

### 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

See [GIT_COMMIT_GUIDE.md](GIT_COMMIT_GUIDE.md) for commit conventions.

### 📧 Contact

- **Author:** Flavio Magacho
- **Repository:** https://github.com/magacho/mcp-git-server
- **Issues:** https://github.com/magacho/mcp-git-server/issues

### 🌟 Star History

If this project helped you, please consider giving it a ⭐ on GitHub!

---

Made with ❤️ for the developer community
