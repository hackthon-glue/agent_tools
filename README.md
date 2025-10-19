# AI Recruitment Platform - AgentCore Edition

AI Agent Platform for Enterprise HR Systems (AWS Bedrock AgentCore + Strands)

## Overview

Orchestrator integrates 4 specialized agents:

**Orchestrator Agent** - Main coordinator (integrates all agents)

Specialized Agents:

1. **Concierge Agent** - Career consultation & job search (AgentCore Memory)
2. **Skill Parser Agent** - Resume & GitHub analysis (PDF Tools)
3. **Job Matcher Agent** - Candidate × Job matching (Knowledge Base)
4. **Interviewer Copilot Agent** - Interview support (AgentCore Memory)

## Architecture

```
agents/
├── orchestrator_agent.py       # Main orchestrator
├── concierge_agent.py          # Conversational agent (Memory)
├── skill_parser_agent.py       # Skill analysis
├── job_matcher_agent.py        # Matching (KB)
├── interviewer_copilot_agent.py # Interview support (Memory)
├── memory_hook.py              # AgentCore Memory Hook
└── tools/
    ├── dynamodb_tools.py       # DynamoDB access
    ├── kb_tools.py             # Knowledge Base
    ├── memory_tools.py         # AgentCore Memory
    ├── pdf_tools.py            # PDF parsing
    ├── agent_tools.py          # Agent invocation
    ├── collector_tools.py      # Web Collectors
    └── collectors/             # Collector implementations
        ├── linkedin.py
        ├── github.py
        ├── job_market.py
        └── candidate_search.py
```

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment variables
export AWS_REGION=us-west-2
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

## Local Testing

```bash
# Unit tests
pytest tests/test_agents.py -v
pytest tests/test_orchestrator.py -v

# Integration tests
python test_local.py

# Individual agent tests
python agents/concierge_agent.py
```

## DynamoDB Table Schema

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

## Knowledge Base Configuration

Evaluation criteria documents:

- Skill matching criteria
- Years of experience evaluation
- Cultural fit indicators

## AgentCore Memory Features

### Memory Hook Integration

- **MemoryHook**: Strands HookProvider implementation
- **on_agent_initialized**: Load past conversation history
- **on_message_added**: Auto-save new messages

### Session Configuration

- **Concierge Agent**: 1-hour session (conversation history)
- **Interviewer Copilot**: 30-minute session (interview context)
- **Default K value**: Retrieve last 3 conversation turns

## Tech Stack

### Core Framework

- **AWS Bedrock AgentCore**: Runtime, Memory, Gateway
- **Strands**: Agent framework
- **Claude 3.5 Sonnet v2**: LLM model (us.anthropic.claude-3-5-sonnet-20241022-v2:0)

### Tool Integration

- **Sequential Thinking**: Reasoning tool for complex tasks
- **AgentCore Memory**: Session management & conversation history
- **Context7**: Library documentation search
- **AWS Docs**: AWS official documentation search

### Data Stores

- **DynamoDB**: Users, jobs, GitHub profiles
- **Bedrock Knowledge Base**: Evaluation criteria & matching rules

### Web Collectors

- **LinkedIn Collector**: Profiles & job postings
- **GitHub Collector**: Repositories & contributions
- **Job Market Collector**: Job market data
- **Candidate Search Collector**: Candidate search

## License

MIT
