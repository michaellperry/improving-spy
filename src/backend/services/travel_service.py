"""Travel service for managing spy travel state and operations."""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from ..models import TravelState, TravelStateCreate, TravelStateUpdate, CityModel, TrainScheduleModel
from ..core.database import get_db

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
            # For now, we'll return a default state since travel_state isn't stored in DB yet
            # This will be enhanced when we add travel_state to the SpyModel
            logger.debug(f"Getting travel state for spy: {spy_id}")
            
            # Return default state for demonstration
            return TravelState(
                city_id="vienna",
                time_utc=datetime.now(timezone.utc),
                inventory={
                    "passport": "Valid",
                    "tickets": [],
                    "cash": "500 EUR",
                    "equipment": ["disguise", "radio"]
                }
            )
        except Exception as e:
            logger.error(f"Error getting travel state for spy {spy_id}: {str(e)}")
            return None
    
    def update_travel_state(self, spy_id: str, updates: TravelStateUpdate) -> Optional[TravelState]:
        """
        Update travel state for a spy.
        
        Args:
            spy_id: The ID of the spy
            updates: TravelStateUpdate object with fields to update
            
        Returns:
            Updated TravelState object or None if update failed
        """
        try:
            logger.debug(f"Updating travel state for spy {spy_id} with updates: {updates}")
            
            # Get current state
            current_state = self.get_travel_state(spy_id)
            if not current_state:
                logger.warning(f"No existing travel state found for spy {spy_id}")
                return None
            
            # Validate updates before applying
            if not self._validate_state_transition(current_state, updates):
                logger.warning(f"Invalid state transition for spy {spy_id}")
                return None
            
            # Apply updates
            updated_state = self._apply_updates(current_state, updates)
            
            # Validate final state
            if not self._validate_state_consistency(updated_state):
                logger.error(f"State consistency validation failed for spy {spy_id}")
                return None
            
            logger.info(f"Successfully updated travel state for spy {spy_id}")
            return updated_state
            
        except Exception as e:
            logger.error(f"Error updating travel state for spy {spy_id}: {str(e)}")
            return None
    
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
    
    def _validate_state_transition(self, current_state: TravelState, 
                                  updates: TravelStateUpdate) -> bool:
        """
        Validate that the proposed state transition is valid.
        
        Args:
            current_state: Current travel state
            updates: Proposed updates
            
        Returns:
            True if transition is valid, False otherwise
        """
        try:
            # Validate city_id if being updated
            if updates.city_id and updates.city_id != current_state.city_id:
                # Check if the city exists
                city = self.db.query(CityModel).filter(CityModel.id == updates.city_id).first()
                if not city:
                    logger.warning(f"Invalid city_id: {updates.city_id}")
                    return False
            
            # Validate time_utc if being updated
            if updates.time_utc:
                # Ensure time is not in the past (allow small buffer for timezone issues)
                if updates.time_utc < datetime.now(timezone.utc).replace(microsecond=0):
                    logger.warning(f"Time cannot be in the past: {updates.time_utc}")
                    return False
            
            # Validate inventory if being updated
            if updates.inventory:
                # Basic inventory validation
                if not isinstance(updates.inventory, dict):
                    logger.warning("Inventory must be a dictionary")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating state transition: {str(e)}")
            return False
    
    def _validate_state_consistency(self, state: TravelState) -> bool:
        """
        Validate that the final state is internally consistent.
        
        Args:
            state: Travel state to validate
            
        Returns:
            True if state is consistent, False otherwise
        """
        try:
            # Check if city exists
            city = self.db.query(CityModel).filter(CityModel.id == state.city_id).first()
            if not city:
                logger.warning(f"City {state.city_id} does not exist")
                return False
            
            # Check if time is valid
            if state.time_utc.tzinfo is None:
                logger.warning("Time must have timezone information")
                return False
            
            # Check if inventory is valid
            if not isinstance(state.inventory, dict):
                logger.warning("Inventory must be a dictionary")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating state consistency: {str(e)}")
            return False
    
    def _apply_updates(self, current_state: TravelState, 
                       updates: TravelStateUpdate) -> TravelState:
        """
        Apply updates to the current state.
        
        Args:
            current_state: Current travel state
            updates: Updates to apply
            
        Returns:
            Updated travel state
        """
        # Create new state with updates
        new_state_data = current_state.model_dump()
        
        if updates.city_id is not None:
            new_state_data["city_id"] = updates.city_id
        
        if updates.time_utc is not None:
            new_state_data["time_utc"] = updates.time_utc
        
        if updates.inventory is not None:
            # Merge inventory updates
            new_inventory = current_state.inventory.copy()
            new_inventory.update(updates.inventory)
            new_state_data["inventory"] = new_inventory
        
        return TravelState(**new_state_data)
    
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
