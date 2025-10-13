# Agent Tools

AIエージェント向けのデータ収集・分析ツール群

## 概要

このプロジェクトは、AIエージェントが外部データを収集・分析するためのツールセットです。ブラウザベースのデータ収集機能を提供し、旅行推薦やパネルディスカッションなどのユースケースに対応します。

### アーキテクチャ

```
Collectors → main.py (AgentCore App) → RDS + S3 (Knowledge Base)
    ↓              ↓
  Tests    Panel Discussion
```

## 主要コンポーネント

### Collectors (`agents/src/collectors/`)

ブラウザを使用してリアルタイムデータを収集するモジュール群：

- **`base.py`**: 全コレクターの基底クラス（`BaseBrowserCollector`）
  - ブラウザとエージェントの遅延初期化
  - JSON レスポンスのパース
  - センチメント分析

- **`news.py`**: ニュース収集（`BrowserNewsCollector`）
  - 国別トップヘッドライン取得
  - センチメント分析付き

- **`weather.py`**: 気象情報収集（`BrowserWeatherCollector`）
  - 国・都市別の現在の天気
  - 気温、天候、ムード影響度

- **`flight.py`**: フライト検索（`BrowserFlightCollector`）
  - 空港間のフライト検索
  - 価格、所要時間、航空会社情報

- **`trends.py`**: トレンド収集（`BrowserTrendCollector`）
  - 国別トレンドトピック
  - エンゲージメント指標

## メインアプリケーション

### `main.py` - Bedrock AgentCore アプリケーション

パネルディスカッションシステムのエントリーポイント。複数のエキスパートエージェントが議論を行い、国の気分を分析します。

**主要エンドポイント:**

- `run_panel_discussion`: パネルディスカッション実行 + RDS/S3保存
- `collect_data_only`: データ収集のみ（Collectors使用）
- `list_discussions`: ディスカッション履歴取得
- `get_discussion`: 特定ディスカッション取得
- `rag_chat`: Knowledge BaseからRAG検索
- `health_check`: システムヘルスチェック

**データフロー:**
1. Collectorsでニュース・天気・トレンド・フライトを収集
2. パネルディスカッションで分析・議論
3. 結果をRDS + S3 (Knowledge Base)に保存
4. RAGチャットで過去の分析を検索可能

## テスト

### `test_panel_v2.py` - パネルディスカッションテスト

main.pyのパネルディスカッション機能をテスト。エージェント間の議論フローとRDS保存を検証します。

**テスト内容:**
- パネルシステム初期化
- RDSストレージ接続（オプション）
- テスト国データでディスカッション実行
- 結果の検証とRDS保存

**実行方法:**
```bash
cd agents/tests
python test_panel_v2.py
```

### `test_smart_travel_agent.py` - 旅行エージェントテスト

スマート旅行エージェントの統合テスト。ユーザーの好みや制約から最適な旅行先を発見します。

**4つのテストシナリオ:**

1. **好み基づく発見** (`test_discover_from_preferences`)
   - 建築、料理、気候、予算から候補国を推薦
   - 各候補のニュース、天気、トレンド、フライトを収集
   - スコアリングとトップ2推薦

2. **ムード基づく発見** (`test_discover_from_mood`)
   - ユーザーの感情状態を解釈
   - リラックス、冒険、文化などのニーズにマッチ
   - 感情的充足を重視した推薦

3. **アクティビティ基づく発見** (`test_discover_from_activities`)
   - 希望アクティビティから目的地を特定
   - フェスティバル、グルメ、写真、ナイトライフなど
   - 現在の状況を検証して推薦

4. **制約基づく発見** (`test_discover_from_constraints`)
   - 予算、気温、安全性などのハード制約
   - 文化、食事などのソフト優先度
   - 全制約を満たす最適解を提示

**実行方法:**
```bash
cd agents/tests/collectors
python test_smart_travel_agent.py
```

### その他のテスト

**Collectorsテスト:**
- `test_browser_collector.py`: 個別コレクターの単体テスト
- `test_collectors_local.py`: ローカル環境でのコレクターテスト
- `test_agent_data_collection.py`: エージェントデータ収集フロー
- `test_data_collection.py`: データ収集パイプライン

**統合テスト:**
- `test_panel_v2.py`: main.pyのパネルディスカッション機能
- `test_smart_travel_agent.py`: Collectorsを使った旅行推薦

## セットアップ

```bash
# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定
cp agents/.env.example agents/.env
# .env に AWS 認証情報を設定
```

## 必要な環境変数

```
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

## 技術スタック

- **Strands**: エージェントフレームワーク
- **Amazon Bedrock**: Claude 3.5 Sonnet モデル
- **AgentCore Browser**: ブラウザ自動化
- **Python 3.8+**

## ライセンス

MIT
