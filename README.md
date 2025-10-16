# Servidor de Recuperação de Contexto para Repositórios Git (MCP Server)

Este projeto fornece um servidor de API autocontido em Docker que clona um repositório Git público, o indexa usando modelos de embedding da OpenAI e expõe um endpoint para buscar trechos de código e documentação relevantes para uma pergunta em linguagem natural.

É a peça de "Recuperação" (Retrieval) para um sistema de RAG (Retrieval-Augmented Generation), projetada para alimentar um agente de IA externo (como um workflow no n8n) com o contexto necessário para responder perguntas sobre uma base de código.

### ✨ Funcionalidades

-   **Embeddings Flexíveis:** Suporte a embeddings locais gratuitos (Sentence Transformers) ou OpenAI (pago)
-   **Configuração Zero:** Funciona sem chaves de API - embeddings locais por padrão
-   **Configurável via Variáveis de Ambiente:** Aponte para qualquer repositório Git público sem alterar o código
-   **Cache Persistente:** O banco de dados vetorial é criado na primeira execução e reutilizado
-   **API Simples:** Endpoints REST para busca e monitoramento
-   **Pronto para Produção:** Container Docker otimizado com usuário não-root
-   **Estimativa de Custos:** Mostra custos estimados para diferentes provedores

### 🚀 Como Usar

#### Pré-requisitos

1.  **Docker** instalado e em execução na sua máquina.
2.  Uma **API Key da OpenAI**. Você pode obter uma em [platform.openai.com/api-keys](https://platform.openai.com/api-keys).

#### Executando com Docker

**Modo Gratuito (Padrão - Embeddings Locais):**
```bash
docker run -p 8000:8000 \
  -e REPO_URL="https://github.com/n8n-io/n8n.git" \
  -e REPO_BRANCH="master" \
  -v ./mcp_data/chroma_db:/app/chroma_db \
  --name mcp-server \
  flaviomagacho/mcp-git-server:latest
```

**Modo OpenAI (Pago - Alta Qualidade):**
```bash
docker run -p 8000:8000 \
  -e REPO_URL="https://github.com/n8n-io/n8n.git" \
  -e REPO_BRANCH="master" \
  -e EMBEDDING_PROVIDER="openai" \
  -e OPENAI_API_KEY="SUA_CHAVE_API_SEGURA" \
  -v ./mcp_data/chroma_db:/app/chroma_db \
  --name mcp-server \
  flaviomagacho/mcp-git-server:latest
```

#### Build e Teste Local

```bash
# Clone e build
git clone https://github.com/magacho/mcp-git-server.git
cd mcp-git-server
docker build -t mcp-git-server .

# Teste com repositório pequeno
docker run -p 8000:8000 \
  -e REPO_URL="https://github.com/octocat/Hello-World.git" \
  -e REPO_BRANCH="master" \
  mcp-git-server

# Verificar status (em outro terminal)
curl http://localhost:8000/health

# Usar com seu repositório
docker run -p 8000:8000 \
  -e REPO_URL="https://github.com/seu-usuario/seu-repo.git" \
  -e REPO_BRANCH="main" \
  -v ./data/chroma_db:/app/chroma_db \
  mcp-git-server
```


### 🔧 Configuração (Variáveis de Ambiente)

#### Obrigatórias
-   `REPO_URL` (obrigatório): A URL `.git` do repositório público a ser indexado.

#### Opcionais - Repositório
-   `REPO_BRANCH`: A branch que será clonada para o MCP Server (padrão: `main`)

#### Opcionais - Embeddings
-   `EMBEDDING_PROVIDER`: Provedor de embeddings (padrão: `sentence-transformers`)
  - `sentence-transformers` - Gratuito, boa qualidade
  - `huggingface` - Gratuito, boa qualidade  
  - `openai` - Pago, alta qualidade
-   `OPENAI_API_KEY`: Chave da API OpenAI (necessária apenas para `openai`)
-   `ST_EMBEDDING_MODEL`: Modelo Sentence Transformers (padrão: `all-MiniLM-L6-v2`)
-   `HF_EMBEDDING_MODEL`: Modelo HuggingFace (padrão: `sentence-transformers/all-MiniLM-L6-v2`)
-   `TOKEN_COUNT_METHOD`: Método de contagem (padrão: `local`)

### 🤖 Provedores de Embedding

#### Sentence Transformers (Padrão - Gratuito) ⭐
- **Qualidade**: Boa
- **Custo**: Gratuito
- **Velocidade**: Média (processamento local)
- **Configuração**: Automática, sem chaves necessárias
- **Recomendado para**: Uso geral, desenvolvimento, testes

#### HuggingFace (Gratuito)
- **Qualidade**: Boa
- **Custo**: Gratuito
- **Velocidade**: Média (processamento local)
- **Configuração**: Automática, sem chaves necessárias
- **Recomendado para**: Modelos específicos, multilíngue

#### OpenAI (Pago)
- **Qualidade**: Alta
- **Custo**: ~$0.0001 por 1K tokens
- **Velocidade**: Rápida (API)
- **Configuração**: Requer `OPENAI_API_KEY`
- **Recomendado para**: Produção com alta qualidade

### � Início  Rápido (Gratuito)

O servidor agora usa **embeddings locais por padrão** - sem necessidade de chaves de API!

```bash
# Modo padrão - completamente gratuito
docker run -p 8000:8000 \
  -e REPO_URL="https://github.com/n8n-io/n8n.git" \
  -v ./mcp_data/chroma_db:/app/chroma_db \
  flaviomagacho/mcp-git-server:latest
```

Acesse: `http://localhost:8000` para verificar o status.

### 🔌 Endpoints da API

**`GET /`** - Status do servidor
**`GET /health`** - Health check
**`GET /embedding-info`** - Informações sobre configuração de embeddings

**`POST /retrieve`** - Busca por fragmentos de contexto relevantes

**Corpo da Requisição (JSON):**
```json
{
  "query": "Sua pergunta sobre o código aqui",
  "top_k": 5
}
```

**Exemplo com `curl`:**
```bash
curl -X POST "http://localhost:8000/retrieve" \
-H "Content-Type: application/json" \
-d '{"query": "Como o n8n gerencia credenciais?", "top_k": 3}'
```

**Verificar configuração:**
```bash
curl http://localhost:8000/embedding-info
```

---

### 🗺️ Roadmap

Confira o [ROADMAP.md](ROADMAP.md) para ver as funcionalidades planejadas.

---

*Este projeto foi criado em [10 de Outubro de 2025].*

