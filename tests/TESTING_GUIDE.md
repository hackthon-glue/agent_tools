# Testing Guide - AI Recruitment Platform

## Test Structure

### 📁 Directory Structure

```
tests/
├── unit/              # Unit tests (with mocks)
├── integration/       # Integration tests (real AWS connection)
├── acceptance/        # Acceptance tests (E2E)
├── conftest.py        # Auto-mock configuration
├── pytest.ini         # pytest configuration
└── TESTING_GUIDE.md   # This file
```

## 🎯 Test Levels

### 1. Unit Tests

- **Location**: `tests/unit/`
- **Purpose**: Fast validation of individual functions
- **Dependencies**: All mocked (no AWS credentials required)
- **Execution**: `pytest tests/unit -v`
- **Speed**: ⚡ Fast (~1 second)
- **Coverage**: 29 tests

### 2. Integration Tests

- **Location**: `tests/integration/`
- **Purpose**: Validate real AWS connections
- **Dependencies**: AWS credentials required
- **Execution**: `pytest -m integration -v`
- **Speed**: 🐢 Medium (~5-10 seconds)
- **Coverage**: 3 tests (DynamoDB, KB, Memory)

### 3. Acceptance Tests

- **Location**: `tests/acceptance/`
- **Purpose**: Validate entire agent workflows
- **Dependencies**: All AWS resources + AgentCore
- **Execution**: `pytest -m acceptance -v`
- **Speed**: 🐌 Slow (~10-30 seconds)
- **Coverage**: 5 tests (all agents)

## 🚀 Execution Methods

```bash
# Default (unit tests only, no AWS required)
pytest

# Unit tests only (explicit)
pytest tests/unit -v

# Integration tests (AWS credentials required)
pytest -m integration -v

# Acceptance tests (full environment required)
pytest -m acceptance -v

# All tests (AWS credentials required)
pytest -m "" -v

# With coverage
pytest tests/unit --cov=agents --cov-report=html
```

## 🔧 Environment Setup

### Unit Tests

```bash
# No AWS credentials required (conftest.py auto-mocks)
pytest
```

### Integration & Acceptance Tests

```bash
# Configure AWS credentials
export AWS_REGION=us-west-2
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret

# Or use AWS SSO
aws sso login

# Optional environment variables
export KNOWLEDGE_BASE_ID=your_kb_id
export MEMORY_ID=your_memory_id
```

## 🔄 Auto-Mock Features

`tests/conftest.py` automatically mocks:

- `boto3.client` - AWS SDK calls
- `bedrock_agentcore.memory.MemoryClient` - Memory initialization
- `agents.tools.memory_tools.get_conversation_history` - Conversation history retrieval

**Benefit**: All unit tests run without AWS credentials

## 🏷️ pytest Markers

```python
@pytest.mark.unit          # Unit test (runs by default)
@pytest.mark.integration   # Integration test (explicit execution)
@pytest.mark.acceptance    # Acceptance test (explicit execution)
```

## 🔄 Recommended CI/CD Flow

1. **On PR creation**: `pytest` (unit tests only, fast)
2. **On merge to main**: `pytest -m "" -v` (all tests)
3. **On release**: `pytest -m acceptance -v` (E2E validation)

## 💡 Best Practices

- During development: `pytest` for fast validation (no AWS required)
- AWS connection check: `pytest -m integration -v`
- Pre-deployment: `pytest -m acceptance -v` for final validation
- `conftest.py` ensures unit tests never require AWS

## 🐛 Troubleshooting

### AWS SSO Token Expired Error

```bash
# For unit tests → No problem (uses mocks)
pytest tests/unit -v

# For integration/acceptance tests → Re-authenticate
aws sso login
pytest -m integration -v
```

### Tests Not Found

```bash
# Check pytest.ini configuration
cat tests/pytest.ini

# Verify test discovery
pytest --collect-only
```

### Mocks Not Working

```bash
# Verify conftest.py exists
ls tests/conftest.py

# Clear cache
pytest --cache-clear
```
