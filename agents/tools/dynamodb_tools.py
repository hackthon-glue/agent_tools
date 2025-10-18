"""DynamoDB tools for user and job data access"""

import boto3
from typing import Dict, List, Optional
from strands import tool
from .config import ToolConfig
from .base_tool import DataSourceTool


class DynamoDBTool(DataSourceTool):
    """DynamoDB data access following SOLID principles"""

    def _create_client(self):
        return boto3.resource("dynamodb", region_name=ToolConfig.AWS_REGION)

    def execute(self, operation: str, **kwargs) -> Dict:
        try:
            if operation == "get_user":
                return self._get_user(kwargs["user_id"])
            elif operation == "get_jobs":
                return self._get_jobs(kwargs.get("filters"))
            elif operation == "get_github":
                return self._get_github(kwargs["user_id"])
        except Exception as e:
            return self.handle_error(e, kwargs)

    def _get_user(self, user_id: str) -> Dict:
        table = self.client.Table(ToolConfig.USERS_TABLE)
        response = table.get_item(Key={"user_id": user_id})
        return response.get("Item", {})

    def _get_jobs(self, filters: Optional[Dict]) -> List[Dict]:
        table = self.client.Table(ToolConfig.JOBS_TABLE)
        if filters:
            from boto3.dynamodb.conditions import Attr

            filter_expr = None
            for key, value in filters.items():
                condition = Attr(key).eq(value)
                filter_expr = (
                    condition if filter_expr is None else filter_expr & condition
                )
            response = table.scan(FilterExpression=filter_expr)
        else:
            response = table.scan()
        return response.get("Items", [])

    def _get_github(self, user_id: str) -> Dict:
        table = self.client.Table(ToolConfig.GITHUB_TABLE)
        response = table.get_item(Key={"user_id": user_id})
        return response.get("Item", {})


# Singleton instance
_dynamodb_tool = DynamoDBTool()


@tool
def get_user_profile(user_id: str) -> Dict:
    """Get user profile from DynamoDB

    Args:
        user_id: User ID to retrieve

    Returns:
        User profile data including skills, experience, preferences
    """
    return _dynamodb_tool.execute("get_user", user_id=user_id)


@tool
def get_job_listings(filters: Optional[Dict] = None) -> List[Dict]:
    """Get job listings from DynamoDB

    Args:
        filters: Optional filters (e.g., {'location': 'Tokyo', 'role': 'Engineer'})

    Returns:
        List of job listings
    """
    return _dynamodb_tool.execute("get_jobs", filters=filters)


@tool
def get_github_profile(user_id: str) -> Dict:
    """Get GitHub profile data from DynamoDB

    Args:
        user_id: User ID to retrieve GitHub data for

    Returns:
        GitHub profile data including repos, languages, contributions
    """
    return _dynamodb_tool.execute("get_github", user_id=user_id)
