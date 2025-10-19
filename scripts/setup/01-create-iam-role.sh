#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../utils/common.sh"

echo "Creating IAM role: $ROLE_NAME"

# Generate policies from templates
chmod +x "$SCRIPT_DIR/../utils/generate-template.py"
"$SCRIPT_DIR/../utils/generate-template.py" "$SCRIPT_DIR/../policies" "/tmp/policies"

# Create role
aws iam create-role \
    --role-name $ROLE_NAME \
    --assume-role-policy-document file:///tmp/policies/trust-policy.json 2>/dev/null || echo "Role exists"

# Attach base runtime policy
aws iam put-role-policy \
    --role-name $ROLE_NAME \
    --policy-name AgentCoreRuntimeBase \
    --policy-document file:///tmp/policies/agentcore-runtime-base-policy.json

# Attach application permissions policy
aws iam put-role-policy \
    --role-name $ROLE_NAME \
    --policy-name ApplicationPermissions \
    --policy-document file:///tmp/policies/application-permissions-policy.json

echo "✅ IAM role created: arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}"
echo "arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}"
