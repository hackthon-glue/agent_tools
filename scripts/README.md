# Scripts Directory

Infrastructure setup and deployment scripts for AI Recruitment Platform.

**📖 See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup instructions (existing resources vs. from scratch)**

## Directory Structure

```
scripts/
├── README.md                       # This file
├── setup/                          # AWS resource setup & deployment
│   ├── 00-setup-all.sh            # Run all setup steps (master script)
│   ├── 01-create-iam-role.sh      # IAM role + policies
│   ├── 02-create-dynamodb.sh      # DynamoDB tables
│   ├── 03-create-s3-kb.sh         # S3 bucket + upload criteria docs
│   ├── 04-create-opensearch.sh    # OpenSearch Serverless collection
│   ├── 05-create-knowledge-base.sh # Bedrock Knowledge Base
│   ├── 06-load-test-data.py       # Load test data to DynamoDB
│   └── 07-deploy-all-agents.sh    # Deploy agents to AgentCore Runtime
├── utils/
│   ├── common.sh                  # Shared variables/functions
│   └── 99-cleanup.sh              # Delete all resources
└── policies/                       # IAM policy documentation
    ├── POLICIES.md
    ├── runtime-execution-policy.json
    └── trust-policy.json
```

## Quick Start

### Full Setup (Recommended)

```bash
# 1. Setup all AWS resources
./scripts/setup/00-setup-all.sh

# 2. Load test data
python scripts/setup/06-load-test-data.py

# 3. Run integration tests
pytest -m integration

# 4. Deploy agents to AgentCore
./scripts/setup/07-deploy-all-agents.sh

# 5. Run acceptance tests
pytest -m acceptance
```

### Step-by-Step Setup

```bash
# Phase 1: Independent resources (can run in parallel)
./scripts/setup/01-create-iam-role.sh
./scripts/setup/02-create-dynamodb.sh
./scripts/setup/03-create-s3-kb.sh

# Phase 2: Dependent resources (sequential)
./scripts/setup/04-create-opensearch.sh     # Requires: 01
./scripts/setup/05-create-knowledge-base.sh # Requires: 01, 03, 04

# Phase 3: Data loading
python scripts/setup/06-load-test-data.py   # Requires: 02

# Phase 4: Testing
pytest -m integration                       # Requires: 01, 02, 05

# Phase 5: Deployment
./scripts/setup/07-deploy-all-agents.sh     # Requires: all phases

# Phase 6: Acceptance testing
pytest -m acceptance                        # Requires: deployed agents
```

## Prerequisites

- AWS CLI configured with credentials
- Python 3.9+
- pytest installed
- `.env` file with AWS_REGION (optional, defaults to us-west-2)

## Script Dependencies

### 01-create-iam-role.sh
**Creates:** IAM Role `RecruitmentAgentCoreExecutionRole` with policies for DynamoDB, Bedrock, Textract, S3, OpenSearch  
**Dependencies:** None  
**Permissions:** `iam:CreateRole`, `iam:AttachRolePolicy`, `iam:PutRolePolicy`

### 02-create-dynamodb.sh
**Creates:** Tables `recruitment_users`, `recruitment_jobs`, `recruitment_github_profiles`  
**Dependencies:** None  
**Permissions:** `dynamodb:CreateTable`

### 03-create-s3-kb.sh
**Creates:** S3 bucket `recruitment-agentcore-kb-{ACCOUNT_ID}`, uploads `data/criteria/*.md`  
**Dependencies:** None  
**Permissions:** `s3:CreateBucket`, `s3:PutObject`

### 04-create-opensearch.sh
**Creates:** OpenSearch Serverless collection `recruitment-kb` with encryption, network, and data access policies  
**Dependencies:** 01-create-iam-role.sh (IAM role for data access policy)  
**Permissions:** `aoss:CreateCollection`, `aoss:CreateSecurityPolicy`, `aoss:CreateAccessPolicy`  
**Wait Time:** 30 seconds for collection activation

### 05-create-knowledge-base.sh
**Creates:** Bedrock Knowledge Base `recruitment-evaluation-kb` with S3 data source  
**Dependencies:** 01-create-iam-role.sh (IAM role), 03-create-s3-kb.sh (S3 bucket), 04-create-opensearch.sh (OpenSearch collection)  
**Permissions:** `bedrock:CreateKnowledgeBase`, `bedrock:CreateDataSource`, `bedrock:StartIngestionJob`  
**Output:** Writes `KNOWLEDGE_BASE_ID` to `.env`

### 06-load-test-data.py
**Creates:** 2 test users, 2 test jobs, 1 GitHub profile  
**Dependencies:** 02-create-dynamodb.sh (DynamoDB tables)  
**Permissions:** `dynamodb:PutItem`

### 07-deploy-all-agents.sh
**Deploys:** All 5 agents (orchestrator, concierge, skill_parser, job_matcher, interviewer_copilot)  
**Dependencies:** All setup phases completed  
**Requires:** AgentCore CLI installed

## Resource Details

### DynamoDB Tables
- `recruitment_users` (PK: user_id) - User profiles
- `recruitment_jobs` (PK: job_id) - Job postings
- `recruitment_github_profiles` (PK: user_id) - GitHub data

### Knowledge Base Documents
Uploaded from `data/criteria/`:
- benefits_and_compensation.md
- company_overview.md
- hiring_process_and_standards.md
- interview_guidlines.md
- job_roles_and_requirements.md
- tech_skills_matrix.md

### IAM Permissions
See [policies/POLICIES.md](policies/POLICIES.md) for detailed permission requirements.

## Error Handling

All scripts implement:
- **Idempotency**: Safe to run multiple times
- **Existence checks**: Skip if resource already exists
- **Dependency validation**: Exit with error if required resources missing

## Cleanup

Delete all created resources:

```bash
./scripts/utils/99-cleanup.sh
```

**Cleanup order:**
1. Knowledge Base
2. OpenSearch Collection
3. S3 Bucket
4. DynamoDB Tables
5. IAM Role (last)

## Troubleshooting

### DynamoDB Table Creation Failed
```bash
# Check existing tables
aws dynamodb list-tables --region us-west-2

# Delete if needed
aws dynamodb delete-table --table-name recruitment_users --region us-west-2
```

### Knowledge Base Creation Error
```bash
# Verify OpenSearch collection exists
aws opensearchserverless list-collections --region us-west-2
```

### IAM Permission Issues
```bash
# Check attached policies
aws iam list-attached-role-policies --role-name RecruitmentAgentCoreExecutionRole

# Verify inline policies
aws iam list-role-policies --role-name RecruitmentAgentCoreExecutionRole
```

## Environment Variables

Create `.env` file (optional):
```bash
AWS_REGION=us-west-2
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
DYNAMODB_USERS_TABLE=recruitment_users
DYNAMODB_JOBS_TABLE=recruitment_jobs
DYNAMODB_GITHUB_TABLE=recruitment_github_profiles
```

Defaults are provided if not specified.
