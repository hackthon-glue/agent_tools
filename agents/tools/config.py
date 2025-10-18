"""Configuration for tools"""

import os
from dotenv import load_dotenv

load_dotenv()


class ToolConfig:
    """Centralized configuration for all tools"""

    # AWS
    AWS_REGION = os.getenv("AWS_REGION", "us-west-2")

    # DynamoDB
    USERS_TABLE = os.getenv("DYNAMODB_USERS_TABLE", "recruitment_users")
    JOBS_TABLE = os.getenv("DYNAMODB_JOBS_TABLE", "recruitment_jobs")
    GITHUB_TABLE = os.getenv("DYNAMODB_GITHUB_TABLE", "recruitment_github_profiles")

    # Knowledge Base
    KB_ID = os.getenv("KNOWLEDGE_BASE_ID", "KB123")
    KB_USE_RERANK = os.getenv("KB_USE_RERANK", "true").lower() == "true"
    KB_SEARCH_TYPE = os.getenv("KB_SEARCH_TYPE", "HYBRID")
    KB_MAX_RESULTS = int(os.getenv("KB_MAX_RESULTS", "5"))
    KB_TEMPERATURE = float(os.getenv("KB_TEMPERATURE", "0.7"))
    KB_MAX_TOKENS = int(os.getenv("KB_MAX_TOKENS", "512"))

    # Memory
    MEMORY_ID = os.getenv("MEMORY_ID")
    CONCIERGE_SESSION_TTL = int(os.getenv("CONCIERGE_SESSION_TTL", "3600"))
    INTERVIEWER_SESSION_TTL = int(os.getenv("INTERVIEWER_SESSION_TTL", "1800"))

    # Model
    CLAUDE_MODEL_ID = os.getenv(
        "CLAUDE_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    )
