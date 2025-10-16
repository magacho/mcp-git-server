# Release Notes - v[VERSION]

**Release Date:** [DATE]

**Full Changelog:** [`[PREVIOUS_TAG]...[CURRENT_TAG]`](https://github.com/magacho/mcp-git-server/compare/[PREVIOUS_TAG]...[CURRENT_TAG])

## 🚨 Breaking Changes
<!-- Mudanças que quebram compatibilidade -->
- 

## ✨ New Features
<!-- Novas funcionalidades -->
- 

## 🐛 Bug Fixes
<!-- Correções de bugs -->
- 

## ♻️ Code Refactoring
<!-- Refatorações de código -->
- 

## 🧪 Tests
<!-- Melhorias em testes -->
- 

## 📚 Documentation
<!-- Atualizações de documentação -->
- 

## 🔧 Other Changes
<!-- Outras mudanças (chores, build, etc.) -->
- 

## 🚀 Installation

### Docker (Recommended)

```bash
# Modo gratuito (embeddings locais)
docker run -p 8000:8000 \
  -e REPO_URL="https://github.com/seu-usuario/seu-repo.git" \
  -v ./data:/app/chroma_db \
  flaviomagacho/mcp-git-server:v[VERSION]
```

### Docker com OpenAI (Pago)

```bash
docker run -p 8000:8000 \
  -e REPO_URL="https://github.com/seu-usuario/seu-repo.git" \
  -e EMBEDDING_PROVIDER="openai" \
  -e OPENAI_API_KEY="sk-sua-chave" \
  -v ./data:/app/chroma_db \
  flaviomagacho/mcp-git-server:v[VERSION]
```

## 📊 Summary

- **Total commits:** [NUMBER]
- **Contributors:** [CONTRIBUTORS]

## 🔧 Technical Details

- **Docker Image:** `flaviomagacho/mcp-git-server:v[VERSION]`
- **Base Image:** Python 3.12-slim
- **Default Embeddings:** Sentence Transformers (gratuito)
- **Supported Languages:** Python, Java, JavaScript, TypeScript, Markdown, HTML, CSS, JSON, PDF

## 🆕 What's New in This Release

<!-- Destaque principal da release -->

## 🔄 Migration Guide

<!-- Se houver breaking changes, explicar como migrar -->

## 🐛 Known Issues

<!-- Issues conhecidos nesta versão -->

## 🙏 Contributors

<!-- Agradecer contribuidores -->

---

**Need help?** Check our [documentation](README.md) or open an [issue](https://github.com/magacho/mcp-git-server/issues).