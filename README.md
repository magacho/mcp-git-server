# Servidor de Recuperação de Contexto para Repositórios Git (MCP Server)

Este projeto fornece um servidor de API autocontido em Docker que clona um repositório Git público, o indexa usando modelos de embedding da OpenAI e expõe um endpoint para buscar trechos de código e documentação relevantes para uma pergunta em linguagem natural.

É a peça de "Recuperação" (Retrieval) para um sistema de RAG (Retrieval-Augmented Generation), projetada para alimentar um agente de IA externo (como um workflow no n8n) com o contexto necessário para responder perguntas sobre uma base de código.

### ✨ Funcionalidades

-   **Configurável via Variáveis de Ambiente:** Aponte para qualquer repositório Git público sem alterar o código.
-   **Backend de Embeddings da OpenAI:** Usa os modelos de embedding da OpenAI para uma compreensão semântica de alta qualidade.
-   **Cache Persistente:** O banco de dados vetorial é criado na primeira execução e reutilizado, economizando custos e tempo de inicialização.
-   **API Simples:** Um único endpoint `/retrieve` para facilitar a integração.
-   **Pronto para Produção:** Empacotado em uma imagem Docker leve e pronto para ser implantado.

### 🚀 Como Usar

#### Pré-requisitos

1.  **Docker** instalado e em execução na sua máquina.
2.  Uma **API Key da OpenAI**. Você pode obter uma em [platform.openai.com/api-keys](https://platform.openai.com/api-keys).

#### Executando a partir da Imagem do Docker Hub

Esta é a maneira mais fácil de usar. Não é necessário clonar este repositório.

```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="SUA_CHAVE_API_SEGURA" \
  -e REPO_URL="https://github.com/n8n-io/n8n.git" \
  -e REPO_BRANCH="master" \
  -v ./mcp_data/chroma_db:/app/chroma_db \
  --name meu-mcp-server-n8n \
  flaviomagacho/mcp-git-server:latest
```


### 🔧 Configuração (Variáveis de Ambiente)

-   `OPENAI_API_KEY` (obrigatório): Sua chave secreta da API da OpenAI.
-   `REPO_URL` (obrigatório): A URL `.git` do repositório público a ser indexado.
-   `REPO_BRANCH`: A branch quue será clonada para o MCP Server

### 🔌 Endpoint da API

O servidor expõe um endpoint principal:

**`POST /retrieve`**

Busca por fragmentos de contexto relevantes.

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

---

*Este projeto foi criado em [10 de Outubro de 2025].*

