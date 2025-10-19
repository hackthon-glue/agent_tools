#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Error: .env file not found"
    exit 1
fi

# Validate required variables
if [ -z "$AWS_REGION" ] || [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "Error: AWS_REGION and AWS_ACCOUNT_ID must be set in .env"
    exit 1
fi

# Create execution role
echo "Creating/updating execution role..."
chmod +x "$SCRIPT_DIR/scripts/create-execution-role.sh"
ROLE_ARN=$("$SCRIPT_DIR/scripts/create-execution-role.sh")

# Build ENV_FLAGS
ENV_FLAGS=""
while IFS='=' read -r key value; do
    [[ "$key" =~ ^#.*$ ]] && continue
    [[ -z "$key" ]] && continue
    if [ -n "$value" ]; then
        ENV_FLAGS="$ENV_FLAGS --env $key=$value"
    fi
done < .env

cd agents

# Configure with execution role
echo "Configuring orchestrator agent..."
agentcore configure --entrypoint orchestrator_agent.py --execution-role "$ROLE_ARN"

# Launch
echo "Deploying to AgentCore Runtime..."
agentcore launch --name recruitment-orchestrator $ENV_FLAGS

echo "✅ Deployment complete!"
