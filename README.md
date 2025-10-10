<<<<<<< HEAD
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
  -e OPENAI_API_KEY="sk-SUA_CHAVE_API_DA_OPENAI" \
  -e REPO_URL="[https://github.com/n8n-io/n8n.git](https://github.com/n8n-io/n8n.git)" \
  --name meu-mcp-server \
  SEU_USUARIO_DOCKERHUB/mcp-retrieval-server:latest
```

*Substitua `SEU_USUARIO_DOCKERHUB` pelo seu nome de usuário no Docker Hub.*

### 🔧 Configuração (Variáveis de Ambiente)

-   `OPENAI_API_KEY` (obrigatório): Sua chave secreta da API da OpenAI.
-   `REPO_URL` (obrigatório): A URL `.git` do repositório público a ser indexado.

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
=======
# mcp-git-server
>>>>>>> origin/main
