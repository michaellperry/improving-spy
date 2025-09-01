"""Tools for schedule and service operations."""

import logging
from typing import Dict, Any, Optional

from .travel_base import TravelToolBase

# Set up logging
logger = logging.getLogger(__name__)


class ScheduleTools(TravelToolBase):
    """Tools for schedule and service operations."""

    @classmethod
    def get_schedule(
        cls,
        origin_id: str,
        date_range: str,
        destination_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieve available train services between cities.

        Args:
            origin_id: Starting city identifier
            date_range: Time window for search
            destination_id: Optional target city filter

        Returns:
            Dict containing available train services
        """
        logger.info(
            f"Getting train schedules from {origin_id} to "
            f"{destination_id or 'any destination'}"
        )

        try:
            travel_service = cls._get_travel_service()
            services = travel_service.get_available_services(
                origin_id, date_range, destination_id
            )

            return cls._create_success_response(
                f"Found {len(services)} available train services",
                services=services,
                origin_id=origin_id,
                date_range=date_range,
                destination_id=destination_id,
            )

        except Exception as e:
            return cls._handle_error(
                "getting train schedules",
                e,
                services=[],
                origin_id=origin_id,
                date_range=date_range,
                destination_id=destination_id,
            )

    @classmethod
    def get_train_schedules(
        cls,
        origin_city_id: str,
        destination_city_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get train schedules from a city, optionally filtered by destination.

        Args:
            origin_city_id: Origin city ID
            destination_city_id: Optional destination city ID. If not provided,
                returns all schedules from origin city

        Returns:
            Dict containing train schedules
        """
        if destination_city_id:
            logger.info(
                f"Getting train schedules from {origin_city_id} to "
                f"{destination_city_id}"
            )
        else:
            logger.info(f"Getting all train schedules from {origin_city_id}")

        try:
            travel_service = cls._get_travel_service()

            if destination_city_id:
                schedules = travel_service.get_train_schedules(
                    origin_city_id, destination_city_id
                )
                response_msg = (
                    f"Found {len(schedules)} train schedules from "
                    f"{origin_city_id} to {destination_city_id}"
                )
            else:
                schedules = travel_service.get_schedules_from_city(origin_city_id)
                response_msg = (
                    f"Found {len(schedules)} train schedules from " f"{origin_city_id}"
                )

            return cls._create_success_response(
                response_msg,
                schedules=schedules,
                count=len(schedules),
                origin=origin_city_id,
                destination=destination_city_id,
            )

        except Exception as e:
            return cls._handle_error(
                "retrieving train schedules",
                e,
                schedules=[],
                count=0,
                origin=origin_city_id,
                destination=destination_city_id,
            )
