#!/bin/bash
set -e

source "$(dirname "$0")/../utils/common.sh"

echo "=== Creating S3 Bucket and Uploading KB Documents ==="

BUCKET_NAME="${PROJECT_NAME}-kb-${AWS_ACCOUNT_ID}"

echo "Creating S3 bucket: $BUCKET_NAME"
aws s3 mb s3://$BUCKET_NAME --region $AWS_REGION 2>/dev/null || echo "  ✓ Already exists"

echo "Uploading Knowledge Base documents from data/criteria..."
aws s3 sync "$(dirname "$0")/../../data/criteria/" s3://$BUCKET_NAME/criteria/ --region $AWS_REGION

echo "✅ S3 bucket created and documents uploaded"
