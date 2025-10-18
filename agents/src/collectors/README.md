# Recruitment Data Collectors

企業内人事システム向けデータ収集ツール（APIキー任意対応）

## 🔒 プライバシーとコンプライアンス

- **候補者の同意**: 候補者が提供した情報のみを使用
- **規約準拠**: 公式API使用（キーがある場合）
- **柔軟な運用**: APIキーなしでも基本機能は動作

## 📋 Collectors

### LinkedInCollector
- **APIキーあり**: LinkedIn API経由でプロフィール取得
- **APIキーなし**: URL形式検証のみ
- **候補者提供**: LinkedIn URL

### GitHubCollector
- **APIキーあり**: GitHub API経由でプロフィール・リポジトリ取得
- **APIキーなし**: Username検証のみ
- **候補者提供**: GitHub username

### その他のCollectors
- CandidateSearchCollector: 候補者検索
- CompanySearchCollector: 企業情報検索
- JobMarketSearchCollector: 求人市場検索

## 🚀 使用方法

### APIキーありの場合（フル機能）

```python
from agents.src.collectors import collect_candidate_data

result = collect_candidate_data(
    candidate_name="John Doe",
    linkedin_url="https://www.linkedin.com/in/johndoe",
    github_username="johndoe",
    github_api_key="ghp_xxxxxxxxxxxx",  # GitHub API key
    linkedin_api_key="your_linkedin_key"  # LinkedIn API key
)

# APIから取得したデータ
print(result["github"]["public_repos"])  # 42
print(result["github"]["top_languages"])  # ["Python", "JavaScript"]
print(result["linkedin"]["data_source"])  # "LinkedIn API"
```

### APIキーなしの場合（基本機能）

```python
from agents.src.collectors import collect_candidate_data

result = collect_candidate_data(
    candidate_name="John Doe",
    linkedin_url="https://www.linkedin.com/in/johndoe",
    github_username="johndoe"
    # APIキー不要
)

# URL/Username検証のみ
print(result["github"]["valid"])  # True
print(result["github"]["profile_url"])  # "https://github.com/johndoe"
print(result["linkedin"]["valid"])  # True
print(result["api_status"])  # {"github": "disabled", "linkedin": "disabled"}
```

### サービスクラスの使用

```python
from agents.src.collectors import RecruitmentDataCollectionService

# APIキーを指定して初期化
service = RecruitmentDataCollectionService(
    region="us-west-2",
    github_api_key="ghp_xxxx",  # オプション
    linkedin_api_key="your_key"  # オプション
)

# 候補者情報収集
result = service.collect_candidate_info(
    candidate_name="John Doe",
    linkedin_url="https://www.linkedin.com/in/johndoe",
    github_username="johndoe"
)
```

## 🔑 APIキー取得方法

### GitHub API Key

1. GitHub Settings → Developer settings → Personal access tokens
2. "Generate new token (classic)"
3. スコープ選択: `public_repo`, `read:user`
4. 環境変数に設定: `GITHUB_API_KEY=ghp_xxxx`

### LinkedIn API Key

1. LinkedIn Developers → Create App
2. OAuth 2.0設定
3. API keyを取得
4. 環境変数に設定: `LINKEDIN_API_KEY=your_key`

## 📊 取得可能データ

### GitHub（APIキーあり）
- ユーザープロフィール（名前、bio、location）
- 公開リポジトリ一覧
- リポジトリの言語、スター数
- フォロワー/フォロー数

### GitHub（APIキーなし）
- Username検証
- プロフィールURL生成

### LinkedIn（APIキーあり）
- プロフィール情報
- 職務経歴
- スキル

### LinkedIn（APIキーなし）
- URL形式検証
- Username抽出

## ⚠️ 重要な注意事項

1. **APIキーは任意**: なくても基本機能は動作
2. **候補者の同意**: 提供された情報のみ使用
3. **レート制限**: GitHub API（認証なし60/h、認証あり5000/h）
4. **データ管理**: 採用目的のみに使用
