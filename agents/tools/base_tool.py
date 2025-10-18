"""Base classes for tools following SOLID principles"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Abstract base class for all tools (Interface Segregation Principle)"""

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the tool's main functionality"""
        pass

    def handle_error(self, error: Exception, context: Dict = None) -> Dict:
        """Unified error handling"""
        logger.error(f"{self.__class__.__name__} error: {error}", extra=context or {})
        return {"error": str(error), "tool": self.__class__.__name__}


class DataSourceTool(BaseTool):
    """Base class for data source tools (Single Responsibility Principle)"""

    def __init__(self, client=None):
        """Dependency Injection for testability"""
        self._client = client

    @property
    def client(self):
        """Lazy initialization of client"""
        if self._client is None:
            self._client = self._create_client()
        return self._client

    @abstractmethod
    def _create_client(self):
        """Create the specific client (Factory pattern)"""
        pass
