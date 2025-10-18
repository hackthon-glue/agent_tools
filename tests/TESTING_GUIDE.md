# Testing Guide - AI Recruitment Platform

## テスト構成

### 📁 ディレクトリ構造

```
tests/
├── unit/              # 単体テスト（モック使用）
├── integration/       # 結合テスト（実AWS接続）
├── acceptance/        # 受け入れテスト（E2E）
├── conftest.py        # 自動モック設定
├── pytest.ini         # pytest設定
└── TESTING_GUIDE.md   # このファイル
```

## 🎯 テストレベル

### 1. Unit Tests (単体テスト)
- **場所**: `tests/unit/`
- **目的**: 個別機能の高速検証
- **依存**: すべてモック（AWS認証不要）
- **実行**: `pytest tests/unit -v`
- **速度**: ⚡ 高速 (~1秒)
- **カバレッジ**: 29テスト

### 2. Integration Tests (結合テスト)
- **場所**: `tests/integration/`
- **目的**: 実AWS接続の検証
- **依存**: AWS認証情報必須
- **実行**: `pytest -m integration -v`
- **速度**: 🐢 中速 (~5-10秒)
- **カバレッジ**: 3テスト (DynamoDB, KB, Memory)

### 3. Acceptance Tests (受け入れテスト)
- **場所**: `tests/acceptance/`
- **目的**: エージェント全体の動作検証
- **依存**: 全AWSリソース + AgentCore
- **実行**: `pytest -m acceptance -v`
- **速度**: 🐌 低速 (~10-30秒)
- **カバレッジ**: 5テスト (全エージェント)

## 🚀 実行方法

```bash
# デフォルト（単体テストのみ、AWS不要）
pytest

# 単体テストのみ（明示的）
pytest tests/unit -v

# 結合テスト（AWS認証必須）
pytest -m integration -v

# 受け入れテスト（全環境必須）
pytest -m acceptance -v

# すべてのテスト（AWS認証必須）
pytest -m "" -v

# カバレッジ付き
pytest tests/unit --cov=agents --cov-report=html
```

## 🔧 環境設定

### 単体テスト
```bash
# AWS認証不要（conftest.pyが自動モック）
pytest
```

### 結合・受け入れテスト
```bash
# AWS認証情報設定
export AWS_REGION=us-west-2
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret

# または AWS SSO
aws sso login

# オプション環境変数
export KNOWLEDGE_BASE_ID=your_kb_id
export MEMORY_ID=your_memory_id
```

## 🔄 自動モック機能

`tests/conftest.py`が以下を自動モック:
- `boto3.client` - AWS SDK呼び出し
- `bedrock_agentcore.memory.MemoryClient` - Memory初期化
- `agents.tools.memory_tools.get_conversation_history` - 会話履歴取得

**メリット**: AWS認証なしで全単体テストが実行可能

## 🏷️ pytest マーカー

```python
@pytest.mark.unit          # 単体テスト（デフォルト実行）
@pytest.mark.integration   # 結合テスト（明示的実行）
@pytest.mark.acceptance    # 受け入れテスト（明示的実行）
```

## 🔄 CI/CD推奨フロー

1. **PR作成時**: `pytest` (単体テストのみ、高速)
2. **mainマージ時**: `pytest -m "" -v` (全テスト)
3. **リリース時**: `pytest -m acceptance -v` (E2E検証)

## 💡 ベストプラクティス

- 開発中は `pytest` で高速検証（AWS不要）
- AWS接続確認は `pytest -m integration -v`
- デプロイ前は `pytest -m acceptance -v` で最終確認
- `conftest.py`により単体テストは常にAWS不要

## 🐛 トラブルシューティング

### AWS SSO Token Expired エラー
```bash
# 単体テストの場合 → 問題なし（モック使用）
pytest tests/unit -v

# 結合/受け入れテストの場合 → AWS再認証
aws sso login
pytest -m integration -v
```

### テストが見つからない
```bash
# pytest.iniの設定確認
cat tests/pytest.ini

# テスト検出確認
pytest --collect-only
```

### モックが効かない
```bash
# conftest.pyの存在確認
ls tests/conftest.py

# キャッシュクリア
pytest --cache-clear
```
