#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Load .env
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
else
    echo "Error: .env file not found in $PROJECT_ROOT"
    exit 1
fi

# Auto-populate AWS_ACCOUNT_ID if missing
if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "AWS_ACCOUNT_ID not found in .env. Retrieving from AWS..."
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    echo "AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID" >> "$PROJECT_ROOT/.env"
    echo "✓ Added AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID to .env"
fi

# Auto-populate AWS_REGION if missing
if [ -z "$AWS_REGION" ]; then
    echo "AWS_REGION not found in .env. Using default region..."
    AWS_REGION=$(aws configure get region || echo "us-west-2")
    echo "AWS_REGION=$AWS_REGION" >> "$PROJECT_ROOT/.env"
    echo "✓ Added AWS_REGION=$AWS_REGION to .env"
fi

# Validate required variables
if [ -z "$AWS_REGION" ] || [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "Error: AWS_REGION and AWS_ACCOUNT_ID must be set in .env"
    exit 1
fi

# Create execution role
echo "Creating/updating execution role..."
chmod +x "$SCRIPT_DIR/01-create-iam-role.sh"
ROLE_ARN=$("$SCRIPT_DIR/01-create-iam-role.sh")

# Build ENV_FLAGS (exclude AWS_PROFILE for AgentCore Runtime)
ENV_FLAGS=""
while IFS='=' read -r key value; do
    [[ "$key" =~ ^#.*$ ]] && continue
    [[ -z "$key" ]] && continue
    [[ "$key" == "AWS_PROFILE" ]] && continue  # Skip AWS_PROFILE
    if [ -n "$value" ]; then
        ENV_FLAGS="$ENV_FLAGS --env $key=$value"
    fi
done < "$PROJECT_ROOT/.env"

cd "$PROJECT_ROOT/agents"

# Copy requirements.txt if not exists or if source is newer
if [ ! -f requirements.txt ] || [ "$PROJECT_ROOT/requirements.txt" -nt requirements.txt ]; then
    cp "$PROJECT_ROOT/requirements.txt" requirements.txt
fi

# Configure with execution role
echo "Configuring orchestrator agent..."
agentcore configure --entrypoint orchestrator_agent.py --execution-role "$ROLE_ARN"

# Launch
echo "Deploying to AgentCore Runtime..."
agentcore launch $ENV_FLAGS

echo "✅ Deployment complete!"
