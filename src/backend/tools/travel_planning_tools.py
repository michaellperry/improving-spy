"""Tools for route and journey planning."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .travel_base import TravelToolBase

# Set up logging
logger = logging.getLogger(__name__)


class PlanningTools(TravelToolBase):
    """Tools for route and journey planning."""

    @classmethod
    def plan_route(
        cls,
        context_spy_id: str,
        origin_id: str,
        dest_id: str,
        depart_after: str,
        prefs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate guaranteed valid travel itineraries.

        Args:
            context_spy_id: The ID of the spy from context (automatically bound)
            origin_id: Starting city
            dest_id: Destination city
            depart_after: Earliest departure time (ISO 8601) - deprecated,
                now uses spy's current time
            prefs: Travel preferences including min_transfer time

        Returns:
            Dict containing planned route itinerary
        """
        logger.debug(
            f"Planning route from {origin_id} to {dest_id} for spy: "
            f"{context_spy_id}"
        )

        try:
            travel_service = cls._get_travel_service()
            route_result = travel_service.plan_route(
                context_spy_id, origin_id, dest_id, prefs or {}
            )

            if route_result["success"]:
                return cls._create_success_response(
                    f"Route planned successfully from {origin_id} to {dest_id}",
                    spy_id=context_spy_id,
                    origin_id=origin_id,
                    dest_id=dest_id,
                    itinerary=route_result["itinerary"],
                    total_duration=route_result["total_duration"],
                    spy_current_time=route_result.get("spy_current_time"),
                )
            else:
                return {
                    "response": (
                        f"Route planning failed: " f"{route_result['error_message']}"
                    ),
                    "success": False,
                    "spy_id": context_spy_id,
                    "origin_id": origin_id,
                    "dest_id": dest_id,
                    "itinerary": None,
                    "error_message": route_result["error_message"],
                    "tool_calls": [],
                }

        except Exception as e:
            return cls._handle_error(
                "planning route",
                e,
                spy_id=context_spy_id,
                origin_id=origin_id,
                dest_id=dest_id,
                itinerary=None,
            )

    @classmethod
    def plan_journey(
        cls,
        origin_city_id: str,
        destination_city_id: str,
        departure_date: datetime,
    ) -> Dict[str, Any]:
        """Plan a journey between two cities.

        Args:
            origin_city_id: Origin city ID
            destination_city_id: Destination city ID
            departure_date: Departure date and time

        Returns:
            Dict containing journey plan
        """
        logger.debug(
            f"Planning journey from {origin_city_id} to " f"{destination_city_id}"
        )

        try:
            travel_service = cls._get_travel_service()
            journey_result = travel_service.plan_journey(
                origin_city_id, destination_city_id, departure_date
            )

            if journey_result["success"]:
                return cls._create_success_response(
                    journey_result["message"],
                    journey_plan=journey_result["journey_plan"],
                    origin=origin_city_id,
                    destination=destination_city_id,
                    departure_date=departure_date.isoformat(),
                )
            else:
                return {
                    "response": journey_result["message"],
                    "success": False,
                    "journey_plan": None,
                    "origin": origin_city_id,
                    "destination": destination_city_id,
                    "departure_date": departure_date.isoformat(),
                    "tool_calls": [],
                }

        except Exception as e:
            return cls._handle_error(
                "planning journey",
                e,
                journey_plan=None,
                origin=origin_city_id,
                destination=destination_city_id,
                departure_date=departure_date.isoformat(),
            )
