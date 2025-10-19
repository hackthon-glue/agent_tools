# Testing Guide - AI Recruitment Platform

## Test Structure

### 📁 Directory Structure

```
tests/
├── unit/              # Unit tests (mocked AWS/AgentCore)
├── integration/       # Integration tests (real AWS services)
├── acceptance/        # E2E tests (full agent workflows)
├── conftest.py        # Auto-mock configuration
├── pytest.ini         # pytest configuration
└── TESTING_GUIDE.md   # This guide
```

## 🎯 Test Levels

### 1. Unit Tests (単体テスト)

**Purpose**: 個別の関数・ツールの動作検証（モック使用）

**Prerequisites**:
- ✅ No AWS credentials required
- ✅ All dependencies mocked
- ✅ Fast execution (~1s)

**Execution**:
```bash
pytest tests/unit -v
```

**Test Content** (8 files, 20+ tests):

| File | Tests | Coverage |
|------|-------|----------|
| `test_agents.py` | 6 tests | All 4 agents + tool integration |
| `test_orchestrator.py` | 4 tests | Agent routing logic |
| `test_memory_tools.py` | 2 tests | Memory event creation, history retrieval |
| `test_dynamodb_tools.py` | 4 tests | User profile, job listings, GitHub profile |
| `test_kb_tools.py` | 2 tests | Evaluation criteria retrieval |
| `test_pdf_tools.py` | 3 tests | Resume parsing (Claude + Textract) |
| `test_agent_tools.py` | - | Agent invocation |
| `test_collector_tools.py` | - | Web collectors |

**Key Test Scenarios**:
- ✅ Concierge Agent: Conversation flow
- ✅ Skill Parser Agent: Resume + GitHub analysis
- ✅ Job Matcher Agent: Matching logic
- ✅ Interviewer Copilot: Question generation
- ✅ Orchestrator: Request routing to specialized agents
- ✅ Memory Tools: Event creation, history retrieval
- ✅ DynamoDB Tools: CRUD operations
- ✅ Knowledge Base: Criteria retrieval
- ✅ PDF Tools: Resume parsing

### 2. Integration Tests (結合テスト)

**Purpose**: 実際のAWSサービスとの接続検証

**Prerequisites**:
- ⚠️ AWS credentials required
- ⚠️ AWS resources must exist (DynamoDB tables, Memory, KB)
- ⚠️ Medium execution time (~5-10s)

**Execution**:
```bash
# Configure AWS credentials first
export AWS_REGION=us-west-2
export MEMORY_ID=your_memory_id
export KNOWLEDGE_BASE_ID=your_kb_id

# Run integration tests
pytest -m integration -v
```

**Test Content** (3 files, 5+ tests):

| File | Tests | Coverage |
|------|-------|----------|
| `test_memory_integration.py` | 2 tests | AgentCore Memory client, event creation |
| `test_dynamodb_integration.py` | 2 tests | DynamoDB connection, user profile retrieval |
| `test_kb_integration.py` | 1 test | Knowledge Base retrieval |

**Key Test Scenarios**:
- ✅ AgentCore Memory: Real memory client initialization
- ✅ AgentCore Memory: Create memory event with real API
- ✅ DynamoDB: Connection validation
- ✅ DynamoDB: User profile retrieval from real table
- ✅ Knowledge Base: Evaluation criteria retrieval

### 3. Acceptance Tests (受け入れテスト)

**Purpose**: エンドツーエンドのエージェントワークフロー検証

**Prerequisites**:
- ⚠️ Full AWS environment required
- ⚠️ AgentCore Runtime deployed
- ⚠️ All resources configured (DynamoDB, Memory, KB)
- ⚠️ Slow execution (~10-30s)

**Execution**:
```bash
# Full environment setup required
export AWS_REGION=us-west-2
export MEMORY_ID=your_memory_id
export KNOWLEDGE_BASE_ID=your_kb_id

# Run acceptance tests
pytest -m acceptance -v
```

**Test Content** (2 files, 5+ tests):

| File | Tests | Coverage |
|------|-------|----------|
| `test_concierge_acceptance.py` | 1 test | Full career consultation workflow |
| `test_orchestrator_acceptance.py` | 4+ tests | Multi-agent orchestration |
| `test_local.py` | - | Local end-to-end testing |

**Key Test Scenarios**:
- ✅ Concierge Agent: User query → AI response (job search)
- ✅ Orchestrator: Career consultation routing
- ✅ Orchestrator: Resume analysis routing
- ✅ Orchestrator: Job matching routing
- ✅ Orchestrator: Interview support routing
- ✅ Multi-agent workflow: Request → Routing → Specialized Agent → Response

### 4. Post-Deployment Tests (デプロイ後テスト)

**Purpose**: 本番環境での動作検証

**Prerequisites**:
- ⚠️ Production environment deployed
- ⚠️ AgentCore Runtime accessible
- ⚠️ Production credentials

**Execution**:
```bash
# Use production environment
export AWS_REGION=us-west-2
export ENV=production

# Run smoke tests
pytest -m acceptance -k "test_concierge" -v

# Or run specific production validation
python tests/acceptance/test_local.py
```

**Test Content**:

| Test Type | Coverage |
|-----------|----------|
| Smoke Tests | Basic agent invocation |
| Health Checks | Memory, DynamoDB, KB connectivity |
| Performance Tests | Response time validation |
| Integration Tests | Cross-agent communication |

**Key Validation Points**:
- ✅ All agents respond within SLA (<5s)
- ✅ Memory persistence working
- ✅ Knowledge Base queries successful
- ✅ DynamoDB read/write operations
- ✅ Multi-agent orchestration functional
- ✅ Error handling and logging

## 📋 Test Execution Procedures

### Procedure 1: Unit Tests (開発中)

**When**: During development, before commit

**Steps**:
```bash
# 1. No setup required (auto-mocked)
pytest tests/unit -v

# 2. Run specific test file
pytest tests/unit/test_agents.py -v

# 3. Run specific test
pytest tests/unit/test_agents.py::test_concierge_agent -v

# 4. With coverage report
pytest tests/unit --cov=agents --cov-report=html
open htmlcov/index.html
```

**Expected Results**:
- ✅ All tests pass in <5s
- ✅ No AWS connection errors
- ✅ Coverage >80%

### Procedure 2: Integration Tests (マージ前)

**When**: Before merging to main branch

**Steps**:
```bash
# 1. Configure AWS credentials
export AWS_REGION=us-west-2
aws sso login

# 2. Set resource IDs
export MEMORY_ID=your_memory_id
export KNOWLEDGE_BASE_ID=your_kb_id

# 3. Run integration tests
pytest -m integration -v

# 4. Verify AWS connectivity
pytest tests/integration/test_dynamodb_integration.py -v
pytest tests/integration/test_memory_integration.py -v
```

**Expected Results**:
- ✅ All tests pass in <30s
- ✅ Real AWS connections successful
- ✅ No resource not found errors

### Procedure 3: Acceptance Tests (デプロイ前)

**When**: Before production deployment

**Steps**:
```bash
# 1. Full environment setup
export AWS_REGION=us-west-2
export MEMORY_ID=your_memory_id
export KNOWLEDGE_BASE_ID=your_kb_id
aws sso login

# 2. Run acceptance tests
pytest -m acceptance -v

# 3. Run orchestrator E2E test
pytest tests/acceptance/test_orchestrator_acceptance.py -v

# 4. Run concierge E2E test
pytest tests/acceptance/test_concierge_acceptance.py -v
```

**Expected Results**:
- ✅ All workflows complete successfully
- ✅ Multi-agent orchestration works
- ✅ Memory persistence verified
- ✅ Response quality acceptable

### Procedure 4: Post-Deployment Tests (デプロイ後)

**When**: After production deployment

**Steps**:
```bash
# 1. Configure production environment
export AWS_REGION=us-west-2
export ENV=production
aws sso login --profile production

# 2. Run smoke tests
pytest -m acceptance -k "test_concierge" -v

# 3. Validate critical paths
python tests/acceptance/test_local.py

# 4. Monitor logs
aws logs tail /aws/bedrock/agentcore --follow
```

**Expected Results**:
- ✅ Smoke tests pass
- ✅ Response time <5s
- ✅ No errors in logs
- ✅ Memory persistence working

## 🚀 Quick Commands

```bash
# Development (fast)
pytest

# Pre-commit (verify changes)
pytest tests/unit -v

# Pre-merge (AWS connectivity)
pytest -m integration -v

# Pre-deployment (E2E)
pytest -m acceptance -v

# All tests
pytest -m "" -v

# Specific agent
pytest tests/unit/test_agents.py::test_concierge_agent -v

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

## 🎭 Mock Strategy

### Auto-Mocked (conftest.py)

- `boto3.client` - All AWS SDK calls
- `bedrock_agentcore.memory.MemoryClient` - Memory client
- `agents.tools.memory_tools.get_conversation_history` - History retrieval
- `agents.tools.seqthink_tool.invoke` - Sequential thinking
- `agents.tools.awsdocs_tool.search` - AWS docs search

### Manual Mocking

```python
# Mock AgentCore Memory responses
@patch('bedrock_agentcore.memory.MemoryClient')
def test_with_memory(mock_memory):
    mock_memory.return_value.get_memory_items.return_value = [
        {"content": "Previous conversation"}
    ]
    # Test code here

# Mock Sequential Thinking
@patch('agents.tools.seqthink_tool.invoke')
def test_with_reasoning(mock_seqthink):
    mock_seqthink.return_value = {
        "thoughtNumber": 1,
        "nextThoughtNeeded": False,
        "reasoning": "Analysis complete"
    }
    # Test code here
```

**Benefit**: Unit tests run without AWS credentials or network calls

## 🏷️ pytest Markers

```python
@pytest.mark.unit          # Unit test (runs by default)
@pytest.mark.integration   # Integration test (explicit execution)
@pytest.mark.acceptance    # Acceptance test (explicit execution)
```

## 🔄 CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: pytest tests/unit -v
  
  integration-tests:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v2
      - name: Run integration tests
        run: pytest -m integration -v
  
  acceptance-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'release'
    steps:
      - uses: actions/checkout@v3
      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v2
      - name: Run acceptance tests
        run: pytest -m acceptance -v
```

### Recommended Flow

| Stage | Trigger | Tests | Duration |
|-------|---------|-------|----------|
| **PR Creation** | `git push` | Unit tests | ~5s |
| **Merge to Main** | PR merge | Unit + Integration | ~30s |
| **Release** | Tag creation | All tests | ~60s |
| **Post-Deploy** | Deployment complete | Smoke tests | ~10s |

## 📊 Test Coverage Matrix

| Component | Unit | Integration | Acceptance | Total |
|-----------|------|-------------|------------|-------|
| **Concierge Agent** | ✅ 1 test | ✅ 1 test | ✅ 1 test | 3 |
| **Skill Parser Agent** | ✅ 1 test | - | - | 1 |
| **Job Matcher Agent** | ✅ 1 test | ✅ 1 test | - | 2 |
| **Interviewer Copilot** | ✅ 1 test | - | - | 1 |
| **Orchestrator** | ✅ 4 tests | - | ✅ 4 tests | 8 |
| **Memory Tools** | ✅ 2 tests | ✅ 2 tests | - | 4 |
| **DynamoDB Tools** | ✅ 4 tests | ✅ 2 tests | - | 6 |
| **Knowledge Base** | ✅ 2 tests | ✅ 1 test | - | 3 |
| **PDF Tools** | ✅ 3 tests | - | - | 3 |
| **Agent Tools** | ✅ tests | - | - | - |
| **Collector Tools** | ✅ tests | - | - | - |
| **Total** | **20+ tests** | **7+ tests** | **5+ tests** | **32+** |

## 🎯 Agent-Specific Test Scenarios

### Concierge Agent (Memory + Reasoning)

```bash
# Unit: Conversation flow (mocked)
pytest tests/unit/test_agents.py::test_concierge_agent -v

# Integration: Memory persistence (real AWS)
pytest tests/integration/test_memory_integration.py -v

# Acceptance: Full conversation (E2E)
pytest tests/acceptance/test_concierge_acceptance.py -v
```

**Test Flow**:
1. Unit: Mock agent response → Verify conversation structure
2. Integration: Real Memory API → Verify event creation
3. Acceptance: Full workflow → Verify job search response

### Job Matcher Agent (Knowledge Base + Reasoning)

```bash
# Unit: Matching logic (mocked)
pytest tests/unit/test_agents.py::test_job_matcher -v

# Integration: KB queries (real AWS)
pytest tests/integration/test_kb_integration.py -v
```

**Test Flow**:
1. Unit: Mock KB results → Verify matching algorithm
2. Integration: Real KB query → Verify criteria retrieval

### Orchestrator Agent (All Tools)

```bash
# Unit: Agent coordination (mocked)
pytest tests/unit/test_orchestrator.py -v

# Acceptance: Multi-agent workflow (E2E)
pytest tests/acceptance/test_orchestrator_acceptance.py -v
```

**Test Flow**:
1. Unit: Mock all agents → Verify routing logic
2. Acceptance: Real agents → Verify end-to-end orchestration

## 💡 Best Practices

### Development Workflow

1. **Write unit test first** (TDD approach)
   ```bash
   # Create test file
   touch tests/unit/test_new_feature.py
   
   # Write failing test
   pytest tests/unit/test_new_feature.py -v
   
   # Implement feature
   # Run test until it passes
   ```

2. **Run unit tests frequently** (fast feedback)
   ```bash
   pytest tests/unit -v
   ```

3. **Run integration tests before commit**
   ```bash
   pytest -m integration -v
   ```

4. **Run acceptance tests before PR**
   ```bash
   pytest -m acceptance -v
   ```

### Testing Guidelines

- ✅ **Unit tests**: Mock all external dependencies
- ✅ **Integration tests**: Use real AWS services, clean up resources
- ✅ **Acceptance tests**: Test complete workflows, verify business logic
- ✅ **Tool testing**: Test tools independently before agent integration
- ✅ **Memory testing**: Always clean up test sessions
- ✅ **Error handling**: Test both success and failure scenarios
- ✅ **Coverage**: Aim for >80% code coverage

### Common Patterns

```python
# Unit test pattern
@patch('agents.tools.memory_tools.MemoryClient')
def test_with_mock(mock_memory):
    mock_memory.return_value.get_items.return_value = []
    # Test code

# Integration test pattern
@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("AWS_REGION"), reason="AWS not configured")
def test_real_aws():
    # Test with real AWS

# Acceptance test pattern
@pytest.mark.acceptance
def test_e2e_workflow():
    # Test complete workflow
```

## 🐛 Troubleshooting

### AWS SSO Token Expired

```bash
# Unit tests: No issue (mocked)
pytest tests/unit -v

# Integration/Acceptance: Re-authenticate
aws sso login
pytest -m integration -v
```

### AgentCore Memory Connection Failed

```bash
# Check Memory ID configuration
echo $MEMORY_ID

# Verify Memory exists
aws bedrock-agent-runtime get-memory --memory-id $MEMORY_ID

# Run with mock instead
pytest tests/unit/test_memory_tools.py -v
```

### Knowledge Base Query Failed

```bash
# Verify KB ID
echo $KNOWLEDGE_BASE_ID

# Check KB status
aws bedrock-agent get-knowledge-base --knowledge-base-id $KNOWLEDGE_BASE_ID

# Use mock for unit tests
pytest tests/unit/test_kb_tools.py -v
```

### Tests Not Found

```bash
# Verify pytest.ini
cat tests/pytest.ini

# Check test discovery
pytest --collect-only

# Clear cache
pytest --cache-clear
```

### Mock Not Applied

```bash
# Verify conftest.py
ls tests/conftest.py

# Check mock patches
pytest tests/unit -v --setup-show
```
