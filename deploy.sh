#!/bin/bash
set -e

# .envファイルから環境変数を読み込んで--envフラグを生成
ENV_FLAGS=""
if [ -f .env ]; then
    while IFS='=' read -r key value; do
        # コメント行と空行をスキップ
        [[ "$key" =~ ^#.*$ ]] && continue
        [[ -z "$key" ]] && continue
        
        # 値が空でない場合のみ追加
        if [ -n "$value" ]; then
            ENV_FLAGS="$ENV_FLAGS --env $key=$value"
        fi
    done < .env
else
    echo "Error: .env file not found"
    echo "Please create .env from .env.example"
    exit 1
fi

cd agents

# Configure
echo "Configuring orchestrator agent..."
agentcore configure --entrypoint orchestrator_agent.py

# Launch with environment variables
echo "Deploying to AgentCore Runtime..."
agentcore launch --name recruitment-orchestrator $ENV_FLAGS

echo "✅ Deployment complete!"
