# AI Recruitment Platform

**Enterprise HR Automation with Multi-Agent AI System**

Built on AWS Bedrock AgentCore + Strands Framework

---

## Overview

An intelligent recruitment platform that automates enterprise HR workflows through specialized AI agents. The system orchestrates career consultation, resume analysis, candidate matching, and interview support using AWS Bedrock's foundation models and AgentCore infrastructure.

**Key Capabilities:**

- Conversational career guidance with memory persistence
- Automated resume and GitHub profile analysis
- Intelligent candidate-job matching using knowledge bases
- Real-time interview support with contextual assistance

---

## Architecture

### Multi-Agent System

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator Agent                        │
│              (Coordinates all specialized agents)            │
└────────────┬────────────┬────────────┬──────────────┬───────┘
             │            │            │              │
    ┌────────▼───┐  ┌────▼─────┐  ┌──▼──────┐  ┌──────▼───────┐
    │ Concierge  │  │  Skill   │  │   Job   │  │ Interviewer  │
    │   Agent    │  │  Parser  │  │ Matcher │  │   Copilot    │
    └────────────┘  └──────────┘  └─────────┘  └──────────────┘
         │               │              │              │
    Memory API      PDF Tools      Knowledge      Memory API
                                      Base
```

### Agent Responsibilities

| Agent                   | Purpose                                   | Key Technologies                      |
| ----------------------- | ----------------------------------------- | ------------------------------------- |
| **Orchestrator**        | Routes requests to specialized agents     | Strands framework, AgentCore Runtime  |
| **Concierge**           | Career consultation & job search guidance | AgentCore Memory (1-hour sessions)    |
| **Skill Parser**        | Resume & GitHub profile analysis          | PDF parsing, Claude 3.5 Sonnet        |
| **Job Matcher**         | Candidate-job matching with scoring       | Bedrock Knowledge Base, HYBRID search |
| **Interviewer Copilot** | Interview question generation & support   | AgentCore Memory (30-min sessions)    |

---

## Tech Stack

### Core Infrastructure

- **AWS Bedrock AgentCore**: Serverless agent runtime with built-in observability
- **Strands Framework**: Agent orchestration and tool integration
- **Claude 3.5 Sonnet v2**: Foundation model (`us.anthropic.claude-sonnet-4-5-20250929-v1:0`)

### Data & Storage

- **DynamoDB**: User profiles, job listings, GitHub data
- **Bedrock Knowledge Base**: Evaluation criteria, matching rules (HYBRID search with reranking)
- **AgentCore Memory**: Conversation history and session management

### Tools & Integrations

- **Sequential Thinking**: Multi-step reasoning for complex tasks
- **PDF Tools**: Resume parsing (Claude + Textract)
- **Web Collectors**: LinkedIn, GitHub, job market data
- **Context7**: Library documentation search
- **AWS Docs**: Official AWS documentation search

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your AWS credentials and resource IDs

# 3. Set up infrastructure (choose your scenario)
./scripts/setup/00-setup-all.sh  # Complete setup from scratch
# OR use existing resources (see SETUP_GUIDE.md)

# 4. Deploy to AgentCore
cd agents
agentcore launch

# 5. Test deployment
pytest -m acceptance -v
```

---

## Documentation

### 📘 [SETUP_GUIDE.md](scripts/SETUP_GUIDE.md)

**When to read:** Setting up AWS infrastructure and deploying agents

**Contents:**

- **Scenario 1**: Using existing Knowledge Base, S3, and OpenSearch resources
- **Scenario 2**: Complete setup from scratch (automated scripts)
- Infrastructure dependencies and deployment order
- AgentCore Runtime deployment with Memory configuration
- Environment variable configuration
- Troubleshooting common deployment issues

**Use this guide when:**

- First-time setup of the platform
- Deploying to a new AWS account or region
- Configuring DynamoDB tables, Knowledge Base, or Memory
- Troubleshooting deployment failures

---

### 🧪 [TESTING_GUIDE.md](tests/TESTING_GUIDE.md)

**When to read:** Running tests and validating agent functionality

**Contents:**

- **Unit Tests**: Fast, mocked tests (22 tests, no AWS required)
- **Integration Tests**: Real AWS service connections (6 tests)
- **Acceptance Tests**: End-to-end workflows with deployed agents (4 tests)
- Test execution workflow (development → pre-merge → pre-deployment)
- Mock strategy and test patterns
- Coverage matrix for all agents and tools

**Use this guide when:**

- Developing new features (TDD workflow)
- Validating changes before commits
- Testing deployed agents in cloud environment
- Debugging agent behavior or tool integration
- Measuring test coverage

---

### 🔐 [POLICIES.md](scripts/policies/POLICIES.md)

**When to read:** Understanding IAM permissions and security configuration

**Contents:**

- Required IAM permissions for all AWS services
- DynamoDB table access policies
- Bedrock Knowledge Base and Memory permissions
- Foundation model access (Claude, Nova)
- Cross-region inference profile support
- Trust policy for AgentCore Runtime

**Use this guide when:**

- Setting up IAM roles for the first time
- Troubleshooting permission errors
- Auditing security configurations
- Adding new AWS service integrations
- Configuring cross-account access

---

## Project Structure

```
agent_tools/
├── agents/                          # Agent implementations
│   ├── orchestrator_agent.py        # Main coordinator
│   ├── concierge_agent.py           # Career consultation (Memory)
│   ├── skill_parser_agent.py        # Resume & GitHub analysis
│   ├── job_matcher_agent.py         # Candidate matching (KB)
│   ├── interviewer_copilot_agent.py # Interview support (Memory)
│   ├── memory_hook.py               # AgentCore Memory integration
│   └── tools/                       # Tool implementations
│       ├── dynamodb_tools.py        # DynamoDB access
│       ├── kb_tools.py              # Knowledge Base queries
│       ├── memory_tools.py          # Memory operations
│       ├── pdf_tools.py             # Resume parsing
│       ├── agent_tools.py           # Agent invocation
│       ├── collector_tools.py       # Web data collection
│       └── collectors/              # Collector implementations
│           ├── linkedin.py
│           ├── github.py
│           ├── job_market.py
│           └── candidate_search.py
├── scripts/                         # Setup and deployment scripts
│   ├── setup/                       # Infrastructure setup
│   │   ├── 00-setup-all.sh          # Master setup script
│   │   ├── 01-create-iam-role.sh
│   │   ├── 02-create-dynamodb.sh
│   │   ├── 03-create-s3-kb.sh
│   │   ├── 04-create-opensearch.sh
│   │   ├── 05-create-knowledge-base.sh
│   │   ├── 06-load-test-data.py
│   │   └── 07-deploy-agentcore.sh
│   ├── utils/
│   │   └── 99-cleanup.sh            # Resource cleanup
│   └── policies/                    # IAM policies
│       ├── runtime-execution-policy.json
│       └── trust-policy.json
├── tests/                           # Test suite
│   ├── unit/                        # Unit tests (22 tests)
│   ├── integration/                 # Integration tests (6 tests)
│   ├── acceptance/                  # E2E tests (4 tests)
│   └── conftest.py                  # Auto-mock configuration
├── .env.example                     # Environment template
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## DynamoDB Schema

### recruitment_users

```
user_id (PK) | name | email | skills | experience | preferences
```

### recruitment_jobs

```
job_id (PK) | title | company | location | requirements | description
```

### recruitment_github_profiles

```
user_id (PK) | username | repos | languages | contributions
```

---

## Environment Configuration

Key environment variables (see [.env.example](.env.example)):

```bash
# AWS Configuration
AWS_REGION=us-west-2
AWS_ACCOUNT_ID=your_account_id

# DynamoDB Tables
DYNAMODB_USERS_TABLE=recruitment_users
DYNAMODB_JOBS_TABLE=recruitment_jobs
DYNAMODB_GITHUB_TABLE=recruitment_github_profiles

# Knowledge Base
KNOWLEDGE_BASE_ID=your_kb_id
KB_USE_RERANK=true
KB_SEARCH_TYPE=HYBRID

# Memory
MEMORY_ID=your_memory_id
CONCIERGE_SESSION_TTL=3600
INTERVIEWER_SESSION_TTL=1800

# Model
CLAUDE_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0
```

---

## Development Workflow

```bash
# 1. Local development with unit tests
pytest tests/unit -v

# 2. Integration testing with AWS
pytest -m integration -v

# 3. Deploy to AgentCore
cd agents && agentcore launch

# 4. End-to-end validation
pytest -m acceptance -v

# 5. Monitor logs
aws logs tail /aws/bedrock-agentcore/runtimes/orchestrator_agent-xxxxx-DEFAULT --follow
```

---

## Key Features

### AgentCore Memory Integration

- **Automatic conversation history**: Load past context on agent initialization
- **Session management**: Configurable TTL (1 hour for Concierge, 30 min for Interviewer)
- **Memory Hook**: Strands HookProvider implementation for seamless persistence

### Knowledge Base Search

- **HYBRID search**: Combines semantic and keyword matching
- **Reranking**: Improves result relevance with Bedrock reranking
- **Evaluation criteria**: Skill matching, experience evaluation, cultural fit

### Multi-Agent Orchestration

- **Intelligent routing**: Orchestrator analyzes requests and delegates to specialists
- **Tool integration**: Sequential thinking, PDF parsing, web collectors
- **Error handling**: Graceful fallbacks and retry logic

---

## Observability

### CloudWatch Logs

```bash
/aws/bedrock-agentcore/runtimes/orchestrator_agent-{id}-DEFAULT
```

### X-Ray Tracing

Automatic distributed tracing for all agent invocations

### Metrics Dashboard

```
https://console.aws.amazon.com/cloudwatch/home?region={AWS_REGION}#gen-ai-observability/agent-core
```

---

## License

MIT
