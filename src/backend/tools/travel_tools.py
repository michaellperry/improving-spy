"""Travel tools for AI agent operations."""

from typing import Dict, Any, Optional
from datetime import datetime

# Models are available through the package __init__.py for backward compatibility

# Import tool classes from the new split files
from .travel_map_tools import MapTools
from .travel_schedule_tools import ScheduleTools
from .travel_execution_tools import TravelExecutionTools
from .travel_planning_tools import PlanningTools


class TravelTools:
    """Main travel tools class that combines all tool categories."""

    # Compatibility methods for backward compatibility with tests
    @classmethod
    def get_map(cls) -> Dict[str, Any]:
        """Get the complete transportation network graph."""
        return MapTools.get_map()

    @classmethod
    def get_schedule(
        cls,
        origin_id: str,
        date_range: str,
        destination_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieve available train services between cities."""
        return ScheduleTools.get_schedule(origin_id, date_range, destination_id)

    @classmethod
    def travel(cls, context_spy_id: str, service_id: str) -> Dict[str, Any]:
        """Execute travel on a specific service, updating spy state."""
        return TravelExecutionTools.travel(context_spy_id, service_id)

    @classmethod
    def plan_route(
        cls,
        context_spy_id: str,
        origin_id: str,
        dest_id: str,
        depart_after: str,
        prefs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate guaranteed valid travel itineraries."""
        return PlanningTools.plan_route(
            context_spy_id, origin_id, dest_id, depart_after, prefs
        )

    @classmethod
    def get_travel_state(cls, context_spy_id: str) -> Dict[str, Any]:
        """Get current travel state for the context spy."""
        return TravelExecutionTools.get_travel_state(context_spy_id)

    @classmethod
    def get_available_cities(cls) -> Dict[str, Any]:
        """Get list of available cities for travel."""
        return MapTools.get_available_cities()

    @classmethod
    def get_train_schedules(
        cls,
        origin_city_id: str,
        destination_city_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get train schedules from a city, optionally filtered by destination."""
        return ScheduleTools.get_train_schedules(origin_city_id, destination_city_id)

    @classmethod
    def plan_journey(
        cls,
        origin_city_id: str,
        destination_city_id: str,
        departure_date: datetime,
    ) -> Dict[str, Any]:
        """Plan a journey between two cities."""
        return PlanningTools.plan_journey(
            origin_city_id, destination_city_id, departure_date
        )

    @classmethod
    def get_tools(cls, context_spy_id: str):
        """Return the list of tools bound to a specific spy context.

        Args:
            context_spy_id: The spy ID to bind tools to

        Returns:
            List of tool definitions with context-bound functions
        """
        return [
            {
                "name": "get_map",
                "description": (
                    "Get the complete transportation network graph with cities "
                    "and route information. Use this when you need to understand "
                    "the available travel options and city connections."
                ),
                "function": MapTools.get_map,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "get_schedule",
                "description": (
                    "Retrieve available train services between cities. Use this "
                    "when you need to find train schedules for travel planning."
                ),
                "function": ScheduleTools.get_schedule,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "origin_id": {
                            "type": "string",
                            "description": "Starting city identifier",
                        },
                        "date_range": {
                            "type": "string",
                            "description": "Time window for search",
                        },
                        "destination_id": {
                            "type": "string",
                            "description": "Optional target city filter",
                        },
                    },
                    "required": ["origin_id", "date_range"],
                },
            },
            {
                "name": "travel",
                "description": (
                    "Execute travel on a specific service. Use this when you "
                    "want to travel on a train service. Your date and time will "
                    "be updated."
                ),
                "function": lambda service_id: TravelExecutionTools.travel(
                    context_spy_id, service_id
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service_id": {
                            "type": "string",
                            "description": "Service identifier to travel on",
                        },
                    },
                    "required": ["service_id"],
                },
            },
            {
                "name": "plan_route",
                "description": (
                    "Generate guaranteed valid travel itineraries between "
                    "cities. Use this when you need to plan a complete journey "
                    "with multiple connections."
                ),
                "function": lambda origin_id, dest_id, depart_after, prefs=None: (
                    PlanningTools.plan_route(
                        context_spy_id, origin_id, dest_id, depart_after, prefs
                    )
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "origin_id": {
                            "type": "string",
                            "description": "Starting city",
                        },
                        "dest_id": {
                            "type": "string",
                            "description": "Destination city",
                        },
                        "depart_after": {
                            "type": "string",
                            "description": "Earliest departure time (ISO 8601 format)",
                        },
                        "prefs": {
                            "type": "object",
                            "description": (
                                "Travel preferences including min_transfer time"
                            ),
                        },
                    },
                    "required": ["origin_id", "dest_id", "depart_after"],
                },
            },
            {
                "name": "get_travel_state",
                "description": (
                    "Get your current time, location, and inventory. Use this "
                    "when you need to check where you are, what time it is, "
                    "and what you have."
                ),
                "function": lambda: TravelExecutionTools.get_travel_state(
                    context_spy_id
                ),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "get_available_cities",
                "description": (
                    "Get list of all available cities for travel. Use this "
                    "when you need to see what cities are accessible."
                ),
                "function": MapTools.get_available_cities,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "get_train_schedules",
                "description": (
                    "Get train schedules from a city, optionally filtered by "
                    "destination. Use this when you need to find train times "
                    "from an origin city, with or without specifying a destination."
                ),
                "function": ScheduleTools.get_train_schedules,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "origin_city_id": {
                            "type": "string",
                            "description": "Origin city ID",
                        },
                        "destination_city_id": {
                            "type": "string",
                            "description": (
                                "Optional destination city ID. If not provided, "
                                "returns all schedules from origin city"
                            ),
                        },
                    },
                    "required": ["origin_city_id"],
                },
            },
            {
                "name": "plan_journey",
                "description": (
                    "Plan a complete journey between two cities. Use this "
                    "when you need to plan travel with specific departure times."
                ),
                "function": PlanningTools.plan_journey,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "origin_city_id": {
                            "type": "string",
                            "description": "Origin city ID",
                        },
                        "destination_city_id": {
                            "type": "string",
                            "description": "Destination city ID",
                        },
                        "departure_date": {
                            "type": "string",
                            "description": "Departure date and time (ISO 8601 format)",
                        },
                    },
                    "required": [
                        "origin_city_id",
                        "destination_city_id",
                        "departure_date",
                    ],
                },
            },
        ]
