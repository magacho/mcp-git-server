# Tests - MCP Git Server

This directory contains the automated tests for the project.

## Structure

```
tests/
├── conftest.py              # Global test configuration
├── unit/                    # Unit tests
│   ├── test_models.py       # Tests for models.py
│   ├── test_token_utils.py  # Tests for token_utils.py
│   └── test_embedding_config.py  # Tests for embedding_config.py
└── integration/             # Integration tests
    └── test_api.py          # API endpoint tests
```

## Running Tests

### Install dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Run all tests

```bash
pytest
```

### Run with coverage

```bash
pytest --cov=. --cov-report=html
```

### Run only unit tests

```bash
pytest tests/unit/
```

### Run only integration tests

```bash
pytest tests/integration/
```

### Run specific test

```bash
pytest tests/unit/test_models.py::TestRetrieveRequest::test_valid_request
```

## Coverage

After running tests with coverage, open the HTML report:

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Conventions

- Test file names should start with `test_`
- Test function names should start with `test_`
- Test classes should start with `Test`
- Use fixtures defined in `conftest.py` to reuse code
- Mark slow tests with `@pytest.mark.slow`

## Next Steps

- [ ] Add more unit tests for document_loader.py
- [ ] Add complete integration tests
- [ ] Add performance tests
- [ ] Add security tests
- [ ] Increase coverage to 80%+
