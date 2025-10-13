"""
Test Fake News Detection Tool
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from validators.fake_news_validator import validate_news_content_mock, filter_fake_news
from collectors.news import BrowserNewsCollector


def test_validate_single():
    """Test single content validation"""
    print("\n" + "="*60)
    print("TEST 1: Single Content Validation")
    print("="*60)
    
    # Real news
    real_news = "Scientists discover new renewable energy breakthrough"
    result = validate_news_content_mock(real_news)
    print(f"\nContent: {real_news}")
    print(f"Result: {result}")
    
    # Fake news
    fake_news = "HOAX: Conspiracy theory about unverified claims"
    result = validate_news_content_mock(fake_news)
    print(f"\nContent: {fake_news}")
    print(f"Result: {result}")


def test_filter_articles():
    """Test filtering browser-collected articles"""
    print("\n" + "="*60)
    print("TEST 2: Filter Browser-Collected Articles")
    print("="*60)
    
    # Collect news
    collector = BrowserNewsCollector()
    articles = collector.collect(country_code="jp", max_results=5)
    
    print(f"\nCollected {len(articles)} articles")
    
    # Filter fake news
    validated = filter_fake_news(articles, threshold=0.7)
    
    print(f"\n✅ Validated articles:")
    for i, article in enumerate(validated, 1):
        print(f"{i}. {article['title'][:60]}...")
        print(f"   Confidence: {article['validation']['confidence']}")


def test_with_agent():
    """Test with Strands Agent"""
    print("\n" + "="*60)
    print("TEST 3: Strands Agent Integration")
    print("="*60)
    
    from travel_tools import TRAVEL_TOOLS
    from strands import Agent
    from strands.models import BedrockModel
    
    agent = Agent(
        tools=TRAVEL_TOOLS,
        model=BedrockModel(
            model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
            temperature=0.7,
        ),
        system_prompt="You validate news content for fake news detection."
    )
    
    query = "Get validated news for Japan and check if they are real"
    
    try:
        response = agent(query)
        print(f"\n✅ Agent Response:")
        print(response)
    except Exception as e:
        print(f"\n⚠️  Agent test skipped (requires AWS): {e}")


if __name__ == "__main__":
    test_validate_single()
    test_filter_articles()
    # test_with_agent()  # Uncomment to test with agent
    
    print("\n" + "="*60)
    print("✅ All tests completed")
    print("="*60)
