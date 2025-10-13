"""
実データ取得の検証テスト
Mockデータではなく実際のデータが取得できることを確認
"""

import sys
import os

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src')
)

from dotenv import load_dotenv
from collectors.news import BrowserNewsCollector
from collectors.weather import BrowserWeatherCollector
from collectors.flight import BrowserFlightCollector
from collectors.trends import BrowserTrendCollector

load_dotenv()


def validate_real_news(articles):
    """ニュースが実データか検証"""
    if not articles:
        return False, "記事が取得できませんでした"

    # 実データの特徴をチェック
    first = articles[0]
    if not first.get("title") or not first.get("source"):
        return False, "タイトルまたはソースが空です"

    # Mockデータの特徴がないことを確認
    if "mock" in first.get("title", "").lower():
        return False, "Mockデータが返されました"

    return True, f"✅ 実データ取得成功: {len(articles)}件の記事"


def validate_real_weather(weather):
    """天気が実データか検証"""
    if not weather:
        return False, "天気データが取得できませんでした"

    # 実データの特徴をチェック
    if not weather.get("city") or weather.get("temp") == 0:
        return False, "都市名または気温が不正です"

    # Mockデータの特徴がないことを確認
    if "mock" in weather.get("city", "").lower():
        return False, "Mockデータが返されました"

    return True, f"✅ 実データ取得成功: {weather.get('city')} {weather.get('temp')}°C"


def validate_real_flights(flights):
    """フライトが実データか検証"""
    if not flights:
        return False, "フライトデータが取得できませんでした"

    first = flights[0]

    # Mockデータの特徴をチェック
    if first.get("airline") == "Mock":
        return False, "❌ Mockデータが返されました（AWS認証エラーの可能性）"

    # 実データの特徴をチェック
    if not first.get("airline") or first.get("price") == 0:
        return False, "航空会社または価格が不正です"

    return True, f"✅ 実データ取得成功: {len(flights)}件のフライト"


def validate_real_trends(trends):
    """トレンドが実データか検証"""
    if not trends:
        return False, "トレンドデータが取得できませんでした"

    first = trends[0]

    # Mockデータの特徴をチェック
    if first.get("topic") == "Mock":
        return False, "❌ Mockデータが返されました（AWS認証エラーの可能性）"

    # 実データの特徴をチェック
    if not first.get("topic") or not first.get("description"):
        return False, "トピックまたは説明が不正です"

    return True, f"✅ 実データ取得成功: {len(trends)}件のトレンド"


def test_news_real_data():
    """ニュース実データ検証"""
    print("\n" + "=" * 60)
    print("TEST 1: ニュース実データ検証")
    print("=" * 60)

    collector = BrowserNewsCollector(region=os.getenv("AWS_REGION", "us-west-2"))
    articles = collector.get_top_headlines("JP", max_results=5, validate=False)

    is_real, message = validate_real_news(articles)
    print(f"\n{message}")

    if is_real and articles:
        for i in range(len(articles)):
            print(f"\nnews_detail[{i}]:")
            print(articles[i])

    return is_real


def test_weather_real_data():
    """天気実データ検証"""
    print("\n" + "=" * 60)
    print("TEST 2: 天気実データ検証")
    print("=" * 60)

    collector = BrowserWeatherCollector(region=os.getenv("AWS_REGION", "us-west-2"))
    weather = collector.get_weather("JP", "Tokyo")

    is_real, message = validate_real_weather(weather)
    print(f"\n{message}")

    if is_real:
        print(f"\nweather_detail:")
        print(weather)

    return is_real


def test_flight_real_data():
    """フライト実データ検証"""
    print("\n" + "=" * 60)
    print("TEST 3: フライト実データ検証")
    print("=" * 60)

    collector = BrowserFlightCollector(region=os.getenv("AWS_REGION", "us-west-2"))
    flights = collector.search_flights("LAX", "NRT", "2025-02-15", num_results=5)

    is_real, message = validate_real_flights(flights)
    print(f"\n{message}")

    if not is_real:
        print("\n⚠️  AWS認証情報を確認してください:")
        print("  1. AWS_ACCESS_KEY_ID")
        print("  2. AWS_SECRET_ACCESS_KEY")
        print("  3. AWS_SESSION_TOKEN (一時認証の場合)")
        print("  4. Bedrockモデルアクセス権限")
    elif flights:
        for i in range(len(flights)):
            print(f"\nflight_detail[{i}]:")
            print(flights[i])

    return is_real


def test_trends_real_data():
    """トレンド実データ検証"""
    print("\n" + "=" * 60)
    print("TEST 4: トレンド実データ検証")
    print("=" * 60)

    collector = BrowserTrendCollector(region=os.getenv("AWS_REGION", "us-west-2"))
    trends = collector.get_trending_topics("JP", hours=168, num_results=5)

    is_real, message = validate_real_trends(trends)
    print(f"\n{message}")

    if not is_real:
        print("\n⚠️  AWS認証情報を確認してください:")
        print("  1. AWS_ACCESS_KEY_ID")
        print("  2. AWS_SECRET_ACCESS_KEY")
        print("  3. AWS_SESSION_TOKEN (一時認証の場合)")
        print("  4. Bedrockモデルアクセス権限")
    elif trends:
        for i in range(len(trends)):
            print(f"\ntrend_detail[{i}]:")
            print(trends[i])

    return is_real


def main():
    """全検証テスト実行"""
    print("\n" + "=" * 60)
    print("実データ取得検証テストスイート")
    print("=" * 60)

    results = {}

    try:
        results["news"] = test_news_real_data()
        results["weather"] = test_weather_real_data()
        results["flight"] = test_flight_real_data()
        results["trends"] = test_trends_real_data()

        print("\n" + "=" * 60)
        print("検証結果サマリー")
        print("=" * 60)
        print(f"  ニュース: {'✅ 実データ' if results['news'] else '❌ Mockデータ'}")
        print(f"  天気: {'✅ 実データ' if results['weather'] else '❌ Mockデータ'}")
        print(f"  フライト: {'✅ 実データ' if results['flight'] else '❌ Mockデータ'}")
        print(f"  トレンド: {'✅ 実データ' if results['trends'] else '❌ Mockデータ'}")

        all_real = all(results.values())
        if all_real:
            print("\n🎉 全てのコレクターで実データ取得成功！")
        else:
            print("\n⚠️  一部のコレクターでMockデータが返されています")
            print("AWS認証情報とBedrockアクセス権限を確認してください")

        return all_real

    except Exception as e:
        print(f"\n❌ テスト失敗: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
