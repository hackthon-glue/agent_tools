#!/bin/bash
set -e

source "$(dirname "$0")/../utils/common.sh"

BUCKET_NAME="${PROJECT_NAME}-kb-${AWS_ACCOUNT_ID}"
KB_NAME="recruitment-evaluation-kb"
ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}"

echo "=== Creating Bedrock Knowledge Base ==="

# Check OpenSearch collection
COLLECTION_ID=$(aws opensearchserverless list-collections \
    --region $AWS_REGION \
    --query "collectionSummaries[?name=='recruitment-kb'].id" \
    --output text 2>/dev/null || echo "")

if [ -z "$COLLECTION_ID" ]; then
    echo "❌ OpenSearch collection 'recruitment-kb' not found"
    echo "   Run: ./scripts/setup/03.5-create-opensearch.sh"
    exit 1
fi

COLLECTION_ARN="arn:aws:aoss:${AWS_REGION}:${AWS_ACCOUNT_ID}:collection/${COLLECTION_ID}"
echo "  ✓ OpenSearch collection found: $COLLECTION_ID"

# Check if KB already exists
EXISTING_KB=$(aws bedrock-agent list-knowledge-bases \
    --region $AWS_REGION \
    --query "knowledgeBaseSummaries[?name=='$KB_NAME'].knowledgeBaseId" \
    --output text 2>/dev/null || echo "")

if [ -n "$EXISTING_KB" ]; then
    echo "  ✓ Knowledge Base already exists: $EXISTING_KB"
    echo "KNOWLEDGE_BASE_ID=$EXISTING_KB" >> .env
    exit 0
fi

echo "Creating Knowledge Base: $KB_NAME"

KB_ID=$(aws bedrock-agent create-knowledge-base \
    --name $KB_NAME \
    --role-arn $ROLE_ARN \
    --knowledge-base-configuration "type=VECTOR,vectorKnowledgeBaseConfiguration={embeddingModelArn=arn:aws:bedrock:${AWS_REGION}::foundation-model/amazon.titan-embed-text-v1}" \
    --storage-configuration "type=OPENSEARCH_SERVERLESS,opensearchServerlessConfiguration={collectionArn=${COLLECTION_ARN},vectorIndexName=recruitment-index,fieldMapping={vectorField=vector,textField=text,metadataField=metadata}}" \
    --region $AWS_REGION \
    --query 'knowledgeBase.knowledgeBaseId' \
    --output text 2>/dev/null || echo "")

if [ -z "$KB_ID" ]; then
    echo "❌ Knowledge Base creation failed"
    exit 1
fi

echo "  ✓ Knowledge Base created: $KB_ID"
echo "KNOWLEDGE_BASE_ID=$KB_ID" >> .env

# Create data source
echo "Creating data source..."
DATA_SOURCE_ID=$(aws bedrock-agent create-data-source \
    --knowledge-base-id $KB_ID \
    --name "s3-criteria-docs" \
    --data-source-configuration "type=S3,s3Configuration={bucketArn=arn:aws:s3:::${BUCKET_NAME},inclusionPrefixes=[criteria/]}" \
    --region $AWS_REGION \
    --query 'dataSource.dataSourceId' \
    --output text 2>/dev/null || echo "")

if [ -z "$DATA_SOURCE_ID" ]; then
    echo "  ⚠ Data source creation failed (may already exist)"
else
    echo "  ✓ Data source created: $DATA_SOURCE_ID"
    
    # Start ingestion
    echo "Starting ingestion job..."
    aws bedrock-agent start-ingestion-job \
        --knowledge-base-id $KB_ID \
        --data-source-id $DATA_SOURCE_ID \
        --region $AWS_REGION >/dev/null 2>&1 && echo "  ✓ Ingestion started" || echo "  ⚠ Ingestion failed"
fi

echo ""
echo "✅ Knowledge Base setup complete: $KB_ID"
