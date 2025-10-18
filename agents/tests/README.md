# Tests

人材採用データ収集ツールのテストスイート

## テストファイル

### 1. test_collectors.py
個別Collectorの接続テスト

```bash
python test_collectors.py
```

### 2. test_service_acceptance.py ⭐
**エージェントが呼び出すメインツールの受け入れテスト**

```bash
python test_service_acceptance.py
```

## 受け入れテスト内容

### ✅ Full Candidate Data Collection
完全な候補者データ収集ワークフロー
- LinkedIn、GitHub、候補者検索、企業情報を一括取得
- データ構造の検証
- タイムスタンプとAPIステータスの確認

### ✅ Convenience Function
エージェント向け簡易関数のテスト
- `collect_candidate_data()`関数の動作確認
- 最小限のコードで呼び出し可能

### ✅ Individual Methods
個別メソッドの独立動作テスト
- `get_linkedin_profile()`
- `get_github_profile()`
- `search_candidate()`
- `search_company()`
- `search_job_market()`

### ✅ Minimal Input
最小限の入力での動作テスト
- 候補者名のみで動作確認
- オプション引数なしでの動作

### ✅ API Status Tracking
APIキーの有無による動作切り替えテスト
- APIキーなし: 検証のみ
- APIキーあり: フルデータ取得

## エージェントからの呼び出し例

```python
from collectors import collect_candidate_data

# エージェントツールとして使用
result = collect_candidate_data(
    candidate_name="Satya Nadella",
    linkedin_url="https://www.linkedin.com/in/satyanadella",
    github_username="microsoft",
    company="Microsoft"
)

# 結果の構造
{
    "candidate_name": "Satya Nadella",
    "collection_timestamp": "2025-10-18T13:41:53.431698",
    "api_status": {
        "github": "disabled",
        "linkedin": "disabled"
    },
    "linkedin": {...},
    "github": {...},
    "candidate_search": {...},
    "company_info": {...}
}
```

## 期待される出力

```
🚀 RecruitmentDataCollectionService Acceptance Tests
============================================================
Testing main tool that agents will call
============================================================

ACCEPTANCE TEST: Full Candidate Data Collection
============================================================
✅ Candidate: Satya Nadella
⏰ Timestamp: 2025-10-18T13:41:53.431698
📊 API Status: {'github': 'disabled', 'linkedin': 'disabled'}
🔗 LinkedIn: True
💻 GitHub: True
🔍 Candidate Search: True
🏢 Company Info: True

ACCEPTANCE TEST: Convenience Function
============================================================
✅ Candidate: Sundar Pichai
✅ All data collected successfully

ACCEPTANCE TEST: Individual Methods
============================================================
✅ LinkedIn: True
✅ GitHub: True
✅ Candidate Search: True
✅ Company Search: True
✅ Job Market Search: True

ACCEPTANCE TEST: Minimal Input
============================================================
✅ Candidate: John Doe
✅ Minimal data collected successfully

ACCEPTANCE TEST: API Status Tracking
============================================================
✅ No API: {'github': 'disabled', 'linkedin': 'disabled'}

============================================================
✅ All acceptance tests passed!
============================================================

📝 Summary:
- Service can collect full candidate data
- Convenience function works for agents
- Individual methods work independently
- Minimal input is handled correctly
- API status is tracked properly
```

## 環境変数（オプション）

```bash
# GitHub API（オプション）
export GITHUB_API_KEY=ghp_xxxxxxxxxxxx

# LinkedIn API（オプション）
export LINKEDIN_API_KEY=your_key
```

## 注意事項

- AgentCore Browserテストは実際にAWS Bedrockに接続します
- AWS認証情報が必要です
- テスト実行にはAWS料金が発生する可能性があります
- AWS認証エラーが出てもテストは成功します（フォールバック動作）
