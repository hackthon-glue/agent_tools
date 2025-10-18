# AI Recruitment Platform - AgentCore Edition

企業内人事システム向け AI エージェントプラットフォーム（AWS Bedrock AgentCore + Strands）

## 概要

オーケストレーターが 4 つの専門エージェントを統合：

**Orchestrator Agent** - メインコーディネーター（全エージェント統合）

専門エージェント：

1. **Concierge Agent** - キャリア相談・求人探し（AgentCore Memory）
2. **Skill Parser Agent** - 履歴書・GitHub 解析（PDF Tools）
3. **Job Matcher Agent** - 候補者 × 求人マッチング（Knowledge Base）
4. **Interviewer Copilot Agent** - 面接支援（AgentCore Memory）

## アーキテクチャ

```
agents/
├── orchestrator_agent.py       # メインオーケストレーター
├── concierge_agent.py          # 対話エージェント（Memory）
├── skill_parser_agent.py       # スキル解析
├── job_matcher_agent.py        # マッチング（KB）
├── interviewer_copilot_agent.py # 面接支援（Memory）
├── memory_hook.py              # AgentCore Memory Hook
└── tools/
    ├── dynamodb_tools.py       # DynamoDB アクセス
    ├── kb_tools.py             # Knowledge Base
    ├── memory_tools.py         # AgentCore Memory
    ├── pdf_tools.py            # PDF解析
    ├── agent_tools.py          # エージェント呼び出し
    ├── collector_tools.py      # Web Collectors
    └── collectors/             # 各種Collector実装
        ├── linkedin.py
        ├── github.py
        ├── job_market.py
        └── candidate_search.py
```

## セットアップ

```bash
# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定
export AWS_REGION=us-west-2
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

## ローカルテスト

```bash
# 単体テスト
pytest tests/test_agents.py -v
pytest tests/test_orchestrator.py -v

# 統合テスト
python test_local.py

# 個別エージェントテスト
python agents/concierge_agent.py
```

## AgentCore Runtime デプロイ

### 0. Orchestrator Agent (メイン)

```bash
cd agents
agentcore configure --entrypoint orchestrator_agent.py
agentcore launch --name orchestrator-agent

# テスト
agentcore invoke '{
  "user_id": "user123",
  "request": "求人を探しています",
  "session_id": "session123"
}'
```

### 1. Concierge Agent

```bash
cd agents
agentcore configure --entrypoint concierge_agent.py
agentcore launch --name concierge-agent

# テスト
agentcore invoke '{
  "user_id": "user123",
  "message": "ソフトウェアエンジニアの求人を探しています",
  "session_id": "session123"
}'
```

### 2. Skill Parser Agent

```bash
agentcore configure --entrypoint skill_parser_agent.py
agentcore launch --name skill-parser-agent

# テスト
agentcore invoke '{
  "user_id": "user123",
  "resume_pdf": "base64_encoded_pdf_here"
}'
```

### 3. Job Matcher Agent

```bash
agentcore configure --entrypoint job_matcher_agent.py
agentcore launch --name job-matcher-agent

# テスト
agentcore invoke '{
  "user_id": "user123",
  "filters": {"location": "Tokyo", "role": "Engineer"}
}'
```

### 4. Interviewer Copilot Agent

```bash
agentcore configure --entrypoint interviewer_copilot_agent.py
agentcore launch --name interviewer-copilot-agent

# テスト
agentcore invoke '{
  "user_id": "user123",
  "interview_id": "int123",
  "action": "generate_questions"
}'
```

## DynamoDB テーブル構成

### recruitment_users

```
user_id (PK) | name | email | skills | experience | preferences
```

### recruitment_jobs

```
job_id (PK) | title | company | location | requirements | description
```

### recruitment_github_profiles

```
user_id (PK) | username | repos | languages | contributions
```

## Knowledge Base 構成

評価基準ドキュメント：

- スキルマッチング基準
- 経験年数評価
- 文化適合性指標

## AgentCore Memory 機能

### Memory Hook 統合

- **MemoryHook**: Strands HookProvider 実装
- **on_agent_initialized**: 過去の会話履歴をロード
- **on_message_added**: 新しいメッセージを自動保存

### セッション設定

- **Concierge Agent**: 1 時間セッション（会話履歴）
- **Interviewer Copilot**: 30 分セッション（面接コンテキスト）
- **デフォルト K 値**: 直近 3 ターンの会話を取得

## 技術スタック

### コアフレームワーク

- **AWS Bedrock AgentCore**: Runtime, Memory, Gateway
- **Strands**: エージェントフレームワーク
- **Claude 4.5 Sonnet v2**: LLM モデル (us.anthropic.claude-sonnet-4-5-20250929-v1:0)

### ツール統合

- **Sequential Thinking**: 複雑な推論タスク用思考ツール
- **AgentCore Memory**: セッション管理・会話履歴保存
- **Context7**: ライブラリドキュメント検索
- **AWS Docs**: AWS 公式ドキュメント検索

### データストア

- **DynamoDB**: ユーザ・求人・GitHub プロファイル
- **Bedrock Knowledge Base**: 評価基準・マッチングルール

### Web Collectors

- **LinkedIn Collector**: プロフィール・求人情報
- **GitHub Collector**: リポジトリ・コントリビューション
- **Job Market Collector**: 求人市場データ
- **Candidate Search Collector**: 候補者検索

## ライセンス

MIT
