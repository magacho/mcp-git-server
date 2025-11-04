# 🔐 Setup Personal Access Token (PAT)

Para permitir que o workflow crie Pull Requests automaticamente, você precisa configurar um Personal Access Token.

## 📋 Passos:

### 1. Criar o Token

1. Acesse: https://github.com/settings/tokens
2. Click em **"Generate new token"** → **"Generate new token (classic)"**
3. Dê um nome descritivo: `Auto-Test Agent - mcp-git-server`
4. Defina expiração: **No expiration** (ou 1 ano se preferir)
5. Selecione os **scopes** necessários:
   - ☑️ **`repo`** (Full control of private repositories)
     - ☑️ repo:status
     - ☑️ repo_deployment
     - ☑️ public_repo
     - ☑️ repo:invite
     - ☑️ security_events
   - ☑️ **`workflow`** (Update GitHub Action workflows)

6. Click em **"Generate token"**
7. **COPIE O TOKEN** (você só verá uma vez!)

---

### 2. Adicionar como Secret no Repositório

1. Vá para o repositório: https://github.com/magacho/mcp-git-server
2. Click em **Settings** (ícone de engrenagem)
3. No menu lateral, click em **Secrets and variables** → **Actions**
4. Click no botão **"New repository secret"**
5. Preencha:
   - **Name:** `GH_PAT`
   - **Secret:** Cole o token que você copiou
6. Click em **"Add secret"**

---

### 3. Verificar Configuração

O workflow está configurado para usar o secret assim:

```yaml
- name: Checkout code
  uses: actions/checkout@v3
  with:
    token: ${{ secrets.GH_PAT || github.token }}

- name: Create Pull Request
  env:
    GH_TOKEN: ${{ secrets.GH_PAT || github.token }}
  run: |
    gh pr create ...
```

**Comportamento:**
- ✅ Se `GH_PAT` existir → Usa o PAT (pode criar PRs)
- ⚠️ Se `GH_PAT` não existir → Usa `github.token` (não pode criar PRs)

---

### 4. Testar

Após configurar o secret:

1. Crie uma issue de teste:
```bash
gh issue create \
  --title "🧪 Test: Auto-test agent with PAT" \
  --label "test-coverage" \
  --body "Testing automatic PR creation with PAT."
```

2. Aguarde ~3-5 minutos

3. Verifique se:
   - ✅ Workflow rodou
   - ✅ Branch foi criada
   - ✅ PR foi criado automaticamente
   - ✅ Comentário apareceu na issue

---

## 🔒 Segurança

### Boas Práticas:

✅ **DO:**
- Use tokens com expiração se possível
- Use scopes mínimos necessários
- Rotacione tokens periodicamente
- Revogue tokens não utilizados

❌ **DON'T:**
- Nunca commite tokens no código
- Nunca compartilhe tokens
- Não use o mesmo token em múltiplos lugares

### Revogar Token:

Se precisar revogar:
1. https://github.com/settings/tokens
2. Encontre o token
3. Click em **"Delete"**
4. Gere um novo se necessário

---

## ❓ Troubleshooting

### Workflow ainda falha com "not permitted"?

**Verifique:**
1. Secret foi criado com nome exato: `GH_PAT`
2. Token tem scopes `repo` e `workflow`
3. Token não está expirado
4. Workflow foi atualizado (último commit tem as mudanças)

### Como testar se o token está funcionando?

```bash
# Localmente, com o token
export GH_TOKEN="seu_token_aqui"
gh pr list
```

Se listar PRs sem erro, o token está funcionando.

---

## 📝 Alternativa: GitHub App

Se preferir usar GitHub App (mais seguro mas mais complexo):

1. Crie um GitHub App
2. Instale no repositório
3. Use `actions/create-github-app-token` action
4. Configure workflow para usar o app token

**Documentação:** https://docs.github.com/en/apps/creating-github-apps

---

## ✅ Checklist Final

Antes de usar:
- [ ] Token criado no GitHub
- [ ] Scopes `repo` e `workflow` selecionados
- [ ] Token copiado
- [ ] Secret `GH_PAT` adicionado ao repositório
- [ ] Workflow atualizado (commit aplicado)
- [ ] Testado com issue de exemplo

**Após configurar, o workflow criará PRs automaticamente!** 🚀
