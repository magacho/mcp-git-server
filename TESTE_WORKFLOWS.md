# Plano de Testes - Workflows GitHub Actions

## 🧪 Estratégia de Testes

### Fase 1: Validação Local ✅ (CONCLUÍDA)
- [x] Validação de sintaxe YAML
- [x] Verificação de estrutura dos arquivos

### Fase 2: Commit e Push dos Workflows
```bash
# 1. Adicionar os novos workflows
git add .github/workflows/testes-automaticos.yml
git add .github/workflows/cobertura-testes.yml
git add .github/workflows/vulnerabilidades-seguranca.yml
git add .github/workflows/publicacao-docker.yml
git add WORKFLOWS_STRUCTURE.md

# 2. Remover workflows antigos
git rm .github/workflows/test.yml
git rm .github/workflows/test-coverage-check.yml
git rm .github/workflows/publicar-docker.yml

# 3. Fazer commit
git commit -m "feat: reestruturação completa dos workflows

- Adiciona workflow de Testes Automaticos
- Adiciona workflow de Cobertura de Testes (min 60%)
- Adiciona workflow de Vulnerabilidades e Segurança (tags)
- Adiciona workflow de Publicação Docker (tags + validação)
- Remove workflows antigos duplicados
- Adiciona documentação completa em WORKFLOWS_STRUCTURE.md

Os novos workflows seguem a estrutura:
- Testes a cada commit (testes + cobertura)
- Segurança e Docker apenas em tags
- Issues automáticas para falhas
- Bloqueio de publicação se testes falharem"

# 4. Push para main
git push origin main
```

### Fase 3: Testar Workflows de Commit (AUTOMÁTICO)
Ao fazer o push acima, dois workflows serão executados automaticamente:

**✅ Testes que devem rodar:**
1. `Testes Automaticos` - Deve executar todos os testes
2. `Cobertura de Testes` - Deve verificar a cobertura

**🔍 O que observar:**
- Acesse: https://github.com/SEU_USUARIO/mcp-git-server/actions
- Verifique se ambos workflows iniciaram
- Aguarde conclusão (2-3 minutos)
- Verifique se passou ou falhou

**📊 Cenários possíveis:**
- ✅ **Ambos passam**: Ótimo! Workflows funcionando
- ❌ **Testes falham**: Issue será criada automaticamente
- ⚠️ **Cobertura < 60%**: Issue será criada + workflow falha

### Fase 4: Testar PR com Comentários

```bash
# 1. Criar branch de teste
git checkout -b test/workflow-pr

# 2. Fazer uma mudança simples (para testar comentário)
echo "# Test" >> README.md
git add README.md
git commit -m "test: validar comentário de cobertura em PR"

# 3. Push da branch
git push origin test/workflow-pr

# 4. Criar PR via GitHub
# https://github.com/SEU_USUARIO/mcp-git-server/compare/main...test/workflow-pr
```

**🔍 O que observar:**
- O PR deve receber um comentário automático com relatório de cobertura
- O comentário deve mostrar: percentual, status, link para relatório
- Workflows devem aparecer como checks no PR

### Fase 5: Testar Workflows de Tag

```bash
# 1. Voltar para main
git checkout main
git pull origin main

# 2. Criar tag de teste
git tag v0.0.1-test -m "Test: validar workflows de tag"

# 3. Push da tag
git push origin v0.0.1-test
```

**✅ Workflows que devem rodar:**
1. `Vulnerabilidades e Seguranca` - Análise de segurança
2. `Publicacao Docker` - **Apenas se testes passaram**

**🔍 O que observar:**
- Acesse: https://github.com/SEU_USUARIO/mcp-git-server/actions
- Workflow de segurança deve iniciar
- Workflow de Docker deve:
  - ✅ Iniciar se testes passaram anteriormente
  - ❌ Ser cancelado se testes falharam

**📊 Validações importantes:**
- [ ] Job "Verificar Pré-requisitos" deve consultar workflows anteriores
- [ ] Se algum teste falhou, Docker não deve publicar
- [ ] Se tudo passou, imagem deve ser publicada no Docker Hub

### Fase 6: Testar Criação de Issues

**Cenário 1: Forçar falha nos testes**
```bash
# 1. Criar branch
git checkout -b test/force-test-failure

# 2. Adicionar teste que falha (temporário)
cat > test_failure.py << 'EOF'
def test_that_fails():
    assert False, "Teste forçado a falhar"
EOF

git add test_failure.py
git commit -m "test: forçar falha para validar issue"
git push origin test/force-test-failure

# Fazer merge na main (ou push direto se preferir)
```

**🔍 O que observar:**
- Issue deve ser criada automaticamente
- Label: `autotest-failure`
- Título: "🔴 Falha nos Testes Automáticos"
- Corpo deve conter: commit, branch, link do workflow

**Cenário 2: Forçar cobertura baixa**
```bash
# 1. Criar arquivo sem testes
cat > uncovered_code.py << 'EOF'
def nova_funcao_sem_testes():
    # Muitas linhas de código
    for i in range(100):
        x = i * 2
        y = x + 3
    return x + y
EOF

git add uncovered_code.py
git commit -m "test: adicionar código sem testes para validar cobertura"
git push origin main
```

**🔍 O que observar:**
- Se cobertura cair abaixo de 60%
- Issue deve ser criada automaticamente
- Label: `test-coverage`
- Título: "🔴 Cobertura de Testes Abaixo de 60%"

### Fase 7: Testar Bloqueio de Publicação

**Objetivo:** Garantir que Docker não publica se testes falharem

```bash
# Com testes falhando (da Fase 6):

# 1. Criar tag
git tag v0.0.2-test-block
git push origin v0.0.2-test-block

# 2. Observar workflow de Docker
```

**✅ Resultado esperado:**
- Job "Verificar Pré-requisitos" deve FALHAR
- Job "Build e Push Docker" NÃO deve executar
- Mensagem: "Testes ou cobertura falharam. Publicação do Docker cancelada."

### Fase 8: Validação Completa

**Após corrigir os testes:**
```bash
# 1. Remover código de teste
git rm test_failure.py uncovered_code.py
git commit -m "test: remover códigos de teste"
git push origin main

# 2. Aguardar testes passarem

# 3. Criar tag final
git tag v0.0.3-test-success
git push origin v0.0.3-test-success

# 4. Verificar publicação no Docker Hub
```

**✅ Validação final:**
- [ ] Testes passaram
- [ ] Cobertura >= 60%
- [ ] Docker foi publicado
- [ ] Tags corretas no Docker Hub
- [ ] Descrição atualizada no Docker Hub

## 📋 Checklist de Validação

### Workflows de Commit
- [ ] Testes Automaticos executa
- [ ] Cobertura de Testes executa
- [ ] Issues criadas em falhas
- [ ] Comentários em PRs funcionam

### Workflows de Tag
- [ ] Vulnerabilidades executa em tag
- [ ] Docker verifica pré-requisitos
- [ ] Docker bloqueia se testes falharam
- [ ] Docker publica se tudo OK

### Issues Automáticas
- [ ] autotest-failure criada corretamente
- [ ] test-coverage criada corretamente
- [ ] security-vulnerability criada se necessário
- [ ] Labels corretas aplicadas

### Publicação Docker
- [ ] Build e push funcionam
- [ ] Tags semver corretas
- [ ] Cache funcionando
- [ ] Descrição atualizada

## 🚨 Troubleshooting

### Workflow não iniciou
```bash
# Verificar sintaxe
cd .github/workflows
for f in *.yml; do yamllint $f; done
```

### Job falhou inesperadamente
- Verificar logs no GitHub Actions
- Verificar secrets (DOCKERHUB_USERNAME, DOCKERHUB_TOKEN)
- Verificar permissões do workflow

### Issue não foi criada
- Verificar se workflow tem permission: `issues: write`
- Verificar se já existe issue aberta com mesma label
- Verificar logs do step de criação de issue

### Docker não publica
- Verificar se testes passaram anteriormente
- Verificar job "Verificar Pré-requisitos"
- Verificar secrets do Docker Hub
- Verificar se tag segue padrão v*.*.*

## 📞 Comandos Úteis

```bash
# Ver workflows remotos
gh workflow list

# Ver runs de um workflow
gh run list --workflow="Testes Automaticos"

# Ver detalhes de um run
gh run view <run-id>

# Ver logs de um run
gh run view <run-id> --log

# Listar issues
gh issue list --label autotest-failure

# Deletar tag (se necessário)
git tag -d v0.0.1-test
git push origin :refs/tags/v0.0.1-test
```

## ⏱️ Tempo Estimado

- Fase 2-3: 5 minutos
- Fase 4: 5 minutos  
- Fase 5: 10 minutos
- Fase 6: 15 minutos
- Fase 7: 10 minutos
- Fase 8: 10 minutos

**Total: ~55 minutos** para testes completos

## 🎯 Teste Rápido (15 minutos)

Se quiser testar rapidamente:

```bash
# 1. Commit dos workflows
git add .github/workflows/*.yml WORKFLOWS_STRUCTURE.md
git rm .github/workflows/test*.yml .github/workflows/publicar-docker.yml
git commit -m "feat: reestruturação dos workflows"
git push origin main

# 2. Aguardar conclusão (3-5 min)

# 3. Criar tag de teste
git tag v0.0.1-test
git push origin v0.0.1-test

# 4. Observar resultados
```

Acesse: https://github.com/SEU_USUARIO/mcp-git-server/actions

✅ Se tudo estiver verde, está funcionando!
