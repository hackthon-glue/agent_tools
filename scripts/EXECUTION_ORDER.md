# Script Execution Order

## Quick Reference

```
00-setup-all.sh              ← Master script (runs 01-05 automatically)
  ├─ 01-create-iam-role.sh
  ├─ 02-create-dynamodb.sh
  ├─ 03-create-s3-kb.sh
  ├─ 04-create-opensearch.sh
  └─ 05-create-knowledge-base.sh

06-load-test-data.py         ← Load test data
07-deploy-all-agents.sh      ← Deploy to AgentCore
99-cleanup.sh                ← Delete all resources
```

## Execution Flow

### Phase 1: Infrastructure Setup (Parallel)
```bash
./scripts/setup/01-create-iam-role.sh       # IAM Role + Policies
./scripts/setup/02-create-dynamodb.sh       # DynamoDB Tables
./scripts/setup/03-create-s3-kb.sh          # S3 Bucket + Upload docs
```

### Phase 2: Dependent Resources (Sequential)
```bash
./scripts/setup/04-create-opensearch.sh     # Requires: 01
./scripts/setup/05-create-knowledge-base.sh # Requires: 01, 03, 04
```

### Phase 3: Data Loading
```bash
python scripts/setup/06-load-test-data.py   # Requires: 02
```

### Phase 4: Integration Testing
```bash
pytest -m integration                       # Requires: 01, 02, 05
```

### Phase 5: Deployment
```bash
./scripts/setup/07-deploy-all-agents.sh     # Requires: all phases
```

### Phase 6: Acceptance Testing
```bash
pytest -m acceptance                        # Requires: deployed agents
```

## One-Command Setup

```bash
./scripts/setup/00-setup-all.sh             # Runs phases 1-2
python scripts/setup/06-load-test-data.py   # Phase 3
pytest -m integration                       # Phase 4
./scripts/setup/07-deploy-all-agents.sh     # Phase 5
pytest -m acceptance                        # Phase 6
```

## Cleanup

```bash
./scripts/utils/99-cleanup.sh               # Delete all resources
```

## Dependencies

| Script | Depends On | Creates |
|--------|-----------|---------|
| 01 | None | IAM Role |
| 02 | None | DynamoDB Tables |
| 03 | None | S3 Bucket + Docs |
| 04 | 01 | OpenSearch Collection |
| 05 | 01, 03, 04 | Knowledge Base |
| 06 | 02 | Test Data |
| 07 | 01-06 | Deployed Agents |
| 99 | None | Cleanup |
