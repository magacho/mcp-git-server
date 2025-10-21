# 🗺️ Roadmap - MCP Git Server

Este documento contém o planejamento de funcionalidades futuras para o projeto. As funcionalidades estão organizadas por prioridade e complexidade.

---

## 🔥 Alta Prioridade

### 1. Suporte a Repositórios Privados do GitHub
**Status:** 📋 Planejado  
**Complexidade:** Média  
**Descrição:**  
Adicionar autenticação para clonar e indexar repositórios privados do GitHub.

**Implementação sugerida:**
- Suporte a Personal Access Token (PAT) via variável de ambiente `GITHUB_TOKEN`
- Suporte a SSH keys montadas no container
- Suporte a GitHub App authentication para organizações
- Validação de permissões antes de clonar

**Variáveis de ambiente:**
```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
REPO_URL=https://github.com/empresa/repo-privado.git
```

**Benefícios:**
- Permite uso em projetos corporativos
- Maior segurança no acesso aos repositórios
- Integração com CI/CD privado

---

### 2. Detecção e Atualização Automática de Código
**Status:** 📋 Planejado  
**Complexidade:** Alta  
**Descrição:**  
Implementar sistema de verificação de atualizações no repositório e re-indexação incremental.

**Funcionalidades:**
- **Polling periódico:** Verificar commits novos a cada X minutos
- **Webhook listener:** Receber notificações do GitHub quando houver push
- **Re-indexação inteligente:** Processar apenas arquivos modificados
- **Versionamento:** Manter histórico de versões indexadas
- **Endpoint de status:** `/status` mostrando última atualização

**Implementação sugerida:**
```python
# Novo endpoint
POST /refresh
{
  "force": false  # true = re-indexa tudo, false = apenas novos commits
}

# Resposta
{
  "status": "updated",
  "previous_commit": "abc123",
  "current_commit": "def456",
  "files_updated": 15,
  "files_added": 3,
  "files_removed": 1
}
```

**Estratégias de atualização:**
1. **Incremental:** Git pull + processar apenas diffs
2. **Snapshot:** Comparar hash dos arquivos
3. **Timestamp:** Re-indexar arquivos modificados após última indexação

**Benefícios:**
- Mantém índice sempre atualizado
- Economiza tokens (não reprocessa tudo)
- Reduz tempo de atualização

---

## 🚀 Média Prioridade

### 3. Autenticação e Autorização da API
**Status:** 📋 Planejado  
**Complexidade:** Média  
**Descrição:**  
Proteger endpoints com autenticação para evitar uso não autorizado.

**Opções:**
- API Key via header `X-API-Key`
- JWT tokens
- OAuth2 para integração com GitHub
- Rate limiting por usuário/API key

**Exemplo:**
```bash
curl -X POST "http://localhost:8000/retrieve" \
  -H "X-API-Key: seu-token-secreto" \
  -H "Content-Type: application/json" \
  -d '{"query": "Como funciona autenticação?"}'
```

---

### 4. Suporte a Múltiplos Repositórios
**Status:** 💡 Ideia  
**Complexidade:** Alta  
**Descrição:**  
Permitir indexar e consultar múltiplos repositórios simultaneamente.

**Endpoints propostos:**
```python
POST /repositories
{
  "name": "meu-projeto",
  "url": "https://github.com/user/repo.git",
  "branch": "main"
}

GET /repositories
# Lista todos os repositórios indexados

POST /retrieve
{
  "query": "Como fazer autenticação?",
  "repositories": ["meu-projeto", "outro-projeto"],  # opcional
  "top_k": 5
}

DELETE /repositories/{name}
# Remove repositório indexado
```

**Benefícios:**
- Buscar em múltiplas bases de código
- Comparar implementações entre projetos
- Centralizar conhecimento de organização

---

### 5. Cache de Queries Frequentes
**Status:** 💡 Ideia  
**Complexidade:** Baixa  
**Descrição:**  
Implementar cache Redis/in-memory para queries repetidas.

**Implementação:**
- Cache de resultados por hash da query
- TTL configurável (ex: 1 hora)
- Invalidação ao atualizar repositório
- Estatísticas de cache hit/miss

**Benefícios:**
- Reduz custos de embedding
- Resposta mais rápida
- Menor carga na API da OpenAI

---

## 🔮 Baixa Prioridade / Futuro

### 6. Interface Web (UI)
**Status:** 💡 Ideia  
**Complexidade:** Média  
**Descrição:**  
Dashboard web para gerenciar repositórios e fazer buscas.

**Funcionalidades:**
- Visualizar repositórios indexados
- Fazer buscas interativas
- Ver estatísticas de uso
- Configurar webhooks
- Logs em tempo real

---

### 7. Suporte a Outros Provedores de Embedding
**Status:** 💡 Ideia  
**Complexidade:** Média  
**Descrição:**  
Permitir usar embeddings alternativos além da OpenAI.

**Opções:**
- Cohere
- HuggingFace (modelos open-source)
- Anthropic
- Embeddings locais (sentence-transformers)

**Benefícios:**
- Redução de custos
- Privacidade (modelos locais)
- Flexibilidade

---

### 8. Filtros Avançados de Busca
**Status:** 💡 Ideia  
**Complexidade:** Baixa  
**Descrição:**  
Adicionar filtros para refinar resultados.

**Exemplos:**
```json
{
  "query": "função de autenticação",
  "top_k": 5,
  "filters": {
    "file_extensions": [".py", ".js"],
    "exclude_paths": ["tests/", "node_modules/"],
    "max_file_size": 50000,
    "languages": ["python", "javascript"]
  }
}
```

---

### 9. Análise de Código e Métricas
**Status:** 💡 Ideia  
**Complexidade:** Alta  
**Descrição:**  
Gerar insights sobre o repositório indexado.

**Métricas:**
- Linguagens mais usadas
- Arquivos mais referenciados em buscas
- Complexidade de código
- Documentação coverage
- Dependências e imports

---

### 10. Exportação e Backup
**Status:** 💡 Ideia  
**Complexidade:** Baixa  
**Descrição:**  
Permitir exportar índice vetorial e fazer backups.

**Funcionalidades:**
```bash
GET /export/{repository_name}
# Retorna arquivo .tar.gz com ChromaDB

POST /import
# Importa índice pré-processado
```

**Benefícios:**
- Migração entre ambientes
- Disaster recovery
- Compartilhar índices processados

---

## 🛠️ Melhorias Técnicas

### 11. Observabilidade e Monitoramento
**Status:** 📋 Planejado  
**Complexidade:** Média  

**Implementar:**
- Métricas Prometheus (`/metrics`)
- Health checks (`/health`, `/ready`)
- Structured logging (JSON)
- Tracing distribuído (OpenTelemetry)
- Alertas para falhas

---

### 12. Testes Automatizados
**Status:** 📋 Planejado  
**Complexidade:** Média  

**Cobertura:**
- Testes unitários (pytest)
- Testes de integração
- Testes de carga (locust)
- CI/CD com GitHub Actions

---

### 13. Otimização de Performance
**Status:** 💡 Ideia  
**Complexidade:** Variável  

**Melhorias:**
- Chunking adaptativo por tipo de arquivo
- Compressão de embeddings
- Índice HNSW para busca mais rápida
- Lazy loading de documentos grandes
- Paralelização de queries

---

## 📊 Legenda de Status

- 📋 **Planejado** - Funcionalidade definida, pronta para implementação
- 💡 **Ideia** - Conceito inicial, precisa de refinamento
- 🚧 **Em Desenvolvimento** - Implementação em andamento
- ✅ **Concluído** - Funcionalidade implementada e testada
- ⏸️ **Pausado** - Desenvolvimento temporariamente suspenso
- ❌ **Cancelado** - Funcionalidade descartada

---

## ✅ Concluído

### v0.1.0 - Release Estável com Embeddings Locais 🎉
- ✅ **Embeddings locais por padrão** - Funciona sem chaves de API
- ✅ **Configuração simplificada** - Um único container via docker run
- ✅ **Suporte flexível** - Local (gratuito) ou OpenAI (pago)
- ✅ **Endpoints de monitoramento** - /health, /embedding-info
- ✅ **Estimativa de custos** em tempo real
- ✅ **Documentação completa** - Guias claros de uso
- ✅ **Arquitetura limpa** - Sem docker-compose, apenas Dockerfile

### v0.0.25 - Embeddings Locais e Otimizações
- ✅ Suporte a embeddings locais (Sentence Transformers, HuggingFace)
- ✅ Sistema flexível de provedores de embedding
- ✅ Contagem de tokens otimizada (local vs tiktoken)
- ✅ Estimativa de custos para diferentes provedores
- ✅ Modernização para FastAPI com lifespan context manager
- ✅ Docker otimizado com usuário não-root

### v0.0.24 - Otimização de Rate Limiting
- ✅ Implementado controle de tokens por minuto (TPM)
- ✅ Melhorado sistema de batching para respeitar limites da API
- ✅ Logs mais informativos sobre o progresso do processamento

### v0.0.23 - Controle de Rate Limiting  
- ✅ Adicionado limite de tokens para evitar exceder quotas da OpenAI
- ✅ Sistema de batching inteligente para processamento de documentos
- ✅ Monitoramento de uso de tokens em tempo real

---

## 🤝 Como Contribuir

Se você quer implementar alguma dessas funcionalidades:

1. Abra uma issue no GitHub referenciando este roadmap
2. Discuta a abordagem antes de começar
3. Faça um fork e crie uma branch
4. Submeta um PR com testes

---

**Última atualização:** Outubro 2025  
**Mantenedor:** @magacho
