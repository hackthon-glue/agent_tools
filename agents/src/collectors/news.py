"""News collector using RSS feeds and browser scraping"""

from typing import Dict, List
from datetime import datetime
import re
import requests
import xml.etree.ElementTree as ET
from .base import BaseBrowserCollector

try:
    from ..news_validator_agent import filter_authentic_news
except ImportError:
    # Fallback if news_validator_agent is not available
    def filter_authentic_news(articles, threshold=0.7):
        return {"authentic": articles, "stats": {"pass_rate": 1.0}}


class BrowserNewsCollector(BaseBrowserCollector):
    """Collect news using AgentCore Browser"""

    SYSTEM_PROMPT = "You are a news extraction assistant. Extract news articles from RSS feeds and return structured JSON data."
    MAX_TOKENS = 2000

    PROMPT_TEMPLATE = """
### OBJECTIVE
Your task is to act as a news data extractor. Navigate to the provided RSS feed URL and extract news articles precisely according to the specified schema.

### CONTEXT OF THIS SEARCH
The user is collecting the top {max_results} news articles from the following RSS feed:
{url}

### INSTRUCTIONS
1. Go to the URL: {url}
2. Parse the RSS feed content (XML format).
3. Extract the top {max_results} news article entries from the feed.
4. Return the data as a single, valid JSON array. Do not include any other text or explanations in your response.
5. Skip any ads, promotional content, or non-article entries.

### OUTPUT SCHEMA
Return a JSON array of news article objects. If no articles are visible, return an empty array `[]`.
Each object must conform to this schema:
```json
[
  {{
    "title": "string",
    "description": "string",
    "url": "string",
    "source": "string",
    "published_at": "string (ISO 8601 format if available)"
  }}
]
```"""

    feeds = {
        "jp": "https://www.japantimes.co.jp/feed/",
        "us": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "uk": "https://feeds.bbci.co.uk/news/rss.xml",
        "fr": "https://www.france24.com/en/rss",
        "de": "https://rss.dw.com/xml/rss-en-all",
        "cn": "https://www.scmp.com/rss/91/feed",
        "kr": "https://www.koreaherald.com/rss/",
        "in": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
        "br": "https://rss.folha.uol.com.br/fsp/mundo/index.xml",
        "au": "https://www.abc.net.au/news/feed/51120/rss.xml",
    }

    def collect(self, country_code: str, max_results: int = 10, **kwargs) -> List[Dict]:
        """Alias for get_top_headlines"""
        return self.get_top_headlines(country_code, max_results)

    def get_top_headlines(
        self,
        country_code: str,
        max_results: int = 10,
        validate: bool = False,
        threshold: float = 0.7,
    ) -> List[Dict]:
        print(f"🌐 Collecting news for {country_code.upper()}...")

        try:
            articles = self._parse_rss_directly(country_code, max_results)
            if articles:
                print(f"✅ Collected {len(articles)} articles")

                if validate:
                    print(f"🔍 Validating authenticity (threshold={threshold})...")
                    result = filter_authentic_news(articles, threshold)
                    print(f"📊 Pass rate: {result['stats']['pass_rate']*100:.0f}%")
                    return result["authentic"]

                return articles
        except Exception as e:
            print(f"⚠️  Direct RSS failed: {str(e)[:100]}")
            try:
                print(f"🔄 Trying browser scraping...")
                url = self.feeds.get(country_code.lower(), self.feeds["jp"])
                articles = self._parse_rss_with_browser(url, max_results)
                if articles:
                    print(f"✅ Collected {len(articles)} articles via browser")
                    return articles
            except Exception as e:
                print(f"⚠️  Browser scraping failed: {str(e)[:100]}")

        return self._get_fallback_news(country_code, max_results)

    def _parse_rss_with_browser(self, url: str, max_results: int) -> List[Dict]:
        """Parse RSS feed using browser scraping"""
        prompt = self.PROMPT_TEMPLATE.format(url=url, max_results=max_results)
        articles = self._scrape_with_browser(prompt)

        for article in articles:
            text = f"{article.get('title', '')} {article.get('description', '')}"
            article["sentiment"] = self._calculate_sentiment(text)

        return articles

    def _parse_rss_directly(self, country_code: str, max_results: int) -> List[Dict]:
        """Direct RSS parsing"""

        url = self.feeds.get(country_code.lower(), self.feeds["jp"])
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        items = root.findall(".//item") or root.findall(
            ".//{http://www.w3.org/2005/Atom}entry"
        )

        articles = []
        for item in items[:max_results]:
            title = self._get_elem_text(
                item, ["title", "{http://www.w3.org/2005/Atom}title"]
            )
            desc = (
                self._get_elem_text(
                    item, ["description", "{http://www.w3.org/2005/Atom}summary"]
                )
                or title
            )
            link = (
                self._get_elem_text(item, ["link", "{http://www.w3.org/2005/Atom}link"])
                or url
            )

            if title and len(title) > 5:
                articles.append(
                    {
                        "title": title[:150],
                        "description": re.sub(r"<[^>]*>", "", desc)[:200],
                        "url": link,
                        "source": url.split("/")[2],
                        "sentiment": self._calculate_sentiment(title + " " + desc),
                        "published_at": datetime.now().isoformat(),
                    }
                )

        return articles

    def _get_elem_text(self, item, tags: List[str]) -> str:
        """Get text from first matching tag"""
        for tag in tags:
            elem = item.find(tag)
            if elem is not None:
                return (elem.text or elem.get("href", "")).strip()
        return ""

    def _get_fallback_news(self, country_code: str, max_results: int) -> List[Dict]:
        """Generate fallback data"""
        return [
            {
                "title": f"MOCK",
                "description": "Sample news",
                "source": "fallback",
                "sentiment": 0.0,
                "published_at": datetime.now().isoformat(),
                "url": "https://example.com",
            }
        ][:max_results]
