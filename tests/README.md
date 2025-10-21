# Testes - MCP Git Server

Este diretório contém os testes automatizados do projeto.

## Estrutura

```
tests/
├── conftest.py              # Configuração global de testes
├── unit/                    # Testes unitários
│   ├── test_models.py       # Testes para models.py
│   ├── test_token_utils.py  # Testes para token_utils.py
│   └── test_embedding_config.py  # Testes para embedding_config.py
└── integration/             # Testes de integração
    └── test_api.py          # Testes de API endpoints
```

## Executando os Testes

### Instalar dependências

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Executar todos os testes

```bash
pytest
```

### Executar com cobertura

```bash
pytest --cov=. --cov-report=html
```

### Executar apenas testes unitários

```bash
pytest tests/unit/
```

### Executar apenas testes de integração

```bash
pytest tests/integration/
```

### Executar teste específico

```bash
pytest tests/unit/test_models.py::TestRetrieveRequest::test_valid_request
```

## Coverage

Após executar os testes com cobertura, abra o relatório HTML:

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Convenções

- Nomes de arquivos de teste devem começar com `test_`
- Nomes de funções de teste devem começar com `test_`
- Classes de teste devem começar com `Test`
- Use fixtures definidas em `conftest.py` para reutilizar código
- Marque testes lentos com `@pytest.mark.slow`

## Próximos Passos

- [ ] Adicionar mais testes unitários para document_loader.py
- [ ] Adicionar testes de integração completos
- [ ] Adicionar testes de performance
- [ ] Adicionar testes de segurança
- [ ] Aumentar cobertura para 80%+
