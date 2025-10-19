# IAM Policies for Recruitment AgentCore

## Required Permissions

### DynamoDB
- **Tables**: Configurable via environment variables (defaults: recruitment_users, recruitment_jobs, recruitment_github_profiles)
- **Actions**: GetItem, PutItem, UpdateItem, Query, Scan

### Bedrock Knowledge Base
- **Actions**: Retrieve, Rerank, RetrieveAndGenerate
- **Resources**: All knowledge bases in account

### AgentCore Memory
- **Actions**: CreateEvent, GetLastKTurns, GetMemory, CreateMemory
- **Resources**: All memories in account

### Textract
- **Actions**: AnalyzeDocument, DetectDocumentText
- **Resources**: All (document processing)

### Bedrock Runtime
- **Foundation Models**: Claude (all versions), Nova (all versions)
- **Inference Profiles**: Cross-region and application inference profiles
- **Actions**: InvokeModel, InvokeModelWithResponseStream

## Environment Variables

Required in `.env`:
- `AWS_REGION` - AWS region
- `AWS_ACCOUNT_ID` - AWS account ID

Optional (with defaults):
- `DYNAMODB_USERS_TABLE` (default: recruitment_users)
- `DYNAMODB_JOBS_TABLE` (default: recruitment_jobs)
- `DYNAMODB_GITHUB_TABLE` (default: recruitment_github_profiles)

## Files

- `runtime-execution-policy.json`: Main execution policy for AgentCore Runtime
- `trust-policy.json`: Trust relationship allowing bedrock-agentcore.amazonaws.com to assume role

## Usage

Run `./deploy.sh` which automatically:
1. Creates/updates execution role with required permissions
2. Configures AgentCore with the role
3. Deploys the agent

## Manual Role Creation

```bash
export AWS_REGION=us-west-2
export AWS_ACCOUNT_ID=123456789012
./scripts/create-execution-role.sh
```
