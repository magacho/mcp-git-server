
# Release Notes - v0.9.0

**Release Date:** 2025-11-04

## ✨ New Features

### Infrastructure as Code Support
- **feat: add Terraform file support (.tf, .tfvars, .hcl)** - Full support for indexing and searching Terraform/HCL files
  - New file extensions: `.tf`, `.tfvars`, `.hcl`
  - Seamless integration with existing embedding pipeline
  - Enables DevOps and SRE workflows
  - Use cases: IaC documentation, cloud architecture search

## 🧪 Testing

- **test: comprehensive test suite for Terraform support**
  - 9 new tests covering file extensions, processing, and metadata
  - 100% pass rate for Terraform-specific tests
  - Test coverage increased from 0% to 19% for document_loader.py

## 📚 Documentation

- docs: add Infrastructure section to README with Terraform file types
- docs: update CHANGELOG with v0.9.0 release notes
- docs: move Terraform support to High Priority #1 in ROADMAP

## 🚀 Installation

### Docker (Recommended)

```bash
# Free mode (local embeddings)
docker run -p 8000:8000 \
  -e REPO_URL="https://github.com/your-user/your-repo.git" \
  -v ./data:/app/chroma_db \
  flaviomagacho/mcp-git-server:v0.9.0

# Example with Terraform repository
docker run -p 8000:8000 \
  -e REPO_URL="https://github.com/terraform-aws-modules/terraform-aws-vpc" \
  -e REPO_BRANCH="master" \
  flaviomagacho/mcp-git-server:v0.9.0
```

## 📊 Summary

- **New file types:** `.tf`, `.tfvars`, `.hcl` (Terraform/HCL)
- **New tests:** 9 tests (100% passing)
- **Total tests:** 67 tests (58 passing, 9 pre-existing failures)
- **Use cases:** Infrastructure as Code documentation, DevOps workflows
- **Implementation time:** ~35 minutes (feature + tests)
- **Breaking changes:** None

## 🔗 Links

<<<<<<< HEAD
- **Full Changelog:** [`v0.8.0...v0.9.0`](https://github.com/magacho/mcp-git-server/compare/v0.8.0...v0.9.0)
=======
- **Full Changelog:** [`v0.6.0...v0.9.0`](https://github.com/magacho/mcp-git-server/compare/v0.6.0...v0.9.0)
>>>>>>> cc86056 (docs: prepare release v0.9.0 - Infrastructure as Code support)
- **Docker Image:** `flaviomagacho/mcp-git-server:v0.9.0`

---

# Release Notes - v0.3.0

**Release Date:** 2025-11-04

## ✨ New Features

### Infrastructure as Code Support
- feat: add Terraform file support (.tf, .tfvars, .hcl) - Full support for indexing and searching Terraform/HCL files

## 📚 Documentation

- docs: add Terraform files to supported file types in README
- docs: update ROADMAP with Terraform as high priority feature

## 🚀 Installation

### Docker (Recommended)

```bash
# Free mode (local embeddings)
docker run -p 8000:8000 \
  -e REPO_URL="https://github.com/your-user/your-repo.git" \
  -v ./data:/app/chroma_db \
  flaviomagacho/mcp-git-server:latest
```

## 📊 Summary

- **New file types:** `.tf`, `.tfvars`, `.hcl`
- **Use cases:** Infrastructure as Code, Terraform documentation, DevOps workflows

---

# Release Notes - v0.2.1

**Release Date:** 2025-10-16

# Release Notes - v0.6.0

**Release Date:** 2025-10-21

**Full Changelog:** [`v0.5.1...v0.6.0`](https://github.com/magacho/mcp-git-server/compare/v0.5.1...v0.6.0)

## ✨ New Features

- feat: implement quick wins for production stability (3282a21)

## 📚 Documentation

- docs: update CHANGELOG for v0.5.1 (d095bb2)

## 🚀 Installation

### Docker (Recommended)

```bash
# Modo gratuito (embeddings locais)
 docker run -p 8000:8000 \
   -e REPO_URL="https://github.com/seu-usuario/seu-repo.git" \
   -v ./data:/app/chroma_db \
   flaviomagacho/mcp-git-server:v0.6.0
```

## 📊 Summary

- **Total commits:** 2
- **Contributors:** @magacho


---


# Release Notes - v0.5.1

**Release Date:** 2025-10-21

**Full Changelog:** [`v0.5.0...v0.5.1`](https://github.com/magacho/mcp-git-server/compare/v0.5.0...v0.5.1)

## 📚 Documentation

- docs: complete English translation (i18n phase 2) (c8d9275)
- docs: update CHANGELOG for v0.5.1 (b593aeb)
- docs: update CHANGELOG for v0.5.0 (0919b8c)

## 🔧 Other Changes

- refactor: translate all code to English (i18n) (53b666a)

## 🚀 Installation

### Docker (Recommended)

```bash
# Modo gratuito (embeddings locais)
 docker run -p 8000:8000 \
   -e REPO_URL="https://github.com/seu-usuario/seu-repo.git" \
   -v ./data:/app/chroma_db \
   flaviomagacho/mcp-git-server:v0.5.1
```

## 📊 Summary

- **Total commits:** 4
- **Contributors:** @magacho


---


# Release Notes - v0.5.1

**Release Date:** 2025-10-21

**Full Changelog:** [`v0.5.0...v0.5.1`](https://github.com/magacho/mcp-git-server/compare/v0.5.0...v0.5.1)

## 📚 Documentation

- docs: update CHANGELOG for v0.5.0 (0919b8c)

## 🔧 Other Changes

- refactor: translate all code to English (i18n) (53b666a)

## 🚀 Installation

### Docker (Recommended)

```bash
# Modo gratuito (embeddings locais)
 docker run -p 8000:8000 \
   -e REPO_URL="https://github.com/seu-usuario/seu-repo.git" \
   -v ./data:/app/chroma_db \
   flaviomagacho/mcp-git-server:v0.5.1
```

## 📊 Summary

- **Total commits:** 2
- **Contributors:** @magacho


---


# Release Notes - v0.5.0

**Release Date:** 2025-10-21

**Full Changelog:** [`v0.4.0...v0.5.0`](https://github.com/magacho/mcp-git-server/compare/v0.4.0...v0.5.0)

## ✨ New Features

- feat: add support for private GitHub repositories (c90c36d)

## 📚 Documentation

- docs: update CHANGELOG for v0.4.0 (b653bf4)

## 🚀 Installation

### Docker (Recommended)

```bash
# Modo gratuito (embeddings locais)
 docker run -p 8000:8000 \
   -e REPO_URL="https://github.com/seu-usuario/seu-repo.git" \
   -v ./data:/app/chroma_db \
   flaviomagacho/mcp-git-server:v0.5.0
```

## 📊 Summary

- **Total commits:** 2
- **Contributors:** @magacho


---


# Release Notes - v0.4.0

**Release Date:** 2025-10-21

**Full Changelog:** [`v0.3.0...v0.4.0`](https://github.com/magacho/mcp-git-server/compare/v0.3.0...v0.4.0)

## 🐛 Bug Fixes

- fix: update upload-artifact action from v3 to v4 (57eb137)

## 📚 Documentation

- docs: update CHANGELOG for v0.3.0 (4bab62a)

## 🚀 Installation

### Docker (Recommended)

```bash
# Modo gratuito (embeddings locais)
 docker run -p 8000:8000 \
   -e REPO_URL="https://github.com/seu-usuario/seu-repo.git" \
   -v ./data:/app/chroma_db \
   flaviomagacho/mcp-git-server:v0.4.0
```

## 📊 Summary

- **Total commits:** 2
- **Contributors:** @magacho


---


# Release Notes - v0.3.0

**Release Date:** 2025-10-21

**Full Changelog:** [`v0.2.1...v0.3.0`](https://github.com/magacho/mcp-git-server/compare/v0.2.1...v0.3.0)

## ✨ New Features

- feat: implement quick wins for production readiness (79785d6)

## 📚 Documentation

- docs: update CHANGELOG for v0.2.1 (4e33553)

## 🚀 Installation

### Docker (Recommended)

```bash
# Modo gratuito (embeddings locais)
 docker run -p 8000:8000 \
   -e REPO_URL="https://github.com/seu-usuario/seu-repo.git" \
   -v ./data:/app/chroma_db \
   flaviomagacho/mcp-git-server:v0.3.0
```

## 📊 Summary

- **Total commits:** 2
- **Contributors:** @magacho


---


**Full Changelog:** [`v0.2.0...v0.2.1`](https://github.com/magacho/mcp-git-server/compare/v0.2.0...v0.2.1)

## 🐛 Bug Fixes

- fix: corrige workflow de release notes - resolve problema de detached HEAD (cb12844)

## 🚀 Installation

### Docker (Recommended)

```bash
# Modo gratuito (embeddings locais)
 docker run -p 8000:8000 \
   -e REPO_URL="https://github.com/seu-usuario/seu-repo.git" \
   -v ./data:/app/chroma_db \
   flaviomagacho/mcp-git-server:v0.2.1
```

## 📊 Summary

- **Total commits:** 1
- **Contributors:** @magacho


---

