"""Base collector class for browser-based data collection"""

from strands import Agent
from strands.models import BedrockModel
from strands_tools.browser import AgentCoreBrowser
from typing import Dict, List
from abc import ABC, abstractmethod
import json
import re


class BaseBrowserCollector(ABC):
    """Base class for browser-based data collectors"""

    SYSTEM_PROMPT = "Extract data as JSON."
    MODEL_ID = "us.anthropic.claude-sonnet-4-20250514-v1:0"
    TEMPERATURE = 0
    MAX_TOKENS = 1500

    def __init__(self, region: str = "us-west-2", timeout: int = 20):
        self.region = region
        self.timeout = timeout
        self.browser = None
        self.agent = None

    def _ensure_browser(self):
        """Lazy initialization of browser and agent"""
        if self.browser and self.agent:
            return

        try:
            self.browser = AgentCoreBrowser(region=self.region)
            self.agent = Agent(
                tools=[self.browser.browser],
                model=BedrockModel(
                    model_id=self.MODEL_ID,
                    temperature=self.TEMPERATURE,
                    max_tokens=self.MAX_TOKENS,
                ),
                system_prompt=self.SYSTEM_PROMPT,
            )
        except Exception as e:
            error_msg = str(e)
            if "UnrecognizedClientException" in error_msg or "security" in error_msg.lower():
                print(f"⚠️  AWS authentication failed. Please configure:")
                print(f"   1. AWS credentials: aws configure")
                print(f"   2. IAM permissions for bedrock-agentcore and bedrock:InvokeModel")
                print(f"   3. Enable Claude Sonnet 4.0 in Bedrock console")
            else:
                print(f"⚠️  Browser init failed: {error_msg[:100]}")
            self.browser = None
            self.agent = None

    def _parse_json_response(self, response, return_type: type = list):
        """Parse JSON from agent response"""
        try:
            if isinstance(response, return_type):
                return response

            text = (
                response.message.get("content", [{}])[0].get("text", "")
                if hasattr(response, "message")
                else str(response)
            )
            text = text.strip()

            pattern = r"\[[\s\S]*?\]" if return_type == list else r"\{[\s\S]*?\}"
            matches = list(re.finditer(pattern, text))

            for match in reversed(matches):
                try:
                    parsed = json.loads(match.group(0))
                    if isinstance(parsed, return_type):
                        return parsed
                except:
                    continue

            return json.loads(text) if text else ([] if return_type == list else {})
        except:
            return [] if return_type == list else {}

    def _scrape_with_browser(self, prompt: str) -> List[Dict]:
        """Generic browser scraping method"""
        self._ensure_browser()

        if not self.agent:
            print("⚠️  Browser not initialized - check AWS credentials and Bedrock access")
            return []

        try:
            response = self.agent(prompt)
            return self._parse_json_response(response, list)
        except Exception as e:
            print(f"⚠️  Scraping failed: {str(e)[:100]}")
            return []

    @abstractmethod
    def collect(self, *args, **kwargs):
        """Collect data - must be implemented by subclasses"""
        pass
