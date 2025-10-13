"""
News Validation Agent - Minimal Implementation
AgentCore + Context7 + Sequential Thinking + Hugging Face
"""

from strands import Agent, tool
from strands.models import BedrockModel
from typing import Dict, List
import os
import json


@tool
def validate_article_authenticity(
    title: str,
    description: str,
    threshold: float = 0.7
) -> Dict:
    """
    記事の真偽を評価し、閾値で判定
    
    Args:
        title: 記事タイトル
        description: 記事説明
        threshold: 信頼度閾値 (0-1)
    
    Returns:
        {
            "is_authentic": bool,
            "confidence": float,
            "label": str,
            "reasoning": str
        }
    """
    content = f"{title} {description}"
    
    # Sequential Thinkingで段階的に評価
    validator = Agent(
        model=BedrockModel(
            model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
            temperature=0.1,
            max_tokens=500
        ),
        system_prompt="""あなたはニュース記事の真偽を評価する専門家です。
以下の観点で段階的に分析してください:
1. タイトルの扇情性チェック
2. 内容の具体性・客観性
3. 情報源の明示有無
4. 論理的整合性

最終的に0-1の信頼度スコアを出力してください。"""
    )
    
    prompt = f"""以下の記事を評価してください:

タイトル: {title}
説明: {description}

JSON形式で出力:
{{
    "confidence": 0.0-1.0の数値,
    "label": "REAL" or "FAKE",
    "reasoning": "評価理由（日本語）"
}}"""
    
    try:
        response = validator(prompt)
        
        # JSON抽出
        text = str(response)
        start = text.find('{')
        end = text.rfind('}') + 1
        
        if start >= 0 and end > start:
            result = json.loads(text[start:end])
            confidence = float(result.get("confidence", 0.5))
            label = result.get("label", "UNKNOWN")
            reasoning = result.get("reasoning", "評価不可")
            
            return {
                "is_authentic": confidence >= threshold and label == "REAL",
                "confidence": round(confidence, 3),
                "label": label,
                "reasoning": reasoning,
                "threshold": threshold
            }
    except Exception as e:
        print(f"⚠️ 評価エラー: {e}")
    
    return {
        "is_authentic": False,
        "confidence": 0.0,
        "label": "ERROR",
        "reasoning": "評価失敗",
        "threshold": threshold
    }


@tool
def filter_authentic_news(
    articles: List[Dict],
    threshold: float = 0.7
) -> Dict:
    """
    記事リストをフィルタリング
    
    Args:
        articles: 記事リスト [{"title": str, "description": str, ...}]
        threshold: 信頼度閾値
    
    Returns:
        {
            "authentic": List[Dict],
            "filtered_out": List[Dict],
            "stats": Dict
        }
    """
    authentic = []
    filtered = []
    
    for article in articles:
        title = article.get("title", "")
        desc = article.get("description", "")
        
        validation = validate_article_authenticity(title, desc, threshold)
        
        article["validation"] = validation
        
        if validation["is_authentic"]:
            authentic.append(article)
            print(f"✅ {validation['confidence']:.2f} - {title[:50]}")
        else:
            filtered.append(article)
            print(f"🚫 {validation['confidence']:.2f} - {title[:50]}")
    
    return {
        "authentic": authentic,
        "filtered_out": filtered,
        "stats": {
            "total": len(articles),
            "authentic_count": len(authentic),
            "filtered_count": len(filtered),
            "pass_rate": round(len(authentic) / len(articles), 2) if articles else 0,
            "threshold": threshold
        }
    }


def create_news_validator_agent() -> Agent:
    """ニュース検証エージェント作成"""
    return Agent(
        tools=[validate_article_authenticity, filter_authentic_news],
        model=BedrockModel(
            model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
            temperature=0,
            max_tokens=2000
        ),
        system_prompt="""あなたはニュース記事の真偽を検証する専門エージェントです。

利用可能なツール:
- validate_article_authenticity: 単一記事の真偽評価
- filter_authentic_news: 記事リストの一括フィルタリング

信頼度スコア (0-1):
- 0.8-1.0: 高信頼度（客観的事実、情報源明示）
- 0.6-0.8: 中信頼度（一般的なニュース）
- 0.4-0.6: 低信頼度（扇情的、曖昧）
- 0.0-0.4: 疑わしい（フェイクニュースの可能性）

デフォルト閾値: 0.7"""
    )


# 簡易テスト用
if __name__ == "__main__":
    agent = create_news_validator_agent()
    
    test_articles = [
        {
            "title": "政府が新政策を発表、経済成長を促進",
            "description": "政府は本日、経済成長を促進するための新政策を発表しました。"
        },
        {
            "title": "衝撃！宇宙人が地球に到着か！？",
            "description": "未確認情報によると、宇宙人が地球に到着した可能性があるとのこと。"
        }
    ]
    
    print("\n🧪 テスト実行\n")
    result = agent(f"以下の記事を検証してください: {json.dumps(test_articles, ensure_ascii=False)}")
    print(f"\n結果:\n{result}")
