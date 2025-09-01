"""Schedule utilities service for helper methods related to train schedules."""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from ..models import TrainScheduleModel

# Set up logging
logger = logging.getLogger(__name__)

class ScheduleUtilsService:
    """Service for schedule-related utility methods."""
    
    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db
    
    def get_available_services(self, origin_id: str, date_range: str, 
                             destination_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get available train services between cities.
        
        Args:
            origin_id: Starting city identifier
            date_range: Time window for search
            destination_id: Optional target city filter
            
        Returns:
            List of available train services
        """
        try:
            logger.debug(f"Getting available services from {origin_id} to {destination_id or 'any destination'}")
            
            # Build query
            query = self.db.query(TrainScheduleModel).filter(
                TrainScheduleModel.origin_city_id == origin_id
            )
            
            if destination_id:
                query = query.filter(TrainScheduleModel.destination_city_id == destination_id)
            
            schedules = query.all()
            
            # Convert to service format
            services = []
            for schedule in schedules:
                services.append({
                    "id": schedule.service_id,
                    "origin": schedule.origin_city_id,
                    "destination": schedule.destination_city_id,
                    "dep_local": schedule.departure_time,
                    "arr_local": schedule.arrival_time,
                    "operator": self._get_operator_for_service(schedule.service_id)
                })
            
            return services
            
        except Exception as e:
            logger.error(f"Error getting available services: {str(e)}")
            return []
    
    def get_train_schedules(self, origin_city_id: str, destination_city_id: str) -> List[Dict[str, Any]]:
        """
        Get train schedules between two cities.
        
        Args:
            origin_city_id: ID of the origin city
            destination_city_id: ID of the destination city
            
        Returns:
            List of train schedule dictionaries
        """
        try:
            schedules = self.db.query(TrainScheduleModel).filter(
                TrainScheduleModel.origin_city_id == origin_city_id,
                TrainScheduleModel.destination_city_id == destination_city_id
            ).all()
            
            return [
                {
                    "id": schedule.id,
                    "service_id": schedule.service_id,
                    "origin_city_id": schedule.origin_city_id,
                    "destination_city_id": schedule.destination_city_id,
                    "departure_time": schedule.departure_time,
                    "arrival_time": schedule.arrival_time,
                    "days_of_week": schedule.days_of_week
                }
                for schedule in schedules
            ]
        except Exception as e:
            logger.error(f"Error getting train schedules: {str(e)}")
            return []
    
    def get_schedules_from_city(self, origin_city_id: str) -> List[Dict[str, Any]]:
        """
        Get all train schedules from a specific city.
        
        Args:
            origin_city_id: ID of the origin city
            
        Returns:
            List of train schedule dictionaries
        """
        try:
            schedules = self.db.query(TrainScheduleModel).filter(
                TrainScheduleModel.origin_city_id == origin_city_id
            ).all()
            
            return [
                {
                    "id": schedule.id,
                    "service_id": schedule.service_id,
                    "origin_city_id": schedule.origin_city_id,
                    "destination_city_id": schedule.destination_city_id,
                    "departure_time": schedule.departure_time,
                    "arrival_time": schedule.arrival_time,
                    "days_of_week": schedule.days_of_week
                }
                for schedule in schedules
            ]
        except Exception as e:
            logger.error(f"Error getting schedules from city: {str(e)}")
            return []
    
    def _get_operator_for_service(self, service_id: str) -> str:
        """
        Get operator name for a service ID.
        
        Args:
            service_id: Service identifier
            
        Returns:
            Operator name
        """
        # Simple mapping based on service ID prefix
        if service_id.startswith('S'):
            return "ÖBB"  # Austrian Railways
        elif service_id.startswith('ICE'):
            return "DB"   # German Railways
        elif service_id.startswith('TGV'):
            return "SNCF" # French Railways
        else:
            return "Unknown"
    
    def _calculate_duration(self, departure_time: str, arrival_time: str) -> str:
        """
        Calculate journey duration from departure and arrival times.
        
        Args:
            departure_time: Departure time in HH:MM format
            arrival_time: Arrival time in HH:MM format
            
        Returns:
            Duration string in human-readable format
        """
        try:
            # Parse times (assuming same day for simplicity)
            dep_hour, dep_min = map(int, departure_time.split(':'))
            arr_hour, arr_min = map(int, arrival_time.split(':'))
            
            # Calculate duration in minutes
            dep_minutes = dep_hour * 60 + dep_min
            arr_minutes = arr_hour * 60 + arr_min
            
            # Handle overnight journeys
            if arr_minutes < dep_minutes:
                arr_minutes += 24 * 60
            
            duration_minutes = arr_minutes - dep_minutes
            
            # Convert to hours and minutes
            hours = duration_minutes // 60
            minutes = duration_minutes % 60
            
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
                
        except Exception as e:
            logger.error(f"Error calculating duration: {str(e)}")
            return "Unknown"
