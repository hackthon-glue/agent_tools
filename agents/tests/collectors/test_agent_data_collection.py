"""
Test: Agent calling data collection tools
Validates that Strands Agent can properly invoke browser collectors as tools
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from strands import Agent
from strands.models import BedrockModel

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))
from collectors.service import BrowserDataCollectionService

load_dotenv()


def collect_country_data_tool(country_code: str, max_news: int = 10) -> dict:
    """
    Tool: Collect news and weather data for a country

    Args:
        country_code: ISO country code (e.g., "JP", "US")
        max_news: Maximum number of news articles to collect

    Returns:
        Dictionary with news, weather, and statistics
    """
    service = BrowserDataCollectionService(region=os.getenv("AWS_REGION", "us-west-2"))

    return service.collect_country_data(
        country_code=country_code, max_news=max_news, parallel=True, validate=False
    )


def test_agent_tool_invocation():
    """Test that Agent can invoke data collection tool"""
    print("\n" + "=" * 60)
    print("TEST: Agent Tool Invocation")
    print("=" * 60)

    # Create agent with data collection tool
    agent = Agent(
        tools=[collect_country_data_tool],
        model=BedrockModel(
            model_id="us.anthropic.claude-3-haiku-20240307-v1:0",
            temperature=0.7,
            max_tokens=2000,
        ),
        system_prompt="""You are a data collection assistant.
Use the collect_country_data_tool to gather news and weather information.
Always provide a summary of the collected data.""",
    )

    # Test query
    query = "Collect data for Japan (JP) with 5 news articles"

    print(f"\n📝 Query: {query}")
    print("\n🤖 Agent processing...")

    response = agent(query)

    print(f"\n✅ Agent Response:")
    print(response)

    return response


def test_direct_tool_call():
    """Test direct tool invocation (baseline)"""
    print("\n" + "=" * 60)
    print("TEST: Direct Tool Call (Baseline)")
    print("=" * 60)

    result = collect_country_data_tool("JP", max_news=5)

    print(f"\n✅ Data collected:")
    print(f"  Country: {result['country_code']}")
    print(f"  News articles: {result['statistics']['news_count']}")
    print(f"  Avg sentiment: {result['statistics']['avg_news_sentiment']}")
    print(f"  Weather mood: {result['statistics']['weather_mood_impact']}")

    # Validate data structure
    assert "news" in result
    assert "weather" in result
    assert "statistics" in result
    assert len(result["news"]) > 0
    assert result["weather"] is not None

    print("\n✅ Data validation passed")

    return result


def test_multiple_countries():
    """Test collecting data for multiple countries"""
    print("\n" + "=" * 60)
    print("TEST: Multiple Countries Collection")
    print("=" * 60)

    agent = Agent(
        tools=[collect_country_data_tool],
        model=BedrockModel(
            model_id="us.anthropic.claude-3-haiku-20240307-v1:0",
            temperature=0.7,
            max_tokens=3000,
        ),
        system_prompt="""You are a data collection assistant.
Use collect_country_data_tool to gather data for multiple countries.
Compare the sentiment and weather across countries.""",
    )

    query = "Collect data for Japan (JP) and United States (US), then compare their sentiment"

    print(f"\n📝 Query: {query}")
    print("\n🤖 Agent processing...")

    response = agent(query)

    print(f"\n✅ Agent Response:")
    print(response)

    return response


def validate_data_quality(data: dict):
    """Validate collected data quality"""
    print("\n" + "=" * 60)
    print("DATA QUALITY VALIDATION")
    print("=" * 60)

    checks = []

    # Check news data
    if data["news"] and len(data["news"]) > 0:
        checks.append(("✅", "News articles collected"))

        # Check news structure
        first_news = data["news"][0]
        if "title" in first_news and "url" in first_news:
            checks.append(("✅", "News structure valid"))
        else:
            checks.append(("❌", "News structure invalid"))

        # Check sentiment
        if "sentiment" in first_news:
            checks.append(("✅", "Sentiment analysis present"))
        else:
            checks.append(("⚠️", "Sentiment analysis missing"))
    else:
        checks.append(("❌", "No news articles"))

    # Check weather data
    if data["weather"]:
        checks.append(("✅", "Weather data collected"))

        if "temperature" in data["weather"]:
            checks.append(("✅", "Temperature data present"))
        else:
            checks.append(("⚠️", "Temperature data missing"))

        if "mood_impact" in data["weather"]:
            checks.append(("✅", "Weather mood impact calculated"))
        else:
            checks.append(("⚠️", "Weather mood impact missing"))
    else:
        checks.append(("❌", "No weather data"))

    # Check statistics
    if data["statistics"]:
        checks.append(("✅", "Statistics calculated"))
    else:
        checks.append(("❌", "No statistics"))

    # Print results
    for status, message in checks:
        print(f"{status} {message}")

    passed = sum(1 for s, _ in checks if s == "✅")
    total = len(checks)

    print(f"\n📊 Quality Score: {passed}/{total} checks passed")

    return passed == total


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("AGENT DATA COLLECTION TOOL TEST SUITE")
    print("=" * 60)

    try:
        # Test 1: Direct tool call (baseline)
        print("\n[1/4] Testing direct tool invocation...")
        data = test_direct_tool_call()

        # Test 2: Validate data quality
        print("\n[2/4] Validating data quality...")
        validate_data_quality(data)

        # Test 3: Agent tool invocation
        print("\n[3/4] Testing agent tool invocation...")
        test_agent_tool_invocation()

        # Test 4: Multiple countries
        print("\n[4/4] Testing multiple countries...")
        test_multiple_countries()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
