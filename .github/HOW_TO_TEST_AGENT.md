# 🧪 Como Testar o Auto-Test Agent

## 📋 Problema Atual

O workflow `auto-generate-tests.yml` não pode criar PRs automaticamente porque o GitHub Actions não tem permissão com o token padrão.

## ✅ Solução: 3 Opções

---

### **Opção 1: Script Local (Recomendado)** ⭐

```bash
# Executa o agent localmente e cria branch
./run_auto_test_agent.sh

# Depois cria o PR
gh pr create --base main --head auto-tests-XXXXXXXX \
  --title "🤖 Auto-generated tests to improve coverage" \
  --body "Generated tests to address #1"
```

---

### **Opção 2: Manual Step-by-Step**

```bash
# 1. Gerar coverage
pytest --cov=. --cov-report=json

# 2. Gerar testes
python3 .github/scripts/auto_generate_tests.py

# 3. Ver testes gerados
ls tests/unit/test_*_auto.py

# 4. Rodar testes
pytest tests/unit/test_*_auto.py -v

# 5. Ver coverage
pytest --cov=. --cov-report=term-missing

# 6. Criar branch e commit
git checkout -b auto-tests-manual
git add tests/unit/test_*_auto.py test_generation_summary.md
git commit -m "test: auto-generated tests"
git push origin auto-tests-manual

# 7. Criar PR
gh pr create
```

---

### **Opção 3: Workflow Trigger Manual**

O workflow já existe e pode ser executado manualmente:

```bash
# Via GitHub CLI (ainda não funciona totalmente)
gh workflow run auto-generate-tests.yml -f issue_number=1

# Ou via UI:
# 1. Acesse: https://github.com/magacho/mcp-git-server/actions
# 2. Clique: "Auto-Generate Tests from Coverage Issues"  
# 3. Clique: "Run workflow"
# 4. Preencha: issue_number = 1
# 5. Clique: "Run workflow"
# 6. Aguarde execução
# 7. Veja a branch criada nos comentários da issue
# 8. Crie o PR manualmente
```

---

## 🎯 Resultado Esperado

Qualquer opção vai:
1. ✅ Analisar código não coberto
2. ✅ Gerar 20+ testes inteligentes
3. ✅ Criar arquivos em `tests/unit/test_*_auto.py`
4. ✅ Criar/atualizar branch
5. 📋 Você cria o PR manualmente

---

## 📊 Verificar Resultado

```bash
# Ver testes gerados
ls -la tests/unit/test_*_auto.py

# Contar testes
grep -r "^def test_" tests/unit/test_*_auto.py | wc -l

# Rodar testes específicos
pytest tests/unit/test_document_loader_auto.py -v

# Ver cobertura aumentada
pytest --cov=. --cov-report=term-missing
```

---

## 🐛 Troubleshooting

### Testes já existem
Se os testes já foram gerados em commit anterior:

```bash
# Ver testes existentes
git log --oneline --all --grep="auto-generate"

# Ver na branch específica
git show HEAD:tests/unit/test_main_auto.py
```

### Workflow não roda automaticamente
Isso é esperado! O workflow precisa:
- Issue criada DEPOIS do workflow existir, ou
- Label adicionado/removido manualmente, ou  
- Trigger manual via Actions UI

### Dependências faltando
```bash
# Instalar todas dependências
pip install -r requirements.txt

# Ou específicas
pip install structlog langchain-chroma
```

---

## 🎊 Quick Start (1 minuto)

```bash
# Opção mais rápida
./run_auto_test_agent.sh

# Quando terminar, copie o link do PR ou rode:
gh pr create --fill
```

---

## 📝 Nota

Os testes foram gerados e commitados no commit `8595905`.  
Para testar novamente:

1. Apague os arquivos `test_*_auto.py`
2. Rode o script `./run_auto_test_agent.sh`
3. Veja os testes sendo gerados novamente
