"""Transportation network service for managing city and route information."""
import logging
from typing import Dict, Any, List

from sqlalchemy.orm import Session

from ..models import CityModel, TrainScheduleModel

# Set up logging
logger = logging.getLogger(__name__)

class TransportationNetworkService:
    """Service for managing transportation network and city information."""
    
    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db
    
    def get_transportation_map(self) -> Dict[str, Any]:
        """
        Get the complete transportation network graph.
        
        Returns:
            Dict containing cities and route edges with timezone info
        """
        try:
            logger.debug("Getting transportation network map")
            
            cities_data = self._get_cities_data()
            edges_data = self._get_route_edges()
            
            return {
                "cities": cities_data,
                "edges": edges_data
            }
            
        except Exception as e:
            logger.error(f"Error getting transportation map: {str(e)}")
            return {"cities": [], "edges": []}
    
    def get_available_cities(self) -> List[Dict[str, Any]]:
        """
        Get list of available cities for travel.
        
        Returns:
            List of city dictionaries
        """
        try:
            cities = self.db.query(CityModel).all()
            return [
                {
                    "id": city.id,
                    "name": city.name,
                    "country": city.country,
                    "timezone": city.timezone,
                    "coordinates": city.coordinates
                }
                for city in cities
            ]
        except Exception as e:
            logger.error(f"Error getting available cities: {str(e)}")
            return []
    
    def _get_cities_data(self) -> List[Dict[str, Any]]:
        """
        Get formatted cities data for the transportation map.
        
        Returns:
            List of city data dictionaries
        """
        cities = self.db.query(CityModel).all()
        return [
            {
                "id": city.id,
                "tz": city.timezone.replace("+", "").replace(":00", "")
            }
            for city in cities
        ]
    
    def _get_route_edges(self) -> List[Dict[str, Any]]:
        """
        Get route edges with minimum travel times.
        
        Returns:
            List of edge dictionaries
        """
        schedules = self.db.query(TrainScheduleModel).all()
        
        # Build edges with minimum travel time
        edge_map = {}  # Track min time between city pairs
        
        for schedule in schedules:
            key = (schedule.origin_city_id, schedule.destination_city_id)
            duration = self._calculate_duration_minutes(schedule.departure_time, schedule.arrival_time)
            
            # Update minimum time if this route is faster
            if key not in edge_map or duration < edge_map[key]:
                edge_map[key] = duration
        
        # Convert edge map to list format
        edges = []
        for (origin, dest), min_minutes in edge_map.items():
            edges.append({
                "from": origin,
                "to": dest,
                "min_minutes": min_minutes
            })
        
        return edges
    
    def _calculate_duration_minutes(self, departure_time: str, arrival_time: str) -> int:
        """
        Calculate duration in minutes between departure and arrival times.
        
        Args:
            departure_time: Departure time in HH:MM format
            arrival_time: Arrival time in HH:MM format
            
        Returns:
            Duration in minutes
        """
        # Calculate duration in minutes
        dep_hour, dep_min = map(int, departure_time.split(':'))
        arr_hour, arr_min = map(int, arrival_time.split(':'))
        
        dep_minutes = dep_hour * 60 + dep_min
        arr_minutes = arr_hour * 60 + arr_min
        
        # Handle overnight journeys
        if arr_minutes < dep_minutes:
            arr_minutes += 24 * 60
        
        return arr_minutes - dep_minutes
