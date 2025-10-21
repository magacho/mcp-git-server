# Release Notes - v[VERSION]

**Release Date:** [DATE]

**Full Changelog:** [`[PREVIOUS_TAG]...[CURRENT_TAG]`](https://github.com/magacho/mcp-git-server/compare/[PREVIOUS_TAG]...[CURRENT_TAG])

## 🚨 Breaking Changes
<!-- Changes that break compatibility -->
- 

## ✨ New Features
<!-- New features -->
- 

## 🐛 Bug Fixes
<!-- Bug fixes -->
- 

## ♻️ Code Refactoring
<!-- Code refactoring -->
- 

## 🧪 Tests
<!-- Test improvements -->
- 

## 📚 Documentation
<!-- Documentation updates -->
- 

## 🔧 Other Changes
<!-- Other changes (chores, build, etc.) -->
- 

## 🚀 Installation

### Docker (Recommended)

```bash
# Free mode (local embeddings)
docker run -p 8000:8000 \
  -e REPO_URL="https://github.com/your-username/your-repo.git" \
  -v ./data:/app/chroma_db \
  flaviomagacho/mcp-git-server:v[VERSION]
```

### Docker with OpenAI (Paid)

```bash
docker run -p 8000:8000 \
  -e REPO_URL="https://github.com/your-username/your-repo.git" \
  -e EMBEDDING_PROVIDER="openai" \
  -e OPENAI_API_KEY="sk-your-key" \
  -v ./data:/app/chroma_db \
  flaviomagacho/mcp-git-server:v[VERSION]
```

## 📊 Summary

- **Total commits:** [NUMBER]
- **Contributors:** [CONTRIBUTORS]

## 🔧 Technical Details

- **Docker Image:** `flaviomagacho/mcp-git-server:v[VERSION]`
- **Base Image:** Python 3.12-slim
- **Default Embeddings:** Sentence Transformers (free)
- **Supported Languages:** Python, Java, JavaScript, TypeScript, Markdown, HTML, CSS, JSON, PDF

## 🆕 What's New in This Release

<!-- Highlight main feature of the release -->

## 🔄 Migration Guide

<!-- If there are breaking changes, explain how to migrate -->

## 🐛 Known Issues

<!-- Known issues in this version -->

## 🙏 Contributors

<!-- Thank contributors -->

---

**Need help?** Check our [documentation](README.md) or open an [issue](https://github.com/magacho/mcp-git-server/issues).