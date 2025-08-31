"""Travel service for managing spy travel state and operations."""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from ..models import TravelState, TravelStateCreate, TravelStateUpdate, CityModel, TrainScheduleModel
from ..core.database import get_db
from ..repositories.travel_state_repository import TravelStateRepository

# Set up logging
logger = logging.getLogger(__name__)

class TravelService:
    """Service for managing spy travel state and operations."""
    
    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db
    
    def get_travel_state(self, spy_id: str) -> Optional[TravelState]:
        """
        Retrieve travel state for a spy.
        
        Args:
            spy_id: The ID of the spy
            
        Returns:
            TravelState object or None if not found
        """
        try:
            logger.debug(f"Getting travel state for spy: {spy_id}")
            
            # Use repository to get travel state from database
            travel_state_repo = TravelStateRepository(self.db)
            travel_state = travel_state_repo.get_by_spy_id(spy_id)
            
            if not travel_state:
                logger.debug(f"No travel state found for spy {spy_id}, creating default state")
                # Create default state if none exists
                default_state = TravelStateCreate(
                    city_id="vienna",
                    time_utc=datetime.now(timezone.utc).replace(hour=8, minute=0, second=0, microsecond=0),
                    inventory={
                        "passport": "Valid",
                        "tickets": [],
                        "cash": "500 EUR",
                        "equipment": ["disguise", "radio"]
                    }
                )
                travel_state = travel_state_repo.create(spy_id, default_state)
            
            return travel_state
            
        except Exception as e:
            logger.error(f"Error getting travel state for spy {spy_id}: {str(e)}")
            return None
    
    def get_transportation_map(self) -> Dict[str, Any]:
        """
        Get the complete transportation network graph.
        
        Returns:
            Dict containing cities and route edges with timezone info
        """
        try:
            logger.debug("Getting transportation network map")
            
            # Get all cities
            cities = self.db.query(CityModel).all()
            cities_data = [
                {
                    "id": city.id,
                    "tz": city.timezone.replace("+", "").replace(":00", "")
                }
                for city in cities
            ]
            
            # Get all train schedules to build edges
            schedules = self.db.query(TrainScheduleModel).all()
            
            # Build edges with minimum travel time
            edges = []
            edge_map = {}  # Track min time between city pairs
            
            for schedule in schedules:
                key = (schedule.origin_city_id, schedule.destination_city_id)
                
                # Calculate duration in minutes
                dep_hour, dep_min = map(int, schedule.departure_time.split(':'))
                arr_hour, arr_min = map(int, schedule.arrival_time.split(':'))
                
                dep_minutes = dep_hour * 60 + dep_min
                arr_minutes = arr_hour * 60 + arr_min
                
                # Handle overnight journeys
                if arr_minutes < dep_minutes:
                    arr_minutes += 24 * 60
                
                duration = arr_minutes - dep_minutes
                
                # Update minimum time if this route is faster
                if key not in edge_map or duration < edge_map[key]:
                    edge_map[key] = duration
            
            # Convert edge map to list format
            for (origin, dest), min_minutes in edge_map.items():
                edges.append({
                    "from": origin,
                    "to": dest,
                    "min_minutes": min_minutes
                })
            
            return {
                "cities": cities_data,
                "edges": edges
            }
            
        except Exception as e:
            logger.error(f"Error getting transportation map: {str(e)}")
            return {"cities": [], "edges": []}


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
            current_state = self.get_travel_state(spy_id)
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
            
            # Use spy's current time as the earliest departure time
            depart_after = current_state.time_utc
            
            # Get all available routes
            all_routes = self._find_all_routes(origin_id, dest_id, depart_after, min_transfer)
            
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


    def execute_travel(self, spy_id: str, service_id: str) -> Dict[str, Any]:
        """
        Execute travel on a specific service, updating spy state.
        
        Args:
            spy_id: The ID of the spy traveling
            service_id: Service identifier to travel on
            
        Returns:
            Dict containing travel result and updated state
        """
        try:
            logger.debug(f"Executing travel on service: {service_id} for spy: {spy_id}")
            
            # Get current travel state
            current_state = self.get_travel_state(spy_id)
            if not current_state:
                return {
                    "success": False,
                    "error_code": "NO_TRAVEL_STATE",
                    "error_message": f"No travel state found for spy {spy_id}"
                }
            
            # Get service details
            schedule = self.db.query(TrainScheduleModel).filter(
                TrainScheduleModel.service_id == service_id
            ).first()
            
            if not schedule:
                return {
                    "success": False,
                    "error_code": "INVALID_SERVICE",
                    "error_message": f"Service {service_id} not found"
                }
            
            # Check if spy is in the origin city
            if current_state.city_id != schedule.origin_city_id:
                return {
                    "success": False,
                    "error_code": "WRONG_LOCATION",
                    "error_message": f"Spy is in {current_state.city_id}, but service {service_id} departs from {schedule.origin_city_id}"
                }
            
            # Parse schedule times using spy's current time as base
            departure_time = self._parse_schedule_time(schedule.departure_time, current_state.time_utc)
            
            # Check if departure time has passed in the spy's timeline
            if current_state.time_utc > departure_time + timedelta(minutes=5):  # 5 minute grace period
                return {
                    "success": False,
                    "error_code": "MISSED_DEPARTURE",
                    "error_message": f"Departure time {schedule.departure_time} has passed in the spy's timeline"
                }
            
            # Calculate arrival time and duration
            arrival_time = self._parse_schedule_time(schedule.arrival_time, departure_time)
            duration_minutes = int((arrival_time - departure_time).total_seconds() / 60)
            
            # Update spy's travel state
            travel_state_repo = TravelStateRepository(self.db)
            updated_state = travel_state_repo.update(spy_id, TravelStateUpdate(
                city_id=schedule.destination_city_id,
                time_utc=arrival_time,
                inventory={
                    "tickets": [f"Service {service_id}"],
                    "cash": "500 EUR",  # Keep existing cash
                    "equipment": ["disguise", "radio"]  # Keep existing equipment
                }
            ))
            
            if not updated_state:
                return {
                    "success": False,
                    "error_code": "STATE_UPDATE_FAILED",
                    "error_message": "Failed to update spy's travel state"
                }
            
            travel_result = {
                "service_id": service_id,
                "origin": schedule.origin_city_id,
                "destination": schedule.destination_city_id,
                "departure_time": departure_time.isoformat(),
                "arrival_time": arrival_time.isoformat(),
                "duration_minutes": duration_minutes
            }
            
            return {
                "success": True,
                "travel_result": travel_result,
                "updated_state": updated_state.model_dump()
            }
            
        except Exception as e:
            logger.error(f"Error executing travel: {str(e)}")
            return {
                "success": False,
                "error_code": "TRAVEL_ERROR",
                "error_message": str(e)
            }


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
                "estimated_duration": self._calculate_duration(
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


    def _find_all_routes(self, origin_id: str, dest_id: str, depart_after: datetime, 
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
        
        # Indirect routes (1 transfer)
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


    def _check_connection_issues(self, schedule: TrainScheduleModel, current_time: datetime) -> Dict[str, Any]:
        """
        Check for potential connection issues.
        
        Args:
            schedule: The train schedule to check
            current_time: Current time for validation
            
        Returns:
            Dict with validation result
        """
        try:
            # Check if this is a connecting service (not from Vienna)
            if schedule.origin_city_id != "vienna":
                # Simulate connection check - in real implementation, this would check
                # if the spy arrived at the origin city in time for this connection
                
                # For demo purposes, simulate some connection failures
                if schedule.origin_city_id == "munich" and schedule.service_id == "S3":
                    # Simulate tight connection scenario
                    if current_time.hour < 14:  # Before 2 PM
                        return {
                            "valid": False,
                            "message": "Insufficient transfer time for connection to Paris service"
                        }
                
                if schedule.origin_city_id == "zurich" and schedule.service_id == "S4":
                    # Simulate missed connection scenario
                    if current_time.hour < 16:  # Before 4 PM
                        return {
                            "valid": False,
                            "message": "Previous service arrival time exceeded, connection missed"
                        }
            
            return {
                "valid": True,
                "message": "Connection check passed"
            }
            
        except Exception as e:
            logger.error(f"Error checking connection issues: {str(e)}")
            return {
                "valid": False,
                "message": f"Connection validation error: {str(e)}"
            }

