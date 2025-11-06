# Reestruturação dos GitHub Actions Workflows

## 📋 Resumo

Reestruturação completa dos workflows do GitHub Actions para melhor organização e controle de qualidade.

## 🎯 Estrutura Criada

### 1. **Testes Automaticos** (`testes-automaticos.yml`)
- **Quando roda**: A cada commit (push/PR) na branch `main`
- **O que faz**:
  - Executa todos os testes unitários
  - Valida a integridade do código
- **Em caso de falha**:
  - Cria issue com label `autotest-failure`
  - Bloqueia execução dos workflows de tag

### 2. **Cobertura de Testes** (`cobertura-testes.yml`)
- **Quando roda**: A cada commit (push/PR) na branch `main`
- **O que faz**:
  - Executa testes com análise de cobertura
  - Gera relatórios HTML, XML e JSON
  - Valida se cobertura está >= 60%
- **Em caso de falha**:
  - Cria issue com label `test-coverage`
  - Comenta no PR com detalhes da cobertura
  - Faz upload dos relatórios para Codecov
  - Bloqueia execução dos workflows de tag

### 3. **Testes de Vulnerabilidades e Seguranca** (`vulnerabilidades-seguranca.yml`)
- **Quando roda**: Somente quando uma tag `v*.*.*` é criada ou manualmente
- **O que faz**:
  - Executa Bandit (análise de código)
  - Executa Safety (vulnerabilidades em dependências)
  - Executa pip-audit (auditoria de dependências)
  - Gera relatórios em JSON
- **Em caso de problemas**:
  - Cria issue com label `security-vulnerability`
  - Upload dos relatórios como artifacts

### 4. **Publicacao da Imagem Docker** (`publicacao-docker.yml`)
- **Quando roda**: Somente quando uma tag `v*.*.*` é criada ou manualmente
- **Pré-requisitos**:
  - Verifica se "Testes Automaticos" passou
  - Verifica se "Cobertura de Testes" passou
  - **NÃO executa se algum teste falhou**
- **O que faz**:
  - Build da imagem Docker
  - Push para Docker Hub com múltiplas tags (version, major.minor, major, latest)
  - Atualiza descrição no Docker Hub
  - Usa cache para otimizar builds

## 🔄 Fluxo de Execução

```
┌─────────────────────────────────────────┐
│         Push/PR na main                 │
└────────────┬────────────────────────────┘
             │
             ├─► Testes Automaticos (paralelo)
             │   └─► ❌ Falhou → Cria issue
             │   └─► ✅ Passou
             │
             └─► Cobertura de Testes (paralelo)
                 └─► ❌ < 60% → Cria issue
                 └─► ✅ >= 60%

┌─────────────────────────────────────────┐
│       Criação de Tag v*.*.*             │
└────────────┬────────────────────────────┘
             │
             ├─► Vulnerabilidades e Seguranca
             │   └─► Detectou problemas → Cria issue
             │   └─► Sem problemas críticos
             │
             └─► Publicacao Docker
                 ├─► Verifica se testes passaram
                 ├─► ❌ Testes falharam → CANCELA
                 └─► ✅ Tudo OK → Publica imagem
```

## 🏷️ Labels Utilizadas

- `autotest-failure`: Falha nos testes automáticos
- `test-coverage`: Cobertura abaixo de 60%
- `security-vulnerability`: Vulnerabilidades detectadas
- `bug`: Bug identificado
- `tech-debt`: Débito técnico
- `priority-high`: Alta prioridade
- `priority-critical`: Prioridade crítica

## 📊 Métricas e Relatórios

### Cobertura de Testes
- **Mínimo aceitável**: 60%
- **Relatórios gerados**:
  - HTML interativo (htmlcov/)
  - XML para Codecov
  - JSON para análise programática
- **Comentários automáticos em PRs**

### Segurança
- **Ferramentas**:
  - Bandit: Análise estática de segurança
  - Safety: Vulnerabilidades conhecidas
  - pip-audit: Auditoria de dependências
- **Relatórios em JSON** disponíveis como artifacts

## 🔧 Secrets Necessários

Certifique-se de ter os seguintes secrets configurados no repositório:

- `DOCKERHUB_USERNAME`: Usuário do Docker Hub
- `DOCKERHUB_TOKEN`: Token de acesso ao Docker Hub

## 📝 Arquivos Removidos

Os seguintes workflows antigos foram removidos:
- `test.yml`
- `test-coverage-check.yml`
- `publicar-docker.yml`

## 🎯 Benefícios da Nova Estrutura

1. **Clareza**: Cada workflow tem uma responsabilidade única
2. **Segurança**: Validações antes de publicar
3. **Rastreabilidade**: Issues automáticas para problemas
4. **Eficiência**: Workflows paralelos quando possível
5. **Feedback rápido**: Comentários em PRs
6. **Proteção**: Publicação Docker bloqueada se testes falharem

## 🚀 Próximos Passos

1. Fazer commit dos novos workflows
2. Testar criando um PR
3. Validar a criação de issues automáticas
4. Criar uma tag de teste para validar o fluxo completo
5. Verificar publicação no Docker Hub

## 📖 Como Usar

### Para desenvolvedores:
- Commits normais: Executam testes e cobertura automaticamente
- Issues serão criadas automaticamente se houver problemas
- PRs receberão comentários com relatório de cobertura

### Para releases:
1. Certifique-se de que todos os testes estão passando
2. Crie uma tag: `git tag v1.0.0`
3. Push da tag: `git push origin v1.0.0`
4. Aguarde a execução dos workflows
5. Imagem Docker será publicada automaticamente

## ⚠️ Importante

- Testes devem passar para publicar no Docker
- Cobertura mínima de 60% é obrigatória
- Issues automáticas devem ser revisadas e fechadas após correção
