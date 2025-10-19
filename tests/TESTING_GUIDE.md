# Testing Guide - AI Recruitment Platform

## Overview

AI Agent Platform for Enterprise HR Systems using AWS Bedrock AgentCore + Strands framework.

**Orchestrator integrates 4 specialized agents:**

1. **Concierge Agent** - Career consultation & job search (AgentCore Memory)
2. **Skill Parser Agent** - Resume & GitHub analysis (PDF Tools)
3. **Job Matcher Agent** - Candidate × Job matching (Knowledge Base)
4. **Interviewer Copilot Agent** - Interview support (AgentCore Memory)

---

## Test Structure

```
tests/
├── unit/                          # Unit tests (mocked AWS/AgentCore)
│   ├── test_agents.py             # 7 tests - All agents + tools
│   ├── test_orchestrator.py       # 4 tests - Agent routing
│   ├── test_memory_tools.py       # 2 tests - Memory operations
│   ├── test_dynamodb_tools.py     # 4 tests - DynamoDB CRUD
│   ├── test_kb_tools.py           # 2 tests - Knowledge Base
│   ├── test_pdf_tools.py          # 3 tests - PDF parsing
│   ├── test_agent_tools.py        # Agent invocation
│   └── test_collector_tools.py    # Web collectors
├── integration/                   # Integration tests (real AWS)
│   ├── test_memory_integration.py # 2 tests - AgentCore Memory
│   ├── test_dynamodb_integration.py # 2 tests - DynamoDB
│   └── test_kb_integration.py     # 2 tests - Knowledge Base
├── acceptance/                    # E2E tests (deployed AgentCore)
│   └── test_cloud_deployment.py   # 4 tests - Full workflows
├── conftest.py                    # Auto-mock configuration
├── pytest.ini                     # pytest configuration
└── TESTING_GUIDE.md               # This guide
```

---

## Quick Start

```bash
# Unit tests (no AWS required)
pytest tests/unit -v

# Integration tests (AWS credentials required)
pytest -m integration -v

# Acceptance tests (AgentCore deployment required)
pytest -m acceptance -v
```

---

## Test Levels

### 1. Unit Tests

**Purpose**: Test individual functions and tools with mocked dependencies

**Prerequisites**:

- ✅ No AWS credentials required
- ✅ All dependencies auto-mocked via conftest.py
- ✅ Fast execution (~1s)

**Execution**:

```bash
# Run all unit tests
pytest tests/unit -v

# Run specific test file
pytest tests/unit/test_agents.py -v

# Run specific test
pytest tests/unit/test_agents.py::test_concierge_agent -v

# With coverage report
pytest tests/unit --cov=agents --cov-report=html
open htmlcov/index.html
```

**Test Coverage** (8 files, 22 tests):

| File                      | Tests   | Coverage                                                             |
| ------------------------- | ------- | -------------------------------------------------------------------- |
| `test_agents.py`          | 7 tests | Concierge, Skill Parser, Job Matcher, Interviewer + tool integration |
| `test_orchestrator.py`    | 4 tests | Routes to concierge, skill parser, job matcher, interviewer          |
| `test_memory_tools.py`    | 2 tests | create_memory_event, get_conversation_history                        |
| `test_dynamodb_tools.py`  | 4 tests | get_user_profile, get_job_listings (2), get_github_profile           |
| `test_kb_tools.py`        | 2 tests | retrieve_evaluation_criteria (2)                                     |
| `test_pdf_tools.py`       | 3 tests | parse_resume_claude_only, parse_resume_textract                      |
| `test_agent_tools.py`     | -       | Agent invocation                                                     |
| `test_collector_tools.py` | -       | Web collectors                                                       |

**Key Test Scenarios**:

- ✅ Concierge Agent: Conversation flow with career consultation
- ✅ Skill Parser Agent: Resume + GitHub analysis
- ✅ Job Matcher Agent: Matching logic with Knowledge Base
- ✅ Interviewer Copilot: Interview question generation
- ✅ Orchestrator: Request routing to specialized agents
- ✅ Memory Tools: Event creation, history retrieval
- ✅ DynamoDB Tools: User profile, job listings, GitHub profile CRUD
- ✅ Knowledge Base: Evaluation criteria retrieval
- ✅ PDF Tools: Resume parsing with Claude and Textract

---

### 2. Integration Tests

**Purpose**: Test real AWS service connections

**Prerequisites**:

- ⚠️ AWS credentials required
- ⚠️ AWS resources must exist (DynamoDB tables, Memory, Knowledge Base)
- ⚠️ Medium execution time (~5-10s)

**Execution**:

```bash
# Configure AWS credentials
export AWS_REGION=us-west-2
export MEMORY_ID=your_memory_id
export KNOWLEDGE_BASE_ID=your_kb_id
aws sso login

# Run all integration tests
pytest -m integration -v

# Run specific integration test
pytest tests/integration/test_memory_integration.py -v
```

**Test Coverage** (3 files, 6 tests):

| File                           | Tests   | Coverage                                                            |
| ------------------------------ | ------- | ------------------------------------------------------------------- |
| `test_memory_integration.py`   | 2 tests | memory_client_import, create_memory_event_real                      |
| `test_dynamodb_integration.py` | 2 tests | dynamodb_connection, get_user_profile_real                          |
| `test_kb_integration.py`       | 2 tests | bedrock_agent_runtime_connection, retrieve_evaluation_criteria_real |

**Key Test Scenarios**:

- ✅ AgentCore Memory: Real memory client initialization and event creation
- ✅ DynamoDB: Connection validation and user profile retrieval
- ✅ Knowledge Base: Bedrock connection and evaluation criteria retrieval

---

### 3. Acceptance Tests

**Purpose**: End-to-end agent workflow validation with deployed AgentCore Runtime

**Prerequisites**:

- ⚠️ **CRITICAL**: AgentCore Runtime must be deployed first
- ⚠️ Full AWS environment required
- ⚠️ All resources configured (DynamoDB, Memory, Knowledge Base)
- ⚠️ Slow execution (~10-30s)

**IMPORTANT - Deployment Required**:

Before running acceptance tests, you MUST:

1. **Deploy Orchestrator Agent to AgentCore**:

   ```bash
   cd agents
   agentcore launch
   ```

2. **Set Agent ARN environment variable** (from deployment output):

   ```bash
   export ORCHESTRATOR_AGENT_ARN=arn:aws:bedrock-agentcore:us-west-2:123456789012:runtime/orchestrator_agent-xxxxx
   ```

3. **Set Memory ID environment variable** (from deployment output):

   ```bash
   export AGENTCORE_MEMORY_ID=orchestrator_agent_mem-xxxxx
   ```

4. **Verify deployment**:
   ```bash
   cd agents
   agentcore status
   ```

**ARN Format**:

```
arn:aws:bedrock-agentcore:us-west-2:123456789012:runtime/orchestrator_agent-m0f7es8bJF
```

**Execution**:

```bash
# Full environment setup
export AWS_REGION=us-west-2
export MEMORY_ID=your_memory_id
export KNOWLEDGE_BASE_ID=your_kb_id
export ORCHESTRATOR_AGENT_ARN=arn:aws:bedrock-agentcore:us-west-2:123456789012:runtime/orchestrator_agent-xxxxx
export AGENTCORE_MEMORY_ID=orchestrator_agent_mem-xxxxx

# Run all acceptance tests
pytest -m acceptance -v

# Run specific acceptance test
pytest tests/acceptance/test_cloud_deployment.py::test_cloud_health_check -v
pytest tests/acceptance/test_cloud_deployment.py::test_cloud_orchestrator -v
pytest tests/acceptance/test_cloud_deployment.py::test_cloud_memory_conversation -v
pytest tests/acceptance/test_cloud_deployment.py::test_cloud_memory_persistence -v
```

**Test Coverage** (1 file, 4 tests):

| File                       | Tests   | Coverage                                                            |
| -------------------------- | ------- | ------------------------------------------------------------------- |
| `test_cloud_deployment.py` | 4 tests | Health check, orchestrator, memory conversation, memory persistence |

**Key Test Scenarios**:

- ✅ **test_cloud_health_check**: Agent availability and basic response
- ✅ **test_cloud_orchestrator**: Single job search request routing
- ✅ **test_cloud_memory_conversation**: 3-turn conversation with context retention
  - Turn 1: Initial job search (backend engineer)
  - Turn 2: Follow-up question (salary range) - tests memory recall
  - Turn 3: Another follow-up (company recommendations) - tests memory depth
- ✅ **test_cloud_memory_persistence**: Memory resource verification

**Expected Output**:

```
tests/acceptance/test_cloud_deployment.py::test_cloud_health_check PASSED     [ 25%]
tests/acceptance/test_cloud_deployment.py::test_cloud_orchestrator PASSED     [ 50%]
tests/acceptance/test_cloud_deployment.py::test_cloud_memory_conversation PASSED [ 75%]
tests/acceptance/test_cloud_deployment.py::test_cloud_memory_persistence PASSED [100%]

======================== 4 passed in 30.15s ========================
```

---

## Test Execution Workflow

### Development Phase

```bash
# 1. During development (fast feedback)
pytest tests/unit -v

# 2. Before commit (verify changes)
pytest tests/unit --cov=agents -v
```

### Pre-Merge Phase

```bash
# 1. Configure AWS
export AWS_REGION=us-west-2
aws sso login

# 2. Run integration tests
pytest -m integration -v
```

### Pre-Deployment Phase

```bash
# 1. Deploy to AgentCore
cd agents
agentcore launch

# 2. Set environment variables from deployment output
export ORCHESTRATOR_AGENT_ARN=<from deployment output>
export AGENTCORE_MEMORY_ID=<from deployment output>

# 3. Run acceptance tests
pytest -m acceptance -v
```

### Post-Deployment Phase

```bash
# 1. Smoke tests
pytest -m acceptance -k "test_cloud_health_check" -v

# 2. Monitor logs
aws logs tail /aws/bedrock-agentcore/runtimes/orchestrator_agent-xxxxx-DEFAULT --follow
```

---

## Environment Setup

### Unit Tests

```bash
# No setup required - auto-mocked
pytest tests/unit -v
```

### Integration Tests

```bash
export AWS_REGION=us-west-2
export MEMORY_ID=your_memory_id
export KNOWLEDGE_BASE_ID=your_kb_id
aws sso login
```

### Acceptance Tests

```bash
# Step 1: Deploy AgentCore
cd agents
agentcore launch

# Step 2: Set environment variables from deployment output
export AWS_REGION=us-west-2
export MEMORY_ID=your_memory_id
export KNOWLEDGE_BASE_ID=your_kb_id
export ORCHESTRATOR_AGENT_ARN=arn:aws:bedrock-agentcore:us-west-2:123456789012:runtime/orchestrator_agent-xxxxx
export AGENTCORE_MEMORY_ID=orchestrator_agent_mem-xxxxx
```

---

## Mock Strategy

### Auto-Mocked (conftest.py)

The following are automatically mocked for unit tests:

- `boto3.client` - All AWS SDK calls
- `bedrock_agentcore.memory.MemoryClient` - Memory client
- `agents.tools.memory_tools.get_conversation_history` - History retrieval
- `agents.tools.seqthink_tool.invoke` - Sequential thinking
- `agents.tools.awsdocs_tool.search` - AWS docs search

### Manual Mocking

```python
# Mock AgentCore Memory
@patch('bedrock_agentcore.memory.MemoryClient')
def test_with_memory(mock_memory):
    mock_memory.return_value.get_memory_items.return_value = [
        {"content": "Previous conversation"}
    ]
    # Test code

# Mock Sequential Thinking
@patch('agents.tools.seqthink_tool.invoke')
def test_with_reasoning(mock_seqthink):
    mock_seqthink.return_value = {
        "thoughtNumber": 1,
        "nextThoughtNeeded": False,
        "reasoning": "Analysis complete"
    }
    # Test code
```

---

## pytest Markers

```python
@pytest.mark.unit          # Unit test (runs by default)
@pytest.mark.integration   # Integration test (requires -m integration)
@pytest.mark.acceptance    # Acceptance test (requires -m acceptance)
```

---

## Test Coverage Matrix

| Component               | Unit   | Integration | Acceptance | Total  |
| ----------------------- | ------ | ----------- | ---------- | ------ |
| **Concierge Agent**     | ✅ 1   | -           | ✅ 1       | 2      |
| **Skill Parser Agent**  | ✅ 1   | -           | -          | 1      |
| **Job Matcher Agent**   | ✅ 1   | -           | -          | 1      |
| **Interviewer Copilot** | ✅ 1   | -           | -          | 1      |
| **Orchestrator**        | ✅ 4   | -           | ✅ 4       | 8      |
| **Memory Tools**        | ✅ 2   | ✅ 2        | -          | 4      |
| **DynamoDB Tools**      | ✅ 4   | ✅ 2        | -          | 6      |
| **Knowledge Base**      | ✅ 2   | ✅ 2        | -          | 4      |
| **PDF Tools**           | ✅ 3   | -           | -          | 3      |
| **Agent Tools**         | -      | -           | -          | -      |
| **Collector Tools**     | -      | -           | -          | -      |
| **Total**               | **22** | **6**       | **4**      | **32** |

---

## Agent-Specific Testing

### Concierge Agent (Memory + Reasoning)

```bash
# Unit: Conversation flow (mocked)
pytest tests/unit/test_agents.py::test_concierge_agent -v

# Integration: Memory persistence (real AWS)
pytest tests/integration/test_memory_integration.py -v

# Acceptance: Full conversation (E2E)
pytest tests/acceptance/test_cloud_deployment.py::test_cloud_orchestrator -v
```

### Job Matcher Agent (Knowledge Base + Reasoning)

```bash
# Unit: Matching logic (mocked)
pytest tests/unit/test_agents.py::test_job_matcher_agent -v

# Integration: KB queries (real AWS)
pytest tests/integration/test_kb_integration.py -v
```

### Orchestrator Agent (All Tools)

```bash
# Unit: Agent coordination (mocked)
pytest tests/unit/test_orchestrator.py -v

# Acceptance: Multi-agent workflow (E2E)
pytest tests/acceptance/test_cloud_deployment.py -v
```

---

## Troubleshooting

### AWS Authentication Error

```bash
aws sts get-caller-identity
aws sso login
```

### DynamoDB Tables Not Found

```bash
./scripts/setup/02-create-dynamodb.sh
aws dynamodb list-tables --region us-west-2
```

### AgentCore Memory Connection Failed

```bash
echo $MEMORY_ID
aws bedrock-agent-runtime get-memory --memory-id $MEMORY_ID
pytest tests/unit/test_memory_tools.py -v  # Use mocked version
```

### Agent ARN Not Set (Acceptance Tests)

```bash
# Verify deployment
cd agents
agentcore status

# Set ARN from output
export ORCHESTRATOR_AGENT_ARN=<from deployment output>
export AGENTCORE_MEMORY_ID=<from deployment output>
```

### Test Failed: Agent not found

```bash
# Verify orchestrator exists
aws bedrock-agent-runtime list-agents --region us-west-2

# Redeploy if needed
cd agents
agentcore launch
```

### Tests Not Found

```bash
pytest --collect-only
pytest --cache-clear
```

---

## Best Practices

### Development Workflow

1. **Write unit test first** (TDD)

   ```bash
   touch tests/unit/test_new_feature.py
   pytest tests/unit/test_new_feature.py -v
   ```

2. **Run unit tests frequently**

   ```bash
   pytest tests/unit -v
   ```

3. **Run integration tests before commit**

   ```bash
   pytest -m integration -v
   ```

4. **Deploy and run acceptance tests before PR**
   ```bash
   cd agents && agentcore launch
   export ORCHESTRATOR_AGENT_ARN=<from output>
   pytest -m acceptance -v
   ```

### Testing Guidelines

- ✅ **Unit tests**: Mock all external dependencies
- ✅ **Integration tests**: Use real AWS services, clean up resources
- ✅ **Acceptance tests**: Deploy first, then test complete workflows
- ✅ **Tool testing**: Test tools independently before agent integration
- ✅ **Memory testing**: Always clean up test sessions
- ✅ **Error handling**: Test both success and failure scenarios
- ✅ **Coverage**: Aim for >80% code coverage

### Common Test Patterns

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
    # Test complete workflow with deployed agent
```

---

## Success Criteria

### Unit Tests

- ✅ All 22 tests pass in <5s
- ✅ No AWS connection errors
- ✅ Coverage >80%

### Integration Tests

- ✅ All 6 tests pass in <30s
- ✅ Real AWS connections successful
- ✅ No resource not found errors

### Acceptance Tests

- ✅ AgentCore deployment successful
- ✅ All 4 workflows complete successfully
- ✅ Multi-agent orchestration works
- ✅ Memory persistence verified (3-turn conversation)
- ✅ Response time <5s per request
- ✅ Response quality acceptable
