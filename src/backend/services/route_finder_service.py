"""Route finder service for discovering travel routes between cities."""
import logging
from typing import Dict, Any, List
from datetime import datetime

from sqlalchemy.orm import Session

from ..models import TrainScheduleModel

# Set up logging
logger = logging.getLogger(__name__)

class RouteFinderService:
    """Service for finding travel routes between cities."""
    
    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db
    
    def find_all_routes(self, origin_id: str, dest_id: str, depart_after: datetime, 
                       min_transfer: int) -> List[Dict[str, Any]]:
        """
        Find all possible routes between two cities.
        
        Args:
            origin_id: Starting city
            dest_id: Destination city
            depart_after: Earliest departure time
            min_transfer: Minimum transfer time in minutes
            
        Returns:
            List of possible routes
        """
        routes = []
        
        # Direct routes
        routes.extend(self._find_direct_routes(origin_id, dest_id, depart_after))
        
        # Indirect routes (1 transfer)
        routes.extend(self._find_indirect_routes(origin_id, dest_id, depart_after, min_transfer))
        
        return routes
    
    def _find_direct_routes(self, origin_id: str, dest_id: str, depart_after: datetime) -> List[Dict[str, Any]]:
        """
        Find direct routes between two cities.
        
        Args:
            origin_id: Starting city
            dest_id: Destination city
            depart_after: Earliest departure time
            
        Returns:
            List of direct routes
        """
        routes = []
        
        direct_schedules = self.db.query(TrainScheduleModel).filter(
            TrainScheduleModel.origin_city_id == origin_id,
            TrainScheduleModel.destination_city_id == dest_id
        ).all()
        
        for schedule in direct_schedules:
            departure_time = self._parse_schedule_time(schedule.departure_time, depart_after)
            if departure_time >= depart_after:
                arrival_time = self._parse_schedule_time(schedule.arrival_time, departure_time)
                duration = int((arrival_time - departure_time).total_seconds() / 60)
                
                routes.append({
                    "legs": [{
                        "service_id": schedule.service_id,
                        "origin": schedule.origin_city_id,
                        "destination": schedule.destination_city_id,
                        "departure_time": departure_time,
                        "arrival_time": arrival_time,
                        "duration": duration
                    }],
                    "total_duration": duration,
                    "departure_time": departure_time,
                    "arrival_time": arrival_time
                })
        
        return routes
    
    def _find_indirect_routes(self, origin_id: str, dest_id: str, depart_after: datetime, 
                            min_transfer: int) -> List[Dict[str, Any]]:
        """
        Find indirect routes with one transfer.
        
        Args:
            origin_id: Starting city
            dest_id: Destination city
            depart_after: Earliest departure time
            min_transfer: Minimum transfer time in minutes
            
        Returns:
            List of indirect routes
        """
        routes = []
        
        # Get all cities that can be reached from origin
        intermediate_cities = self.db.query(TrainScheduleModel.destination_city_id).filter(
            TrainScheduleModel.origin_city_id == origin_id
        ).distinct().all()
        
        for intermediate in intermediate_cities:
            intermediate_id = intermediate[0]
            if intermediate_id == dest_id:
                continue
                
            # Find first leg
            first_legs = self.db.query(TrainScheduleModel).filter(
                TrainScheduleModel.origin_city_id == origin_id,
                TrainScheduleModel.destination_city_id == intermediate_id
            ).all()
            
            # Find second leg
            second_legs = self.db.query(TrainScheduleModel).filter(
                TrainScheduleModel.origin_city_id == intermediate_id,
                TrainScheduleModel.destination_city_id == dest_id
            ).all()
            
            # Try all combinations
            for first in first_legs:
                first_departure = self._parse_schedule_time(first.departure_time, depart_after)
                if first_departure < depart_after:
                    continue
                    
                first_arrival = self._parse_schedule_time(first.arrival_time, first_departure)
                
                for second in second_legs:
                    second_departure = self._parse_schedule_time(second.departure_time, first_arrival)
                    
                    # Check transfer time
                    transfer_time = int((second_departure - first_arrival).total_seconds() / 60)
                    if transfer_time < min_transfer:
                        continue
                    
                    second_arrival = self._parse_schedule_time(second.arrival_time, second_departure)
                    total_duration = int((second_arrival - first_departure).total_seconds() / 60)
                    
                    routes.append({
                        "legs": [
                            {
                                "service_id": first.service_id,
                                "origin": first.origin_city_id,
                                "destination": first.destination_city_id,
                                "departure_time": first_departure,
                                "arrival_time": first_arrival,
                                "duration": int((first_arrival - first_departure).total_seconds() / 60)
                            },
                            {
                                "service_id": second.service_id,
                                "origin": second.origin_city_id,
                                "destination": second.destination_city_id,
                                "departure_time": second_departure,
                                "arrival_time": second_arrival,
                                "duration": int((second_arrival - second_departure).total_seconds() / 60)
                            }
                        ],
                        "total_duration": total_duration,
                        "departure_time": first_departure,
                        "arrival_time": second_arrival
                    })
        
        return routes
    
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
