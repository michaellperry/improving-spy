"""Tools for executing travel operations."""

import logging
from typing import Dict, Any

from .travel_base import TravelToolBase

# Set up logging
logger = logging.getLogger(__name__)


class TravelExecutionTools(TravelToolBase):
    """Tools for executing travel operations."""

    @classmethod
    def travel(cls, context_spy_id: str, service_id: str) -> Dict[str, Any]:
        """Execute travel on a specific service, updating spy state.

        Args:
            context_spy_id: The ID of the spy from context (automatically bound)
            service_id: Service identifier to travel on

        Returns:
            Dict containing travel result and updated state
        """
        logger.info(
            f"Executing travel on service: {service_id} for spy: " f"{context_spy_id}"
        )

        try:
            travel_service = cls._get_travel_service()
            result = travel_service.execute_travel(context_spy_id, service_id)

            if result["success"]:
                return cls._create_success_response(
                    f"Successfully traveled on service {service_id}",
                    spy_id=context_spy_id,
                    service_id=service_id,
                    travel_result=result["travel_result"],
                    updated_state=result["updated_state"],
                )
            else:
                return {
                    "response": (
                        f"Travel failed on service {service_id}: "
                        f"{result['error_code']}"
                    ),
                    "success": False,
                    "spy_id": context_spy_id,
                    "service_id": service_id,
                    "error_code": result["error_code"],
                    "error_message": result["error_message"],
                    "tool_calls": [],
                }

        except Exception as e:
            return cls._handle_error(
                "executing travel",
                e,
                spy_id=context_spy_id,
                service_id=service_id,
            )

    @classmethod
    def get_travel_state(cls, context_spy_id: str) -> Dict[str, Any]:
        """Get current travel state for the context spy.

        Args:
            context_spy_id: Spy identifier from context (automatically bound)

        Returns:
            Dict containing travel state information
        """
        logger.info(f"Getting travel state for spy: {context_spy_id}")

        try:
            travel_service = cls._get_travel_service()
            travel_state = travel_service.get_travel_state(context_spy_id)

            if travel_state:
                return cls._create_success_response(
                    f"Current travel state for spy {context_spy_id}",
                    spy_id=context_spy_id,
                    travel_state=travel_state.model_dump(),
                )
            else:
                return {
                    "response": f"No travel state found for spy {context_spy_id}",
                    "spy_id": context_spy_id,
                    "travel_state": None,
                    "tool_calls": [],
                }

        except Exception as e:
            return cls._handle_error(
                "getting travel state",
                e,
                spy_id=context_spy_id,
                travel_state=None,
            )
