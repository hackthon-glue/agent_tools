#!/bin/bash
set -e

source "$(dirname "$0")/../utils/common.sh"

echo "=== Creating DynamoDB Tables ==="

TABLES=("recruitment_users:user_id" "recruitment_jobs:job_id" "recruitment_github_profiles:user_id")

for TABLE_DEF in "${TABLES[@]}"; do
    TABLE_NAME="${TABLE_DEF%%:*}"
    KEY_NAME="${TABLE_DEF##*:}"
    
    echo "Creating table: $TABLE_NAME"
    aws dynamodb create-table \
        --table-name $TABLE_NAME \
        --attribute-definitions AttributeName=$KEY_NAME,AttributeType=S \
        --key-schema AttributeName=$KEY_NAME,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST \
        --region $AWS_REGION 2>/dev/null || echo "  ✓ Already exists"
done

echo "Waiting for tables to be active..."
aws dynamodb wait table-exists --table-name recruitment_users --region $AWS_REGION

echo "✅ DynamoDB tables created"
