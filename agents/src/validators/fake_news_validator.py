"""
Fake News Detection Tool for Strands Agents
"""

import boto3
import json
import os
from typing import Dict, List
from strands import tool

try:
    import sagemaker
    from sagemaker.huggingface import HuggingFaceModel
    SAGEMAKER_AVAILABLE = True
except ImportError:
    SAGEMAKER_AVAILABLE = False


class HuggingFacePredictor:
    """Hugging Face model predictor"""

    _predictor = None

    @classmethod
    def get_predictor(cls):
        """Get or create predictor"""
        if not SAGEMAKER_AVAILABLE:
            raise ImportError("sagemaker module not available")
            
        if cls._predictor is None:

            try:
                role = sagemaker.get_execution_role()
            except ValueError:
                iam = boto3.client("iam")
                role = iam.get_role(RoleName="sagemaker_execution_role")["Role"]["Arn"]

            hub = {
                "HF_MODEL_ID": "Pulk17/Fake-News-Detection",
                "HF_TASK": "text-classification",
                "HF_OPTIMUM_BATCH_SIZE": "1",
                "HF_OPTIMUM_SEQUENCE_LENGTH": "512",
            }

            model = HuggingFaceModel(
                transformers_version="4.43.2",
                pytorch_version="2.1.2",
                py_version="py310",
                env=hub,
                role=role,
            )

            model._is_compiled_model = True

            cls._predictor = model.deploy(
                initial_instance_count=1, instance_type="ml.inf2.xlarge"
            )

        return cls._predictor

    @classmethod
    def predict(cls, text: str) -> Dict:
        """Predict if text is fake or real"""
        predictor = cls.get_predictor()
        result = predictor.predict({"inputs": text})

        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return {"label": "FAKE", "score": 0.0}


@tool
def validate_news_content(content: str, threshold: float = 0.7) -> Dict:
    """
    Validate if news content is real or fake using Hugging Face model.

    Args:
        content: News article text (title + description)
        threshold: Confidence threshold (0-1), default 0.7

    Returns:
        {
            "is_valid": bool,
            "label": str,  # "REAL" or "FAKE"
            "confidence": float,
            "content_preview": str
        }
    """
    try:
        result = HuggingFacePredictor.predict(content)
        label = result.get("label", "FAKE")
        confidence = result.get("score", 0.0)
        is_valid = label == "REAL" and confidence >= threshold

        return {
            "is_valid": is_valid,
            "label": label,
            "confidence": round(confidence, 3),
            "content_preview": content[:100],
        }
    except Exception as e:
        print(f"⚠️  Validation error: {e}")
        return {
            "is_valid": True,
            "label": "UNVALIDATED",
            "confidence": 0.5,
            "content_preview": content[:100],
            "error": str(e),
        }


@tool
def filter_fake_news(articles: List[Dict], threshold: float = 0.7) -> List[Dict]:
    """
    Filter fake news from browser-collected articles.

    Args:
        articles: List of articles with 'title' and 'description'
        threshold: Confidence threshold (0-1), default 0.7

    Returns:
        List of validated articles with validation metadata
    """
    validated = []

    for article in articles:
        content = f"{article.get('title', '')} {article.get('description', '')}"
        validation = validate_news_content(content, threshold)

        if validation["is_valid"]:
            article["validation"] = validation
            validated.append(article)
        else:
            print(f"🚫 Filtered: {article.get('title', '')[:50]}...")

    print(f"✅ Validated {len(validated)}/{len(articles)} articles")
    return validated


# Mock validator for development
@tool
def validate_news_content_mock(content: str, threshold: float = 0.7) -> Dict:
    """
    Mock validation for development (no SageMaker needed).

    Args:
        content: News article text
        threshold: Confidence threshold (0-1)

    Returns:
        Validation result dictionary
    """
    fake_keywords = ["hoax", "conspiracy", "unverified", "rumor"]
    has_fake = any(kw in content.lower() for kw in fake_keywords)

    confidence = 0.4 if has_fake else 0.9
    label = "FAKE" if has_fake else "REAL"

    return {
        "is_valid": confidence >= threshold,
        "label": label,
        "confidence": confidence,
        "content_preview": content[:100],
    }
