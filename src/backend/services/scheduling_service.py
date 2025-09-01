"""Scheduling service for managing train schedules and route planning."""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ..models import TrainScheduleModel
from .travel_state_service import TravelStateService
from .route_finder_service import RouteFinderService
from .schedule_utils_service import ScheduleUtilsService

# Set up logging
logger = logging.getLogger(__name__)

class SchedulingService:
    """Service for managing train schedules and route planning."""
    
    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db
        self._travel_state_service = TravelStateService(db)
        self._route_finder_service = RouteFinderService(db)
        self._utils_service = ScheduleUtilsService(db)
    
    def get_available_services(self, origin_id: str, date_range: str, 
                             destination_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available train services between cities."""
        return self._utils_service.get_available_services(origin_id, date_range, destination_id)
    
    def get_train_schedules(self, origin_city_id: str, destination_city_id: str) -> List[Dict[str, Any]]:
        """Get train schedules between two cities."""
        return self._utils_service.get_train_schedules(origin_city_id, destination_city_id)
    
    def get_schedules_from_city(self, origin_city_id: str) -> List[Dict[str, Any]]:
        """Get all train schedules from a specific city."""
        return self._utils_service.get_schedules_from_city(origin_city_id)
    
    def plan_route(self, spy_id: str, origin_id: str, dest_id: str, 
                  prefs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate guaranteed valid travel itineraries.
        
        Args:
            spy_id: The ID of the spy planning the route
            origin_id: Starting city
            dest_id: Destination city
            prefs: Travel preferences including min_transfer time
            
        Returns:
            Dict containing planned route itinerary
        """
        try:
            logger.info(f"Planning route from {origin_id} to {dest_id} for spy {spy_id}")
            
            # Get spy's current travel state
            current_state = self._travel_state_service.get_travel_state(spy_id)
            if not current_state:
                return {
                    "success": False,
                    "error_message": f"No travel state found for spy {spy_id}"
                }
            
            # Check if spy is in the origin city
            if current_state.city_id != origin_id:
                return {
                    "success": False,
                    "error_message": f"Spy is currently in {current_state.city_id}, not in {origin_id}"
                }
            
            min_transfer = prefs.get("min_transfer", 10)  # Default 10 minute transfer time
            depart_after = current_state.time_utc
            
            # Get all available routes
            all_routes = self._route_finder_service.find_all_routes(origin_id, dest_id, depart_after, min_transfer)
            
            if not all_routes:
                return {
                    "success": False,
                    "error_message": f"No valid route found from {origin_id} to {dest_id} departing after {depart_after.strftime('%H:%M')}"
                }
            
            # Select best route (shortest total time for now)
            best_route = min(all_routes, key=lambda r: r["total_duration"])
            
            return {
                "success": True,
                "itinerary": best_route["legs"],
                "total_duration": best_route["total_duration"],
                "departure_time": best_route["departure_time"].isoformat(),
                "arrival_time": best_route["arrival_time"].isoformat(),
                "spy_current_time": current_state.time_utc.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error planning route: {str(e)}")
            return {
                "success": False,
                "error_message": f"Error planning route: {str(e)}"
            }
    
    def plan_journey(self, origin_city_id: str, destination_city_id: str, 
                    departure_date: datetime) -> Dict[str, Any]:
        """
        Plan a journey between two cities.
        
        Args:
            origin_city_id: ID of the origin city
            destination_city_id: ID of the destination city
            departure_date: Date of departure
            
        Returns:
            Journey plan dictionary
        """
        try:
            logger.info(f"Planning journey from {origin_city_id} to {destination_city_id}")
            
            # Get available schedules
            schedules = self.get_train_schedules(origin_city_id, destination_city_id)
            
            if not schedules:
                return {
                    "success": False,
                    "message": f"No direct train service available from {origin_city_id} to {destination_city_id}",
                    "journey_plan": None
                }
            
            # For now, return the first available schedule
            # This could be enhanced with more sophisticated routing logic
            selected_schedule = schedules[0]
            
            journey_plan = {
                "origin": origin_city_id,
                "destination": destination_city_id,
                "departure_date": departure_date.isoformat(),
                "train_service": selected_schedule["service_id"],
                "departure_time": selected_schedule["departure_time"],
                "arrival_time": selected_schedule["arrival_time"],
                "estimated_duration": self._utils_service._calculate_duration(
                    selected_schedule["departure_time"],
                    selected_schedule["arrival_time"]
                )
            }
            
            return {
                "success": True,
                "message": "Journey planned successfully",
                "journey_plan": journey_plan
            }
        
        except Exception as e:
            logger.error(f"Error planning journey: {str(e)}")
            return {
                "success": False,
                "message": f"Error planning journey: {str(e)}",
                "journey_plan": None
            }

def _parse_schedule_time(self, time_str: str, base_time: datetime) -> datetime:
    """
    Parse schedule time string and convert to datetime.
    
    Args:
        time_str: Time string in "HH:MM" format
        base_time: Base datetime to use for date
        
    Returns:
        Parsed datetime
    """
    hour, minute = map(int, time_str.split(':'))
    return base_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
