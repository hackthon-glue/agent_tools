# Setup Guide

## Prerequisites (All Scenarios)

- AWS CLI configured
- Python 3.9+
- AgentCore CLI installed
- pytest installed

## Quick Reference

```
00-setup-all.sh              ← Master script (Scenario 2 only)
  ├─ 01-create-iam-role.sh
  ├─ 02-create-dynamodb.sh
  ├─ 03-create-s3-kb.sh
  ├─ 04-create-opensearch.sh
  └─ 05-create-knowledge-base.sh

06-load-test-data.py         ← Load test data (both scenarios)
07-deploy-agentcore.sh       ← Deploy to AgentCore (both scenarios)
99-cleanup.sh                ← Delete all resources
```

## Choose Your Scenario

| Scenario       | Use Case            | Infrastructure Created          |
| -------------- | ------------------- | ------------------------------- |
| **Scenario 1** | Existing KB/S3/AOSS | IAM Role + DynamoDB only        |
| **Scenario 2** | From scratch        | IAM + DynamoDB + S3 + AOSS + KB |

---

## Infrastructure Setup

### Scenario 1: Using Existing Resources

**Prerequisites:**

- Existing Knowledge Base ID
- Existing S3 bucket with criteria documents
- Existing OpenSearch Serverless collection

**Steps:**

```bash
# 1. Configure .env with existing resources
cp .env.example .env
# Edit .env: Add KNOWLEDGE_BASE_ID

# 2. Create IAM role
./scripts/setup/01-create-iam-role.sh

# 3. Create DynamoDB tables
./scripts/setup/02-create-dynamodb.sh
```

### Scenario 2: Complete Setup from Scratch

**Automated Setup:**

```bash
# Run master setup script (creates all AWS resources)
./scripts/setup/00-setup-all.sh
```

**Creates:** IAM Role, DynamoDB tables, S3 bucket, OpenSearch Serverless, Bedrock Knowledge Base

**Manual Alternative:**

```bash
# Phase 1: Independent resources (can run in parallel)
./scripts/setup/01-create-iam-role.sh
./scripts/setup/02-create-dynamodb.sh
./scripts/setup/03-create-s3-kb.sh

# Phase 2: Dependent resources (must run sequentially)
./scripts/setup/04-create-opensearch.sh     # Requires: 01
./scripts/setup/05-create-knowledge-base.sh # Requires: 01, 03, 04
```

---

## Script Dependencies

| Script | Depends On | Creates | Used In |
|--------|-----------|---------|----------|
| 01-create-iam-role.sh | None | IAM Role | Both scenarios |
| 02-create-dynamodb.sh | None | DynamoDB Tables | Both scenarios |
| 03-create-s3-kb.sh | None | S3 Bucket + Docs | Scenario 2 only |
| 04-create-opensearch.sh | 01 | OpenSearch Collection | Scenario 2 only |
| 05-create-knowledge-base.sh | 01, 03, 04 | Knowledge Base | Scenario 2 only |
| 06-load-test-data.py | 02 | Test Data | Both scenarios |
| 07-deploy-agentcore.sh | 01-06 | Deployed Agent | Both scenarios |
| 99-cleanup.sh | None | Cleanup | Both scenarios |

---

## Common Deployment Steps (All Scenarios)

### 1. Load Test Data

```bash
python scripts/setup/06-load-test-data.py
```

### 2. Deploy AgentCore Runtime

```bash
./scripts/setup/07-deploy-agentcore.sh
```

**What this script does:**
- Auto-populates AWS_ACCOUNT_ID and AWS_REGION in .env if missing
- Creates/updates IAM execution role
- Excludes AWS_PROFILE from AgentCore Runtime environment
- Configures AgentCore with orchestrator_agent.py entrypoint
- Launches deployment with all .env variables

#### 2.1 Interactive Configuration

The script will prompt for configuration. **Recommended: Press Enter for all defaults.**

| Prompt                   | Default                   | Recommendation                                              |
| ------------------------ | ------------------------- | ----------------------------------------------------------- |
| Agent name               | `orchestrator_agent`      | ✅ Use default                                              |
| Requirements file        | `requirements.txt`        | ✅ Use detected file                                        |
| ECR Repository URI       | Auto-create               | ✅ Press Enter to auto-create                               |
| OAuth authorizer         | No (IAM)                  | ✅ Use IAM (default)                                        |
| Request header allowlist | No                        | ✅ Use default                                              |
| **Memory selection**     | Create new / Use existing | **First time:** Press Enter<br>**Subsequent:** Enter number |

#### 2.2 Build & Deployment Process

**CodeBuild phases (ARM64, ~30-35 seconds total):**

```
✅ QUEUED completed in 1.2s
✅ PROVISIONING completed in 9.4s
✅ DOWNLOAD_SOURCE completed in 1.2s
✅ BUILD completed in 12.9s
✅ POST_BUILD completed in 5.9s
✅ COMPLETED completed in 1.2s
```

**Automated setup:**

- Creates IAM execution role with required permissions
- Configures AgentCore with orchestrator_agent.py entrypoint
- Sets up ECR repository for container images
- Builds and deploys ARM64 container via CodeBuild
- Configures AgentCore Memory for session management
- Enables observability with CloudWatch and X-Ray
- Saves configuration to `agents/.bedrock_agentcore.yaml`

#### 2.3 Deployment Outputs

**Capture these values from the deployment output:**

```
Agent ARN: arn:aws:bedrock-agentcore:{AWS_REGION}:{AWS_ACCOUNT_ID}:runtime/orchestrator_agent-{random_id}
Using existing memory: orchestrator_agent_mem-{random_id}
ECR URI: {AWS_ACCOUNT_ID}.dkr.ecr.{AWS_REGION}.amazonaws.com/bedrock-agentcore-orchestrator_agent:latest
```

**CloudWatch Log Groups:**

```
/aws/bedrock-agentcore/runtimes/orchestrator_agent-{random_id}-DEFAULT
```

**Observability Dashboard:**

```
https://console.aws.amazon.com/cloudwatch/home?region={AWS_REGION}#gen-ai-observability/agent-core
```

### 3. Post-Deployment Configuration

**Extract values from deployment output and update .env:**

```bash
# Example values from deployment output:
echo "ORCHESTRATOR_AGENT_ARN=arn:aws:bedrock-agentcore:{AWS_REGION}:{AWS_ACCOUNT_ID}:runtime/orchestrator_agent-{random_id}" >> .env
echo "AGENTCORE_MEMORY_ID=orchestrator_agent_mem-{random_id}" >> .env
```

**Or manually edit .env:**

```bash
ORCHESTRATOR_AGENT_ARN=arn:aws:bedrock-agentcore:{AWS_REGION}:{AWS_ACCOUNT_ID}:runtime/orchestrator_agent-{random_id}
AGENTCORE_MEMORY_ID=orchestrator_agent_mem-{random_id}
```

### 4. Verification

```bash
# Check deployment status
cd agents && agentcore status

# Basic test
agentcore invoke '{"prompt": "Hello"}'

# Full test
agentcore invoke '{
  "user_id": "user123",
  "request": "Looking for job opportunities",
  "session_id": "session123"
}'
```

**Verify resources:**

```bash
# DynamoDB tables
aws dynamodb list-tables --region {AWS_REGION}

# IAM role
aws iam get-role --role-name RecruitmentAgentCoreExecutionRole

# Scenario 2 only: KB/S3/AOSS
aws s3 ls | grep recruitment-agentcore-kb
aws opensearchserverless list-collections --region {AWS_REGION}
aws bedrock-agent list-knowledge-bases --region {AWS_REGION}
```

### 5. Monitor Logs

```bash
# Replace orchestrator_agent-XXXXX with your actual Agent ARN suffix
# Example: orchestrator_agent-{random_id}

# Tail runtime logs
aws logs tail /aws/bedrock-agentcore/runtimes/orchestrator_agent-{random_id}-DEFAULT \
  --log-stream-name-prefix "2025/10/19/[runtime-logs]" --follow

# View recent logs (last hour)
aws logs tail /aws/bedrock-agentcore/runtimes/orchestrator_agent-{random_id}-DEFAULT \
  --log-stream-name-prefix "2025/10/19/[runtime-logs]" --since 1h

# View OpenTelemetry logs
aws logs tail /aws/bedrock-agentcore/runtimes/orchestrator_agent-{random_id}-DEFAULT \
  --log-stream-names "otel-rt-logs"
```

### 6. Observability Dashboard

```
https://console.aws.amazon.com/cloudwatch/home?region={AWS_REGION}#gen-ai-observability/agent-core
```

**Note:** Data may take up to 10 minutes to appear after first deployment.

### 7. Update Agent Code

```bash
cd agents
agentcore launch  # Uses existing configuration
```

---

## Resource Cleanup

```bash
# Remove all resources
./scripts/utils/99-cleanup.sh
```

**Deletion order:** Knowledge Base → OpenSearch → S3 → DynamoDB → IAM Role

**Selective cleanup:**

```bash
# DynamoDB only
aws dynamodb delete-table --table-name recruitment_users
aws dynamodb delete-table --table-name recruitment_jobs
aws dynamodb delete-table --table-name recruitment_github_profiles

# Knowledge Base only (Scenario 2)
KB_ID=$(grep KNOWLEDGE_BASE_ID .env | cut -d'=' -f2)
aws bedrock-agent delete-knowledge-base --knowledge-base-id $KB_ID
```

---

## Troubleshooting

**[Scenario 1] IAM role cannot access existing KB/S3/AOSS**

```bash
./scripts/setup/01-create-iam-role.sh
aws iam get-role-policy --role-name RecruitmentAgentCoreExecutionRole --policy-name ApplicationPermissions
```

**[Scenario 1] Knowledge Base ID not found**

```bash
aws bedrock-agent list-knowledge-bases --region {AWS_REGION}
echo "KNOWLEDGE_BASE_ID=CORRECT_ID" >> .env
```

**[Scenario 2] OpenSearch collection creation timeout**

```bash
aws opensearchserverless list-collections --region {AWS_REGION}
# Wait for ACTIVE status, then retry
./scripts/setup/05-create-knowledge-base.sh
```

**[Scenario 2] S3 bucket already exists**

```bash
export S3_BUCKET_NAME=recruitment-agentcore-kb-$(date +%s)
./scripts/setup/03-create-s3-kb.sh
```

**[All Scenarios] CodeBuild timeout or failure**

```bash
# Check CodeBuild project status
aws codebuild list-projects | grep bedrock-agentcore

# View build logs
aws codebuild batch-get-builds --ids <build-id>

# Retry deployment
cd agents && agentcore launch
```

**[All Scenarios] Memory configuration issues**

```bash
# List existing memories
aws bedrock-agentcore list-memories --region {AWS_REGION}

# Reconfigure with new memory
cd agents
agentcore configure --entrypoint orchestrator_agent.py
# Select "Press Enter to create new memory" when prompted
```

**[All Scenarios] AWS_PROFILE error in AgentCore Runtime**

```bash
# Error: The config profile (admin) could not be found
# Cause: AWS_PROFILE in .env is not needed for AgentCore Runtime

# Solution: Remove AWS_PROFILE from deployment
# The script now automatically excludes AWS_PROFILE
./scripts/setup/07-deploy-agentcore.sh

# Or manually remove from .env (for local testing only)
# Comment out: # AWS_PROFILE=admin
```

**[All Scenarios] AgentCore Memory AccessDeniedException**

```bash
# Error: User is not authorized to perform: bedrock-agentcore:ListEvents
# Cause: IAM role missing ListEvents permission for AgentCore Memory

# Solution: Update IAM role with missing permissions
./scripts/setup/01-create-iam-role.sh

# Then redeploy
./scripts/setup/07-deploy-agentcore.sh
```

**[All Scenarios] Cross-region Bedrock model access denied**

```bash
# Error: not authorized to perform: bedrock:InvokeModelWithResponseStream on resource: arn:aws:bedrock:us-east-1::foundation-model/*
# Cause: IAM policy restricts models to deployment region only

# Solution: Update IAM role to allow cross-region model access
./scripts/setup/01-create-iam-role.sh

# Then redeploy
./scripts/setup/07-deploy-agentcore.sh
```

**[All Scenarios] Agent tool invocation missing required arguments**

```bash
# Error: Tool invocation fails with missing argument errors
# Cause: Orchestrator calling agent tools without required parameters

# Solution: Update agent code and redeploy
cd agents
agentcore launch
```

---

## Environment Variables

### Common Variables (All Scenarios)

```bash
AWS_REGION={AWS_REGION}
AWS_ACCOUNT_ID=<your-account-id>
DYNAMODB_USERS_TABLE=recruitment_users
DYNAMODB_JOBS_TABLE=recruitment_jobs
DYNAMODB_GITHUB_TABLE=recruitment_github_profiles
ROLE_NAME=RecruitmentAgentCoreExecutionRole
ORCHESTRATOR_AGENT_ARN=<from-deployment-output>
AGENTCORE_MEMORY_ID=<from-deployment-output>
```

### Scenario-Specific Variables

| Variable                     | Scenario 1              | Scenario 2                              |
| ---------------------------- | ----------------------- | --------------------------------------- |
| `KNOWLEDGE_BASE_ID`          | `<existing-kb-id>`      | `<created-by-script-05>`                |
| `S3_BUCKET_NAME`             | `<existing-bucket>`     | `recruitment-agentcore-kb-{ACCOUNT_ID}` |
| `OPENSEARCH_COLLECTION_NAME` | `<existing-collection>` | `recruitment-kb`                        |
