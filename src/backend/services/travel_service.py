"""Travel service orchestrator for managing spy travel operations."""
import logging
from typing import Dict, Any, Optional, List

from sqlalchemy.orm import Session

from .travel_state_service import TravelStateService
from .transportation_network_service import TransportationNetworkService
from .scheduling_service import SchedulingService
from .travel_execution_service import TravelExecutionService
from ..repositories.travel_state_repository import TravelStateRepository

# Set up logging
logger = logging.getLogger(__name__)

class TravelService:
    """Orchestrator service for managing spy travel operations."""
    
    def __init__(self, db: Session):
        """Initialize with database session and specialized services."""
        self.db = db
        self._state_service = TravelStateService(db)
        self._network_service = TransportationNetworkService(db)
        self._scheduling_service = SchedulingService(db)
        self._execution_service = TravelExecutionService(db)
    
    # Travel State Management
    def get_travel_state(self, spy_id: str):
        """Get travel state for a spy."""
        return self._state_service.get_travel_state(spy_id)
    
    def update_travel_state(self, spy_id: str, updates):
        """Update travel state for a spy."""
        return self._state_service.update_travel_state(spy_id, updates)
    
    # Transportation Network
    def get_transportation_map(self) -> Dict[str, Any]:
        """Get the complete transportation network graph."""
        return self._network_service.get_transportation_map()
    
    def get_available_cities(self) -> List[Dict[str, Any]]:
        """Get list of available cities for travel."""
        return self._network_service.get_available_cities()
    
    # Scheduling and Route Planning
    def get_available_services(self, origin_id: str, date_range: str, 
                             destination_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available train services between cities."""
        return self._scheduling_service.get_available_services(origin_id, date_range, destination_id)
    
    def get_train_schedules(self, origin_city_id: str, destination_city_id: str) -> List[Dict[str, Any]]:
        """Get train schedules between two cities."""
        return self._scheduling_service.get_train_schedules(origin_city_id, destination_city_id)
    
    def get_schedules_from_city(self, origin_city_id: str) -> List[Dict[str, Any]]:
        """Get all train schedules from a specific city."""
        return self._scheduling_service.get_schedules_from_city(origin_city_id)
    
    def plan_route(self, spy_id: str, origin_id: str, dest_id: str, 
                  prefs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate guaranteed valid travel itineraries."""
        return self._scheduling_service.plan_route(spy_id, origin_id, dest_id, prefs)
    
    def plan_journey(self, origin_city_id: str, destination_city_id: str, 
                    departure_date) -> Dict[str, Any]:
        """Plan a journey between two cities."""
        return self._scheduling_service.plan_journey(origin_city_id, destination_city_id, departure_date)
    
    # Travel Execution
    def execute_travel(self, spy_id: str, service_id: str) -> Dict[str, Any]:
        """Execute travel on a specific service, updating spy state."""
        return self._execution_service.execute_travel(spy_id, service_id)
    
    # Utility Methods
    def _calculate_duration(self, departure_time: str, arrival_time: str) -> str:
        """Calculate duration between two time strings."""
        try:
            # Parse time strings
            dep_hour, dep_minute = map(int, departure_time.split(':'))
            arr_hour, arr_minute = map(int, arrival_time.split(':'))
            
            # Convert to minutes
            dep_minutes = dep_hour * 60 + dep_minute
            arr_minutes = arr_hour * 60 + arr_minute
            
            # Handle overnight journeys
            if arr_minutes < dep_minutes:
                arr_minutes += 24 * 60  # Add 24 hours
            
            # Calculate difference
            duration_minutes = arr_minutes - dep_minutes
            
            # Format as hours and minutes
            hours = duration_minutes // 60
            minutes = duration_minutes % 60
            
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
                
        except (ValueError, AttributeError):
            return "Unknown"

