"""Tools for map and network operations."""

import logging
from typing import Dict, Any

from .travel_base import TravelToolBase

# Set up logging
logger = logging.getLogger(__name__)


class MapTools(TravelToolBase):
    """Tools for map and network operations."""

    @classmethod
    def get_map(cls) -> Dict[str, Any]:
        """Get the complete transportation network graph.

        Returns:
            Dict containing cities and route edges with timezone info
        """
        logger.info("Getting transportation network map")

        try:
            travel_service = cls._get_travel_service()
            map_data = travel_service.get_transportation_map()

            return cls._create_success_response(
                "Transportation network map retrieved successfully",
                cities=map_data["cities"],
                edges=map_data["edges"],
            )

        except Exception as e:
            return cls._handle_error(
                "getting transportation map",
                e,
                cities=[],
                edges=[],
            )

    @classmethod
    def get_available_cities(cls) -> Dict[str, Any]:
        """Get list of available cities for travel.

        Returns:
            Dict containing available cities
        """
        logger.info("Getting available cities")

        try:
            travel_service = cls._get_travel_service()
            cities = travel_service.get_available_cities()

            return cls._create_success_response(
                f"Found {len(cities)} available cities",
                cities=cities,
                count=len(cities),
            )

        except Exception as e:
            return cls._handle_error(
                "retrieving cities",
                e,
                cities=[],
                count=0,
            )
