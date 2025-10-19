#!/bin/bash
set -e

source "$(dirname "$0")/../utils/common.sh"

echo "=== Creating OpenSearch Serverless Collection ==="

COLLECTION_NAME="recruitment-kb"

# Check if collection exists
EXISTING=$(aws opensearchserverless list-collections \
    --region $AWS_REGION \
    --query "collectionSummaries[?name=='$COLLECTION_NAME'].id" \
    --output text 2>/dev/null || echo "")

if [ -n "$EXISTING" ]; then
    echo "  ✓ Collection already exists: $COLLECTION_NAME"
    exit 0
fi

# Create encryption policy
cat > /tmp/encryption-policy.json <<EOF
{
  "Rules": [
    {
      "ResourceType": "collection",
      "Resource": ["collection/$COLLECTION_NAME"]
    }
  ],
  "AWSOwnedKey": true
}
EOF

aws opensearchserverless create-security-policy \
    --name "${COLLECTION_NAME}-encryption" \
    --type encryption \
    --policy file:///tmp/encryption-policy.json \
    --region $AWS_REGION 2>/dev/null || echo "  ✓ Encryption policy exists"

# Create network policy
cat > /tmp/network-policy.json <<EOF
[
  {
    "Rules": [
      {
        "ResourceType": "collection",
        "Resource": ["collection/$COLLECTION_NAME"]
      }
    ],
    "AllowFromPublic": true
  }
]
EOF

aws opensearchserverless create-security-policy \
    --name "${COLLECTION_NAME}-network" \
    --type network \
    --policy file:///tmp/network-policy.json \
    --region $AWS_REGION 2>/dev/null || echo "  ✓ Network policy exists"

# Create data access policy
cat > /tmp/data-access-policy.json <<EOF
[
  {
    "Rules": [
      {
        "ResourceType": "collection",
        "Resource": ["collection/$COLLECTION_NAME"],
        "Permission": ["aoss:*"]
      },
      {
        "ResourceType": "index",
        "Resource": ["index/$COLLECTION_NAME/*"],
        "Permission": ["aoss:*"]
      }
    ],
    "Principal": [
      "arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}"
    ]
  }
]
EOF

aws opensearchserverless create-access-policy \
    --name "${COLLECTION_NAME}-access" \
    --type data \
    --policy file:///tmp/data-access-policy.json \
    --region $AWS_REGION 2>/dev/null || echo "  ✓ Access policy exists"

# Create collection
echo "Creating OpenSearch Serverless collection..."
COLLECTION_ID=$(aws opensearchserverless create-collection \
    --name $COLLECTION_NAME \
    --type VECTORSEARCH \
    --region $AWS_REGION \
    --query 'createCollectionDetail.id' \
    --output text 2>/dev/null || echo "")

if [ -z "$COLLECTION_ID" ]; then
    echo "  ✓ Collection already exists"
    COLLECTION_ID=$(aws opensearchserverless list-collections \
        --region $AWS_REGION \
        --query "collectionSummaries[?name=='$COLLECTION_NAME'].id" \
        --output text)
fi

echo "Waiting for collection to be active..."
sleep 30

echo "✅ OpenSearch Serverless collection created: $COLLECTION_NAME"
echo "Collection ID: $COLLECTION_ID"
