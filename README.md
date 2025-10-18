# AI Recruitment Platform

人材採用・キャリアマッチング支援AIエージェントプラットフォーム（企業内人事システム）

## 概要

このプロジェクトは、AWS Bedrock AgentCoreを活用した企業内人事システムです。人事部門が採用プロセスでAIエージェントを活用し、候補者体験と業務効率を両立します。

### 🔒 プライバシーとコンプライアンス

- **候補者の同意**: 候補者が提供した情報のみを使用
- **規約準拠**: LinkedInやGitHubの利用規約を遵守
- **公式API使用**: GitHub公式APIを使用（スクレイピングなし）
- **検索結果表示**: 詳細データの自動抽出は行わない

### アーキテクチャ

```
Collectors (Search + API) → Agents (AgentCore) → DynamoDB + S3 (Knowledge Base)
    ↓                              ↓
  Tests                    Multi-Agent System
```

## 主要コンポーネント

### Data Collectors (`agents/src/collectors/`)

規約準拠のデータ収集ツール：

- **`base.py`**: 全コレクターの基底クラス（`BaseBrowserCollector`）
  - ブラウザとエージェントの遅延初期化
  - JSON レスポンスのパース

- **`candidate_search.py`**: 候補者検索（`CandidateSearchCollector`）
  - 検索結果URLの表示のみ
  - データ抽出なし（人事担当者が確認）

- **`github.py`**: GitHub公開プロフィール（`GitHubAPICollector`）
  - GitHub公式API使用
  - 候補者が提供したusernameのみ

- **`company.py`**: 企業情報検索（`CompanySearchCollector`）
  - 検索結果URLの表示のみ
  - 公開情報の確認用

- **`job_market.py`**: 求人市場検索（`JobMarketSearchCollector`）
  - 検索結果URLの表示のみ
  - 市場動向の確認用

### AI Agents

8つの専門エージェントが協調して採用プロセスを支援：

| エージェント | 役割 | 主な機能 |
|------------|------|---------|
| **Orchestrator** | 全体制御・セッション管理 | エージェント間連携、ワークフロー制御 |
| **Candidate Concierge** | 応募者との自然対話 | 志向分析、質問応答、体験向上 |
| **Skill Parser** | 履歴書・GitHub解析 | スキル抽出、経験評価、ポートフォリオ分析 |
| **Job Matcher** | 求人×候補者マッチング | 適合スコア算出、推薦ランキング |
| **Interviewer Copilot** | 面接支援 | 質問提案、要約、評価支援 |
| **Bias Auditor** | バイアス検出 | 法令違反チェック、公平性監査 |
| **Scheduler** | 面接日程調整 | カレンダー連携、自動スケジューリング |
| **Onboarding Guide** | 入社支援 | オンボーディング、HRIS連携 |

## ディレクトリ構成

```
agents/
├── orchestrator/          # 全体制御エージェント
├── candidate_concierge/   # 候補者対話エージェント
├── skill_parser/          # スキル解析エージェント
├── job_matcher/           # マッチングエージェント
├── interviewer_copilot/   # 面接支援エージェント
├── bias_auditor/          # バイアス監査エージェント
├── scheduler/             # スケジューリングエージェント
├── onboarding/            # オンボーディングエージェント
├── src/
│   ├── collectors/        # データ収集ツール（規約準拠）
│   └── storage/           # データストレージ
└── tests/                 # テストスイート
```

## データフロー

1. **候補者が情報を提供**（履歴書、GitHub username等）
2. **Collectors**で検索結果表示 + GitHub API取得
3. **Skill Parser**が候補者プロファイルを解析
4. **Job Matcher**が最適な求人とマッチング
5. **Candidate Concierge**が候補者と対話
6. **Interviewer Copilot**が面接を支援
7. **Bias Auditor**が公平性を監査
8. 結果をDynamoDB + S3 (Knowledge Base)に保存
9. **Orchestrator**が全体を制御

## セットアップ

```bash
# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定
cp agents/.env.example agents/.env
# .env に AWS 認証情報とGitHub tokenを設定
```

## 必要な環境変数

```
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
GITHUB_TOKEN=your_github_token  # オプション（レート制限緩和用）
```

## 使用例

### 候補者情報収集（規約準拠）

```python
from agents.src.collectors import RecruitmentDataCollectionService

# サービス初期化
service = RecruitmentDataCollectionService(
    region="us-west-2",
    github_token="your_github_token"  # オプション
)

# 候補者情報収集（候補者が提供した情報のみ）
result = service.collect_candidate_info(
    candidate_name="John Doe",
    github_username="johndoe",  # 候補者が提供
    company="Tech Corp"
)

# 検索結果URL
print(result["search_results"])

# GitHub公開プロフィール（API経由）
print(result["github_profile"])
```

### 企業情報検索

```python
from agents.src.collectors import CompanySearchCollector

collector = CompanySearchCollector()
search_results = collector.search("Google")

# 検索結果URLを取得
print(search_results["glassdoor_search_url"])
print(search_results["linkedin_company_url"])
```

### 求人市場検索

```python
from agents.src.collectors import JobMarketSearchCollector

collector = JobMarketSearchCollector()
search_results = collector.search("Software Engineer", "San Francisco")

# 検索結果URLを取得
print(search_results["linkedin_jobs_url"])
print(search_results["indeed_search_url"])
```

## 技術スタック

- **Amazon Bedrock AgentCore**: エージェント実行環境
  - Runtime: セッション管理とスケーリング
  - Browser: 検索結果表示
  - Memory: 永続化メモリ（DynamoDB）
  - Gateway: 外部ツール連携（GitHub API等）
  - Identity: IAM/JWT認証
  - Observability: CloudWatch/X-Ray監視

- **Strands**: エージェントフレームワーク
- **Claude 3.5 Sonnet**: LLMモデル
- **GitHub API**: 公式API使用
- **Python 3.10+**

## UI連携

UIバックエンドから`invoke_agent()`でAPIを呼び出し：

```json
{
  "outputText": "エージェントの応答",
  "traceId": "実行トレースID",
  "memoryRef": "メモリ参照",
  "toolCalls": ["使用したツール"]
}
```

## 監視・ログ

- **CloudWatch Logs**: エージェント実行ログ
- **X-Ray**: 分散トレーシング
- **Bedrock Observability**: エージェント動作監視

## ⚠️ 重要な注意事項

1. **候補者の同意が必須**: すべての情報は候補者が自ら提供したもののみ使用
2. **人事担当者の確認**: 検索結果は人事担当者が確認し、候補者に直接情報提供を依頼
3. **データの取り扱い**: 収集したデータは採用目的のみに使用し、適切に管理
4. **規約遵守**: LinkedInやGitHubの利用規約を遵守

## ライセンス

MIT
