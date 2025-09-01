"""Base class and common functionality for travel tools."""

import logging
from typing import Dict, Any

from ..services.travel_service import TravelService
from ..core.database import get_db

# Set up logging
logger = logging.getLogger(__name__)


class TravelToolBase:
    """Base class for travel tools with common functionality."""

    @staticmethod
    def _get_travel_service() -> TravelService:
        """Get a travel service instance with database session."""
        db = next(get_db())
        return TravelService(db)

    @staticmethod
    def _handle_error(operation: str, error: Exception, **context) -> Dict[str, Any]:
        """Handle errors consistently across all tools."""
        error_msg = f"Error {operation}: {str(error)}"
        logger.error(f"{error_msg} - {type(error).__name__}: {str(error)}")

        return {
            "response": f"Error {operation}: {str(error)}",
            "success": False,
            "error_code": f"{operation.upper()}_ERROR",
            "error_message": str(error),
            "tool_calls": [],
            **context,
        }

    @staticmethod
    def _create_success_response(message: str, **data) -> Dict[str, Any]:
        """Create a consistent success response."""
        return {
            "response": message,
            "success": True,
            "tool_calls": [],
            **data,
        }
