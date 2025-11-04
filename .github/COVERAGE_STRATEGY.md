# 🎯 Estratégia de Cobertura de Testes

## Meta Ajustada: 70%

**Data:** 2025-11-04  
**Status:** Ativa

---

## 📊 Situação Atual:

### Coverage Atual: **31-33%**

### Breakdown por Arquivo:

| Arquivo | Coverage | Estratégia |
|---------|----------|------------|
| **models.py** | 100% | ✅ Manter |
| **embedding_config.py** | 89% | ✅ Manter |
| **repo_utils.py** | 77% | 🎯 Melhorar → 85% |
| **report_utils.py** | 59-76% | 🎯 Melhorar → 80% |
| **token_utils.py** | 60-83% | 🎯 Melhorar → 85% |
| **embedding_optimizer.py** | 33-38% | 🎯 Melhorar → 60% |
| **document_loader.py** | 22% | 🎯 Melhorar → 50% |
| **main.py** | 0% | ⏸️ Pular (deps pesadas) |
| **auth.py** | 0% | ⏸️ Pular (deps pesadas) |
| **logging_config.py** | 0% | ⏸️ Pular (deps pesadas) |

---

## 🎯 Plano para Chegar em 70%:

### Fase 1: Melhorar Arquivos Testáveis (31% → 50%)
**Foco:** document_loader.py, embedding_optimizer.py

**Ações:**
- Adicionar testes para funções não cobertas
- Melhorar testes existentes
- Adicionar edge cases

**Resultado Esperado:** +19% coverage

---

### Fase 2: Polir Arquivos Bons (50% → 70%)
**Foco:** repo_utils.py, token_utils.py, report_utils.py

**Ações:**
- Completar cobertura de funções parciais
- Adicionar testes de erro
- Cobrir branches não testados

**Resultado Esperado:** +20% coverage

---

### Fase 3: Manutenção (70%+)
**Foco:** Manter qualidade

**Ações:**
- Novos PRs devem incluir testes
- Coverage não pode cair abaixo de 70%
- Reviews focam em testes

---

## 📝 Arquivos a IGNORAR (por enquanto):

### Motivo: Dependências Pesadas

```python
# main.py - Requer:
- langchain_chroma
- sentence_transformers
- FastAPI runtime

# auth.py - Requer:
- Sistema de autenticação completo
- Integrações externas

# logging_config.py - Requer:
- structlog
- Configuração de logging complexa
```

**Decisão:** Testar quando dependências estiverem instaladas em CI/CD

---

## 🤖 Instruções para Auto-Test Agent:

### Prioridades:

1. **ALTA (focar aqui):**
   - document_loader.py (22% → 50%)
   - embedding_optimizer.py (33% → 60%)

2. **MÉDIA:**
   - repo_utils.py (77% → 85%)
   - token_utils.py (60% → 85%)
   - report_utils.py (59% → 80%)

3. **BAIXA (ignorar):**
   - main.py
   - auth.py
   - logging_config.py

### Configuração do Agent:

```bash
# Excluir arquivos problemáticos ao rodar
pytest --cov=. \
  --ignore=tests/unit/test_main_auto.py \
  --ignore=tests/unit/test_logging_config_auto.py \
  --cov-report=json

# Agent deve focar em:
TARGET_FILES="document_loader.py,embedding_optimizer.py,repo_utils.py,token_utils.py,report_utils.py"
```

---

## 📈 Roadmap de Coverage:

```
╔════════════════════════════════════════╗
║  Roadmap para 70%                      ║
╠════════════════════════════════════════╣
║  Atual:      31% ████░░░░░░░░░░░░░░░  ║
║  Iteração 3: 50% ██████████░░░░░░░░░  ║
║  Iteração 4: 70% ██████████████░░░░░  ║
║  Meta:       70% ██████████████░░░░░  ║
╚════════════════════════════════════════╝
```

### Timeline:
```
✅ Iteração 1: 26% → 33% (+7%)
✅ Iteração 2: 33% → 31% (-2%, ajuste)
🔄 Iteração 3: 31% → 50% (+19%, focar em document_loader + optimizer)
🔄 Iteração 4: 50% → 70% (+20%, polir repo_utils + token_utils)
✅ Meta atingida: 70%
```

---

## 🚀 Como Executar:

### Iteração 3 (próxima):
```bash
# Gerar testes focados
./run_auto_test_agent.sh

# Ou manualmente especificar foco
python3 .github/scripts/auto_generate_tests.py \
  --focus document_loader,embedding_optimizer

# Rodar testes
pytest --cov=. \
  --ignore=tests/unit/test_main_auto.py \
  --ignore=tests/unit/test_logging_config_auto.py
```

---

## 📊 Métricas de Sucesso:

### Para Considerar Iteração Bem-Sucedida:

- ✅ Coverage aumentou (mínimo +5%)
- ✅ Nenhum teste existente quebrou
- ✅ Todos novos testes passam
- ✅ Focou em arquivos prioritários

### Para Atingir Meta de 70%:

- ✅ document_loader.py ≥ 50%
- ✅ embedding_optimizer.py ≥ 60%
- ✅ repo_utils.py ≥ 85%
- ✅ token_utils.py ≥ 85%
- ✅ report_utils.py ≥ 80%
- ✅ Coverage total ≥ 70%

---

## 🔄 Revisão:

**Revisar esta estratégia:**
- ✅ Após cada iteração
- ✅ Se coverage não aumentar
- ✅ Se novos arquivos forem adicionados
- ✅ Quando atingir 70%

**Última atualização:** 2025-11-04  
**Próxima revisão:** Após Iteração 3

