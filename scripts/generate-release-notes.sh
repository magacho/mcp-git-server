#!/bin/bash

# Script para gerar release notes localmente
# Uso: ./scripts/generate-release-notes.sh [tag_anterior] [tag_atual]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Gerador de Release Notes${NC}"
echo "=================================="

# Verificar se estamos em um repositório git
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Erro: Não é um repositório Git${NC}"
    exit 1
fi

# Obter tags
if [ $# -eq 0 ]; then
    # Usar as duas tags mais recentes
    CURRENT_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "HEAD")
    PREVIOUS_TAG=$(git describe --tags --abbrev=0 $CURRENT_TAG^ 2>/dev/null || git rev-list --max-parents=0 HEAD)
elif [ $# -eq 1 ]; then
    CURRENT_TAG=$1
    PREVIOUS_TAG=$(git describe --tags --abbrev=0 $CURRENT_TAG^ 2>/dev/null || git rev-list --max-parents=0 HEAD)
elif [ $# -eq 2 ]; then
    PREVIOUS_TAG=$1
    CURRENT_TAG=$2
else
    echo -e "${RED}❌ Uso: $0 [tag_anterior] [tag_atual]${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Gerando release notes de ${PREVIOUS_TAG} para ${CURRENT_TAG}${NC}"

# Verificar se as tags existem
if ! git rev-parse --verify $CURRENT_TAG >/dev/null 2>&1; then
    echo -e "${RED}❌ Tag atual '$CURRENT_TAG' não encontrada${NC}"
    exit 1
fi

if ! git rev-parse --verify $PREVIOUS_TAG >/dev/null 2>&1; then
    echo -e "${RED}❌ Tag anterior '$PREVIOUS_TAG' não encontrada${NC}"
    exit 1
fi

# Obter commits entre as tags
echo -e "${BLUE}🔍 Analisando commits...${NC}"
COMMITS=$(git log --pretty=format:"%s (%h) - %an" $PREVIOUS_TAG..$CURRENT_TAG --no-merges)

if [ -z "$COMMITS" ]; then
    echo -e "${YELLOW}⚠️  Nenhum commit encontrado entre $PREVIOUS_TAG e $CURRENT_TAG${NC}"
    exit 0
fi

# Categorizar commits
FEATURES=""
FIXES=""
DOCS=""
CHORES=""
BREAKING=""
TESTS=""
REFACTOR=""

while IFS= read -r commit; do
    if [[ $commit == *"feat"* ]] || [[ $commit == *"feature"* ]] || [[ $commit == *"add"* ]]; then
        FEATURES="$FEATURES\n- $commit"
    elif [[ $commit == *"fix"* ]] || [[ $commit == *"bug"* ]] || [[ $commit == *"hotfix"* ]]; then
        FIXES="$FIXES\n- $commit"
    elif [[ $commit == *"docs"* ]] || [[ $commit == *"doc"* ]] || [[ $commit == *"readme"* ]]; then
        DOCS="$DOCS\n- $commit"
    elif [[ $commit == *"test"* ]] || [[ $commit == *"spec"* ]]; then
        TESTS="$TESTS\n- $commit"
    elif [[ $commit == *"refactor"* ]] || [[ $commit == *"refact"* ]]; then
        REFACTOR="$REFACTOR\n- $commit"
    elif [[ $commit == *"BREAKING"* ]] || [[ $commit == *"breaking"* ]]; then
        BREAKING="$BREAKING\n- $commit"
    else
        CHORES="$CHORES\n- $commit"
    fi
done <<< "$COMMITS"

# Criar diretório de release notes se não existir
mkdir -p release-notes

# Nome do arquivo
RELEASE_FILE="release-notes/release-$CURRENT_TAG.md"

# Gerar release notes
echo -e "${GREEN}📝 Gerando arquivo de release notes...${NC}"

cat > "$RELEASE_FILE" << EOF
# Release Notes - $CURRENT_TAG

**Release Date:** $(date '+%Y-%m-%d')

**Full Changelog:** [\`$PREVIOUS_TAG...$CURRENT_TAG\`](https://github.com/magacho/mcp-git-server/compare/$PREVIOUS_TAG...$CURRENT_TAG)

EOF

# Adicionar seções apenas se tiverem conteúdo
if [ ! -z "$BREAKING" ]; then
    echo "## 🚨 Breaking Changes" >> "$RELEASE_FILE"
    echo -e "$BREAKING" >> "$RELEASE_FILE"
    echo "" >> "$RELEASE_FILE"
fi

if [ ! -z "$FEATURES" ]; then
    echo "## ✨ New Features" >> "$RELEASE_FILE"
    echo -e "$FEATURES" >> "$RELEASE_FILE"
    echo "" >> "$RELEASE_FILE"
fi

if [ ! -z "$FIXES" ]; then
    echo "## 🐛 Bug Fixes" >> "$RELEASE_FILE"
    echo -e "$FIXES" >> "$RELEASE_FILE"
    echo "" >> "$RELEASE_FILE"
fi

if [ ! -z "$REFACTOR" ]; then
    echo "## ♻️ Code Refactoring" >> "$RELEASE_FILE"
    echo -e "$REFACTOR" >> "$RELEASE_FILE"
    echo "" >> "$RELEASE_FILE"
fi

if [ ! -z "$TESTS" ]; then
    echo "## 🧪 Tests" >> "$RELEASE_FILE"
    echo -e "$TESTS" >> "$RELEASE_FILE"
    echo "" >> "$RELEASE_FILE"
fi

if [ ! -z "$DOCS" ]; then
    echo "## 📚 Documentation" >> "$RELEASE_FILE"
    echo -e "$DOCS" >> "$RELEASE_FILE"
    echo "" >> "$RELEASE_FILE"
fi

if [ ! -z "$CHORES" ]; then
    echo "## 🔧 Other Changes" >> "$RELEASE_FILE"
    echo -e "$CHORES" >> "$RELEASE_FILE"
    echo "" >> "$RELEASE_FILE"
fi

# Adicionar instruções de instalação
cat >> "$RELEASE_FILE" << EOF
## 🚀 Installation

### Docker (Recommended)

\`\`\`bash
# Modo gratuito (embeddings locais)
docker run -p 8000:8000 \\
  -e REPO_URL="https://github.com/seu-usuario/seu-repo.git" \\
  -v ./data:/app/chroma_db \\
  flaviomagacho/mcp-git-server:$CURRENT_TAG
\`\`\`

### Docker com OpenAI (Pago)

\`\`\`bash
docker run -p 8000:8000 \\
  -e REPO_URL="https://github.com/seu-usuario/seu-repo.git" \\
  -e EMBEDDING_PROVIDER="openai" \\
  -e OPENAI_API_KEY="sk-sua-chave" \\
  -v ./data:/app/chroma_db \\
  flaviomagacho/mcp-git-server:$CURRENT_TAG
\`\`\`

## 📊 Summary

EOF

# Adicionar estatísticas
TOTAL_COMMITS=$(echo "$COMMITS" | wc -l)
CONTRIBUTORS=$(git log $PREVIOUS_TAG..$CURRENT_TAG --format='%an' | sort -u | wc -l)

echo "- **Total commits:** $TOTAL_COMMITS" >> "$RELEASE_FILE"
echo "- **Contributors:** $CONTRIBUTORS" >> "$RELEASE_FILE"
echo "" >> "$RELEASE_FILE"

# Adicionar informações técnicas
echo "## 🔧 Technical Details" >> "$RELEASE_FILE"
echo "" >> "$RELEASE_FILE"
echo "- **Docker Image:** \`flaviomagacho/mcp-git-server:$CURRENT_TAG\`" >> "$RELEASE_FILE"
echo "- **Base Image:** Python 3.12-slim" >> "$RELEASE_FILE"
echo "- **Default Embeddings:** Sentence Transformers (gratuito)" >> "$RELEASE_FILE"
echo "- **Supported Languages:** Python, Java, JavaScript, TypeScript, Markdown, HTML, CSS, JSON, PDF" >> "$RELEASE_FILE"

echo -e "${GREEN}✅ Release notes geradas: $RELEASE_FILE${NC}"

# Mostrar preview
echo -e "${BLUE}📖 Preview:${NC}"
echo "=================================="
head -n 20 "$RELEASE_FILE"
echo "..."
echo "=================================="

echo -e "${YELLOW}💡 Para usar este arquivo:${NC}"
echo "1. Revise o conteúdo em: $RELEASE_FILE"
echo "2. Copie para o GitHub Release ao criar a tag"
echo "3. Ou use o GitHub Actions que fará isso automaticamente"