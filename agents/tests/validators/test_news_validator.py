"""
Test News Validator Agent
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from validators.fake_news_validator import create_news_validator_agent, validate_article_authenticity, filter_authentic_news
import json


def test_single_validation():
    """単一記事の検証テスト"""
    print("\n🧪 Test 1: 単一記事検証\n")
    
    result = validate_article_authenticity(
        title="政府が新経済政策を発表、GDP成長率3%目標",
        description="政府は本日、経済成長を促進するための新政策パッケージを発表しました。専門家は実現可能性が高いと評価しています。",
        threshold=0.7
    )
    
    print(f"結果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    assert "is_authentic" in result
    assert "confidence" in result
    assert "label" in result


def test_batch_filtering():
    """バッチフィルタリングテスト"""
    print("\n🧪 Test 2: バッチフィルタリング\n")
    
    articles = [
        {
            "title": "東京オリンピック、過去最高のメダル獲得",
            "description": "日本代表チームは今大会で過去最高となる58個のメダルを獲得しました。"
        },
        {
            "title": "衝撃！宇宙人が東京に上陸か！？",
            "description": "未確認情報によると、昨夜東京に宇宙人が上陸した可能性があるとのこと。"
        },
        {
            "title": "新型コロナワクチン、効果を確認",
            "description": "厚生労働省は新型コロナワクチンの効果を確認したと発表しました。"
        }
    ]
    
    result = filter_authentic_news(articles, threshold=0.7)
    
    print(f"\n統計:")
    print(f"  総記事数: {result['stats']['total']}")
    print(f"  検証通過: {result['stats']['authentic_count']}")
    print(f"  フィルタ: {result['stats']['filtered_count']}")
    print(f"  通過率: {result['stats']['pass_rate']*100:.0f}%")
    
    assert result['stats']['total'] == 3
    assert result['stats']['authentic_count'] >= 1


def test_agent_integration():
    """エージェント統合テスト"""
    print("\n🧪 Test 3: エージェント統合\n")
    
    agent = create_news_validator_agent()
    
    test_data = [
        {
            "title": "日本経済、四半期連続でプラス成長",
            "description": "内閣府が発表した統計によると、日本経済は4四半期連続でプラス成長を記録しました。"
        }
    ]
    
    prompt = f"以下の記事を検証してください（閾値0.7）: {json.dumps(test_data, ensure_ascii=False)}"
    response = agent(prompt)
    
    print(f"エージェント応答:\n{response}")
    assert response is not None


if __name__ == "__main__":
    test_single_validation()
    test_batch_filtering()
    test_agent_integration()
    
    print("\n✅ 全テスト完了")
