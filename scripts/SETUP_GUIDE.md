# Setup Guide

Two deployment scenarios for AI Recruitment Platform.

## Scenario 1: Using Existing Resources

**Use Case:** KB, S3, and AOSS already exist from previous setup.

### Prerequisites

- Existing Knowledge Base ID
- Existing S3 bucket with criteria documents
- Existing OpenSearch Serverless collection
- `.env` file configured with existing resource IDs

### Setup Steps

```bash
# 1. Configure .env with existing resources
cp .env.example .env
## Check your Knowledge Base ID and AgentCore Memory ID in AWS Console

# 2. Create IAM role
./scripts/setup/01-create-iam-role.sh

# 3. Create DynamoDB tables
./scripts/setup/02-create-dynamodb.sh

# 4. Load test data
python scripts/setup/06-load-test-data.py

# 5. Deploy agents
./scripts/setup/07-deploy-agentcore.sh
```

### Verification

```bash
# Check DynamoDB tables
aws dynamodb list-tables --region us-west-2

# Check IAM role
aws iam get-role --role-name RecruitmentAgentCoreExecutionRole

# Test agent deployment
agentcore invoke --name recruitment-orchestrator --payload '{"user_id":"user123","request":"test"}'
```

---

## Scenario 2: Complete Setup from Scratch

**Use Case:** No existing resources, full infrastructure deployment.

### Prerequisites

- AWS CLI configured
- Python 3.9+
- AgentCore CLI installed
- pytest installed

### Full Setup

```bash
# 1. Run master setup script (creates all AWS resources)
./scripts/setup/00-setup-all.sh
```

**This creates:**

- IAM Role with policies
- DynamoDB tables (users, jobs, github_profiles)
- S3 bucket with criteria documents
- OpenSearch Serverless collection
- Bedrock Knowledge Base

### Manual Step-by-Step (Alternative)

```bash
# Phase 1: Independent resources (parallel execution possible)
./scripts/setup/01-create-iam-role.sh
./scripts/setup/02-create-dynamodb.sh
./scripts/setup/03-create-s3-kb.sh

# Phase 2: Dependent resources (sequential)
./scripts/setup/04-create-opensearch.sh     # Requires: 01
./scripts/setup/05-create-knowledge-base.sh # Requires: 01, 03, 04

# Phase 3: Data loading
python scripts/setup/06-load-test-data.py

# Phase 4: Integration testing
pytest -m integration

# Phase 5: Agent deployment
./scripts/setup/07-deploy-agentcore.sh

# Phase 6: Acceptance testing
pytest -m acceptance
```

### Verification

```bash
# Check all resources
aws dynamodb list-tables --region us-west-2
aws s3 ls | grep recruitment-agentcore-kb
aws opensearchserverless list-collections --region us-west-2
aws bedrock-agent list-knowledge-bases --region us-west-2

# Verify IAM role
aws iam get-role --role-name RecruitmentAgentCoreExecutionRole

# Test agent
agentcore invoke --name recruitment-orchestrator --payload '{"user_id":"user123","request":"test"}'
```

---

## Resource Cleanup

### Remove All Resources

```bash
./scripts/utils/99-cleanup.sh
```

**Deletion order:**

1. Knowledge Base
2. OpenSearch Collection
3. S3 Bucket (with all objects)
4. DynamoDB Tables
5. IAM Role

### Selective Cleanup

```bash
# Delete only DynamoDB tables
aws dynamodb delete-table --table-name recruitment_users
aws dynamodb delete-table --table-name recruitment_jobs
aws dynamodb delete-table --table-name recruitment_github_profiles

# Delete only Knowledge Base
KB_ID=$(grep KNOWLEDGE_BASE_ID .env | cut -d'=' -f2)
aws bedrock-agent delete-knowledge-base --knowledge-base-id $KB_ID
```

---

## Troubleshooting

### Scenario 1 Issues

**Problem:** IAM role cannot access existing KB/S3/AOSS

```bash
# Update IAM role policies
./scripts/setup/01-create-iam-role.sh

# Verify permissions
aws iam get-role-policy --role-name RecruitmentAgentCoreExecutionRole --policy-name ApplicationPermissions
```

**Problem:** Knowledge Base ID not found

```bash
# List available Knowledge Bases
aws bedrock-agent list-knowledge-bases --region us-west-2

# Update .env with correct ID
echo "KNOWLEDGE_BASE_ID=CORRECT_ID" >> .env
```

### Scenario 2 Issues

**Problem:** OpenSearch collection creation timeout

```bash
# Check collection status
aws opensearchserverless list-collections --region us-west-2

# Wait for ACTIVE status, then retry
./scripts/setup/05-create-knowledge-base.sh
```

**Problem:** S3 bucket already exists

```bash
# Use existing bucket or choose different name
export S3_BUCKET_NAME=recruitment-agentcore-kb-$(date +%s)
./scripts/setup/03-create-s3-kb.sh
```

---

## Environment Variables Reference

### Required for Scenario 1

```bash
KNOWLEDGE_BASE_ID=<existing-kb-id>
S3_BUCKET_NAME=<existing-bucket>
OPENSEARCH_COLLECTION_NAME=<existing-collection>
```

### Auto-generated in Scenario 2

```bash
KNOWLEDGE_BASE_ID=<created-by-script-05>
S3_BUCKET_NAME=recruitment-agentcore-kb-{ACCOUNT_ID}
OPENSEARCH_COLLECTION_NAME=recruitment-kb
```

### Common Variables

```bash
AWS_REGION=us-west-2
AWS_ACCOUNT_ID=<your-account-id>
DYNAMODB_USERS_TABLE=recruitment_users
DYNAMODB_JOBS_TABLE=recruitment_jobs
DYNAMODB_GITHUB_TABLE=recruitment_github_profiles
ROLE_NAME=RecruitmentAgentCoreExecutionRole
```
