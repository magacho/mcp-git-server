# 🤖 Automated Test Coverage Analysis

Este projeto usa análise automática de cobertura de testes para sugerir novos casos de teste.

## 📁 Arquivos

### Workflow GitHub Actions
`.github/workflows/test-coverage-check.yml`
- Executa automaticamente em PRs e pushes para main
- Gera relatórios de cobertura
- Comenta nos PRs com sugestões
- Cria issues para baixa cobertura

### Script de Análise
`.github/scripts/suggest_tests.py`
- Analisa código não coberto
- Identifica funções sem testes
- Gera templates de teste
- Calcula prioridades

## 🚀 Como Usar

### Executar Localmente
```bash
# 1. Gerar coverage
pytest --cov=. --cov-report=json

# 2. Analisar e gerar sugestões
python .github/scripts/suggest_tests.py

# 3. Ver arquivo gerado
cat suggested_tests.py
```

### Trigger Manual no GitHub
1. Acesse: Actions → Test Coverage Analysis & Suggestions
2. Clique: Run workflow
3. Escolha branch: main
4. Ver resultados na aba Actions

## 📊 Níveis de Prioridade

- 🔴 **HIGH**: Coverage < 30% ou funções complexas
- 🟡 **MEDIUM**: Coverage 30-70%
- 🟢 **LOW**: Coverage > 70%

## ⚙️ Configuração

### Limites de Cobertura
- **Alvo**: 80%
- **Warning**: < 70%
- **Crítico**: < 50% (bloqueia merge)

### Quando é Executado
- ✅ Pull Requests para main
- ✅ Push para main
- ✅ Manualmente (workflow_dispatch)

## 📝 Output Exemplo

```
🧪 Found 25 functions needing tests:

1. 🔴 HIGH document_loader.py::load_documents_robustly
   Coverage: 19.0% | Complexity: complex
   Template: [generated test code]

2. 🟡 MEDIUM auth.py::verify_api_key
   Coverage: 65.0%
```

## 🎯 Próximos Passos

1. Review `suggested_tests.py`
2. Copiar templates relevantes para arquivos de teste
3. Adaptar e completar implementação
4. Executar testes: `pytest`
5. Verificar cobertura: `pytest --cov=.`

## 📚 Recursos

- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Coverage.py](https://coverage.readthedocs.io/)
