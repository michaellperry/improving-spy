"""Tools for route and journey planning."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import re

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
        departure_date: str,
    ) -> Dict[str, Any]:
        """Plan a journey between two cities.

        Args:
            origin_city_id: Origin city ID
            destination_city_id: Destination city ID
            departure_date: Departure date and time (ISO 8601 format string)

        Returns:
            Dict containing journey plan
        """
        # Parse the departure_date string to datetime - be permissive for LLM input
        try:
            if isinstance(departure_date, str):
                # Try multiple date parsing strategies
                departure_datetime = cls._parse_date_string(departure_date)
            else:
                departure_datetime = departure_date
        except ValueError as e:
            return {
                "response": f"Invalid departure date format: {departure_date}. Please provide a date in formats like '2024-01-15T08:00:00', 'August 31, 2025', or '2024-01-15'",
                "success": False,
                "journey_plan": None,
                "origin": origin_city_id,
                "destination": destination_city_id,
                "departure_date": departure_date,
                "tool_calls": [],
            }
        logger.debug(
            f"Planning journey from {origin_city_id} to " f"{destination_city_id}"
        )

        try:
            travel_service = cls._get_travel_service()
            journey_result = travel_service.plan_journey(
                origin_city_id, destination_city_id, departure_datetime
            )

            if journey_result["success"]:
                return cls._create_success_response(
                    journey_result["message"],
                    journey_plan=journey_result["journey_plan"],
                    origin=origin_city_id,
                    destination=destination_city_id,
                    departure_date=departure_datetime.isoformat(),
                )
            else:
                return {
                    "response": journey_result["message"],
                    "success": False,
                    "journey_plan": None,
                    "origin": origin_city_id,
                    "destination": destination_city_id,
                    "departure_date": departure_datetime.isoformat(),
                    "tool_calls": [],
                }

        except Exception as e:
            return cls._handle_error(
                "planning journey",
                e,
                journey_plan=None,
                origin=origin_city_id,
                destination=destination_city_id,
                departure_date=departure_datetime.isoformat(),
            )

    @classmethod
    def _parse_date_string(cls, date_string: str) -> datetime:
        """Parse various date string formats into a datetime object.
        
        Args:
            date_string: Date string in various formats
            
        Returns:
            datetime object
            
        Raises:
            ValueError: If the date string cannot be parsed
        """
        # Clean up the input
        date_string = date_string.strip()
        
        # Try ISO format first (most common for APIs)
        try:
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except ValueError:
            pass
        
        # Try common date formats
        date_formats = [
            '%B %d, %Y',      # August 31, 2025
            '%b %d, %Y',      # Aug 31, 2025
            '%B %d %Y',       # August 31 2025
            '%b %d %Y',       # Aug 31 2025
            '%Y-%m-%d',       # 2025-08-31
            '%m/%d/%Y',       # 08/31/2025
            '%d/%m/%Y',       # 31/08/2025
            '%Y-%m-%d %H:%M:%S',  # 2025-08-31 14:30:00
            '%Y-%m-%d %H:%M',     # 2025-08-31 14:30
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        
        # If no format works, try to extract date components with regex
        # Pattern for "Month Day, Year" format
        month_day_year = re.match(r'(\w+)\s+(\d{1,2}),?\s+(\d{4})', date_string)
        if month_day_year:
            month_str, day_str, year_str = month_day_year.groups()
            try:
                # Try to parse with month name
                return datetime.strptime(f"{month_str} {day_str}, {year_str}", '%B %d, %Y')
            except ValueError:
                try:
                    # Try abbreviated month
                    return datetime.strptime(f"{month_str} {day_str}, {year_str}", '%b %d, %Y')
                except ValueError:
                    pass
        
        # If all else fails, raise ValueError
        raise ValueError(f"Unable to parse date string: {date_string}")
