"""SNS trends collector using Google Trends"""

from typing import Dict, List
from datetime import datetime
from .base import BaseBrowserCollector


class BrowserTrendCollector(BaseBrowserCollector):
    """Collect trends from Google Trends"""

    MAX_TOKENS = 2000

    PROMPT_TEMPLATE = """
### OBJECTIVE
Your task is to act as a data extractor. Navigate to the provided URL and extract trending topics information precisely according to the specified schema.

### CONTEXT OF THIS SEARCH
The user is looking for the most popular daily search trends in a specific country.

### INSTRUCTIONS
1.  Go to the URL: {url}
2.  The page displays the daily trending searches.
3.  Extract the top {num_results} trending topics from the page.
4.  Return the data as a single, valid JSON array. Do not include any other text or explanations in your response.

### OUTPUT SCHEMA
Return a JSON array of trend objects. If no trends are visible, return an empty array `[]`.
Each object must conform to this schema:
```json
[
  {{
    "topic": "string - The name of the trending topic or hashtag",
    "description": "string - A brief, one-sentence explanation of why it is trending",
    "category": "string - Classify into one of: entertainment, food, nature, animals, fashion, sports, technology, politics, business, other"
  }},...
]
```
"""

    GEO_MAP = {
        "jp": "JP",
        "us": "US",
        "uk": "GB",
        "fr": "FR",
        "de": "DE",
        "cn": "CN",
        "kr": "KR",
        "in": "IN",
        "br": "BR",
        "au": "AU",
    }

    def collect(
        self, country_code: str, hours: int = 168, num_results: int = 10, **kwargs
    ) -> List[Dict]:
        """Alias for get_trending_topics"""
        return self.get_trending_topics(country_code, hours, num_results)

    def get_trending_topics(
        self, country_code: str, hours: int = 168, num_results: int = 10
    ) -> List[Dict]:
        """
        Searches for trends based on the country along with the search context.

        Args:
            country_code (str): IATA code for the origin airport (e.g., "HND").
            hours(int): The number of hours to look back. Defaults to 168.
            num_results (int): The number of trend results to return.

        Returns:
            Dict[str, Any]: A dictionary containing the search context and the list of found trends.
        """
        print(f"📱 Collecting trends for {country_code.upper()}...")

        url = self._build_google_trend_url(country_code, hours)

        prompt = self.PROMPT_TEMPLATE.format(url=url, num_results=num_results)

        trends = self._scrape_with_browser(prompt=prompt)

        if trends:
            for t in trends:
                t.update(
                    {
                        "country": country_code.upper(),
                        "platform": "google_trends",
                        "timestamp": datetime.now().isoformat(),
                        "sentiment": self._calculate_sentiment(
                            t.get("topic", "") + " " + t.get("description", "")
                        ),
                    }
                )
            print(f"✅ Found {len(trends)} trends")
            return trends[:num_results]

        return self._get_fallback_trends(country_code, num_results)

    def _build_google_trend_url(self, country_code: str, hours: int = 168) -> str:
        """Builds a Google Trends.com URL from search parameters."""
        geo = self.GEO_MAP.get(country_code.lower(), "US")
        base_url = f"https://trends.google.com/trends/trendingsearches/daily"

        geo_query = f"?geo={geo}"
        status_query = "&status=active"
        url = base_url + geo_query + status_query

        span_query = f"&hours={hours}"
        url += span_query

        return url

    def _get_fallback_trends(self, country_code: str, num_results: int) -> List[Dict]:
        """Fallback trend data"""
        return [
            {
                "topic": f"Mock",
                "description": "Mock trend",
                "sentiment": 0.0,
                "category": "news",
                "country": country_code.upper(),
                "platform": "fallback",
                "timestamp": datetime.now().isoformat(),
            }
        ][:num_results]
