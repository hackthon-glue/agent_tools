#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=========================================="
echo "  AWS Resources Setup - All Steps"
echo "=========================================="
echo ""

echo "[1/5] Creating IAM Role..."
"$SCRIPT_DIR/01-create-iam-role.sh"
echo ""

echo "[2/5] Creating DynamoDB Tables..."
"$SCRIPT_DIR/02-create-dynamodb.sh"
echo ""

echo "[3/5] Creating S3 Bucket and Uploading Documents..."
"$SCRIPT_DIR/03-create-s3-kb.sh"
echo ""

echo "[4/5] Creating OpenSearch Serverless Collection..."
"$SCRIPT_DIR/04-create-opensearch.sh"
echo ""

echo "[5/5] Creating Bedrock Knowledge Base..."
"$SCRIPT_DIR/05-create-knowledge-base.sh"
echo ""

echo "=========================================="
echo "✅ All AWS resources created successfully"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Load test data: python scripts/setup/06-load-test-data.py"
echo "  2. Run integration tests: pytest -m integration"
echo "  3. Deploy agents: ./scripts/setup/07-deploy-all-agents.sh"
