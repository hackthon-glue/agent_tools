#!/bin/bash
set -e

source "$(dirname "$0")/common.sh"

echo "=== Cleaning Up AWS Resources ==="

read -p "This will delete all resources. Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# DynamoDB
for TABLE in recruitment_users recruitment_jobs recruitment_github_profiles; do
    echo "Deleting table: $TABLE"
    aws dynamodb delete-table --table-name $TABLE --region $AWS_REGION 2>/dev/null || true
done

# S3
BUCKET_NAME="${PROJECT_NAME}-kb-${AWS_ACCOUNT_ID}"
echo "Deleting S3 bucket: $BUCKET_NAME"
aws s3 rb s3://$BUCKET_NAME --force 2>/dev/null || true

# Knowledge Base
if [ -n "$KNOWLEDGE_BASE_ID" ]; then
    echo "Deleting Knowledge Base: $KNOWLEDGE_BASE_ID"
    aws bedrock-agent delete-knowledge-base --knowledge-base-id $KNOWLEDGE_BASE_ID --region $AWS_REGION 2>/dev/null || true
fi

# OpenSearch Serverless
COLLECTION_ID=$(aws opensearchserverless list-collections \
    --region $AWS_REGION \
    --query "collectionSummaries[?name=='recruitment-kb'].id" \
    --output text 2>/dev/null || echo "")

if [ -n "$COLLECTION_ID" ]; then
    echo "Deleting OpenSearch collection: recruitment-kb"
    aws opensearchserverless delete-collection --id $COLLECTION_ID --region $AWS_REGION 2>/dev/null || true
    
    echo "Deleting OpenSearch policies..."
    aws opensearchserverless delete-security-policy --name recruitment-kb-encryption --type encryption --region $AWS_REGION 2>/dev/null || true
    aws opensearchserverless delete-security-policy --name recruitment-kb-network --type network --region $AWS_REGION 2>/dev/null || true
    aws opensearchserverless delete-access-policy --name recruitment-kb-access --type data --region $AWS_REGION 2>/dev/null || true
fi

echo "✅ Cleanup complete"
