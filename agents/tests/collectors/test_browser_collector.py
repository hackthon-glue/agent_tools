"""
Browser Data Collection Connection Test
Displays detailed information about actual data being collected
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from collectors.news import BrowserNewsCollector
from collectors.weather import BrowserWeatherCollector
from collectors.service import BrowserDataCollectionService


def test_news_japan():
    """Test news collection for Japan"""
    print("\n" + "=" * 80)
    print("📰 News Collection Test - Japan (Japan Times)")
    print("=" * 80)

    collector = BrowserNewsCollector(region="us-west-2")
    articles = collector.collect(country_code="jp", max_results=5)

    print(f"\nArticles collected: {len(articles)}\n")

    for i, article in enumerate(articles, 1):
        print(f"[Article {i}]")
        print(f"Title: {article.get('title', 'N/A')}")
        print(f"Description: {article.get('description', 'N/A')[:100]}...")
        print(f"Source: {article.get('source', 'N/A')}")
        print(f"Sentiment: {article.get('sentiment', 0)}")
        print(f"URL: {article.get('url', 'N/A')}")
        print(f"Published: {article.get('published_at', 'N/A')}")
        print()


def test_weather_tokyo():
    """Test weather collection for Tokyo"""
    print("\n" + "=" * 80)
    print("🌤️  Weather Collection Test - Tokyo")
    print("=" * 80)

    collector = BrowserWeatherCollector(region="us-west-2")
    weather = collector.collect(country_code="jp", city="Tokyo")

    print(f"\nCity: {weather.get('city', 'N/A')}, {weather.get('country', 'N/A')}")
    print(f"Temperature: {weather.get('temp', 'N/A')}°C")
    print(f"Feels Like: {weather.get('feels_like', 'N/A')}°C")
    print(f"Condition: {weather.get('description', 'N/A')}")
    print(f"Humidity: {weather.get('humidity', 'N/A')}%")
    print(f"Wind Speed: {weather.get('wind_speed', 'N/A')} km/h")
    print(f"Mood Impact: {weather.get('mood_impact', 0)} (-1=Negative, +1=Positive)")
    print(f"Timestamp: {weather.get('timestamp', 'N/A')}")


def test_full_data_japan():
    """Test full data collection for Japan"""
    print("\n" + "=" * 80)
    print("🇯🇵 Full Data Collection Test - Japan (News + Weather)")
    print("=" * 80)

    service = BrowserDataCollectionService(region="us-west-2")
    data = service.collect_country_data(country_code="jp", max_news=5, parallel=True)

    print("\n[Statistics]")
    stats = data["statistics"]
    print(f"Country Code: {data['country_code']}")
    print(f"News Articles: {stats['news_count']}")
    print(f"Avg Sentiment: {stats['avg_news_sentiment']}")
    print(f"Weather Mood Impact: {stats['weather_mood_impact']}")
    print(f"Collection Method: {stats['collection_method']}")
    print(f"Collection Time: {stats['collection_timestamp']}")

    print("\n[News Summary]")
    for i, article in enumerate(data["news"], 1):
        print(f"{i}. {article['title'][:60]}... (Sentiment: {article['sentiment']})")

    print("\n[Weather Info]")
    weather = data["weather"]
    print(
        f"{weather['city']}: {weather['description']}, {weather['temp']}°C (Mood: {weather['mood_impact']})"
    )


def test_multiple_countries():
    """Test data collection for multiple countries"""
    print("\n" + "=" * 80)
    print("🌍 Multiple Countries Data Collection Test")
    print("=" * 80)

    countries = [("jp", "Tokyo"), ("us", "Washington")]

    service = BrowserDataCollectionService(region="us-west-2")

    for country_code, city in countries:
        print(f"\n--- {country_code.upper()} ({city}) ---")
        try:
            data = service.collect_country_data(
                country_code=country_code, max_news=3, city=city, parallel=True
            )
            print(f"✅ News: {len(data['news'])} articles")
            print(f"   Avg Sentiment: {data['statistics']['avg_news_sentiment']}")
            print(
                f"   Weather: {data['weather']['description']}, {data['weather']['temp']}°C"
            )
            print(f"   Mood: {data['weather']['mood_impact']}")
        except Exception as e:
            print(f"❌ Error: {e}")


def show_raw_data():
    """Display raw data in JSON format"""
    print("\n" + "=" * 80)
    print("📋 Raw Data Display (JSON Format)")
    print("=" * 80)

    service = BrowserDataCollectionService(region="us-west-2")
    data = service.collect_country_data(country_code="jp", max_news=3, parallel=False)

    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        test_news_japan()
        test_weather_tokyo()
        test_full_data_japan()
        test_multiple_countries()
        show_raw_data()

        print("\n" + "=" * 80)
        print("✅ All connection tests completed")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()