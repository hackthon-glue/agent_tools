#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROLE_NAME="RecruitmentAgentCoreExecutionRole"

if [ -z "$AWS_REGION" ] || [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "Error: AWS_REGION and AWS_ACCOUNT_ID must be set"
    exit 1
fi

echo "Creating execution role: $ROLE_NAME"

# Generate policies from templates
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

python3 "$SCRIPT_DIR/generate-from-template.py" \
    "$SCRIPT_DIR/policies/trust-policy.json" \
    "$TEMP_DIR/trust-policy.json"

python3 "$SCRIPT_DIR/generate-from-template.py" \
    "$SCRIPT_DIR/policies/runtime-execution-policy.json" \
    "$TEMP_DIR/runtime-execution-policy.json"

TRUST_POLICY=$(cat "$TEMP_DIR/trust-policy.json")
RUNTIME_POLICY=$(cat "$TEMP_DIR/runtime-execution-policy.json")

# Create role
if aws iam get-role --role-name "$ROLE_NAME" 2>/dev/null; then
    echo "Role already exists, updating policies..."
else
    echo "Creating new role..."
    aws iam create-role \
        --role-name "$ROLE_NAME" \
        --assume-role-policy-document "$TRUST_POLICY" \
        --description "Execution role for Recruitment AgentCore agents"
fi

# Attach inline policy
aws iam put-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-name "RecruitmentAgentCorePolicy" \
    --policy-document "$RUNTIME_POLICY"

ROLE_ARN=$(aws iam get-role --role-name "$ROLE_NAME" --query 'Role.Arn' --output text)
echo "✅ Role created/updated: $ROLE_ARN"
echo "$ROLE_ARN"
