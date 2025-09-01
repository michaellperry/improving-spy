"""Travel execution service for performing actual travel operations."""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ..models import TrainScheduleModel, TravelStateUpdate
from .travel_state_service import TravelStateService

# Set up logging
logger = logging.getLogger(__name__)

class TravelExecutionService:
    """Service for executing travel operations and updating spy state."""
    
    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db
        self._travel_state_service = TravelStateService(db)
    
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
            logger.info(f"Executing travel on service: {service_id} for spy: {spy_id}")
            
            # Get current travel state
            current_state = self._travel_state_service.get_travel_state(spy_id)
            if not current_state:
                return {
                    "success": False,
                    "error_code": "NO_TRAVEL_STATE",
                    "error_message": f"No travel state found for spy {spy_id}"
                }
            
            # Get service details
            schedule = self._get_service_schedule(service_id)
            if not schedule:
                return {
                    "success": False,
                    "error_code": "INVALID_SERVICE",
                    "error_message": f"Service {service_id} not found"
                }
            
            # Validate travel conditions
            validation_result = self._validate_travel_conditions(current_state, schedule)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error_code": validation_result["error_code"],
                    "error_message": validation_result["error_message"]
                }
            
            # Calculate travel details
            departure_time = self._parse_schedule_time(schedule.departure_time, current_state.time_utc)
            arrival_time = self._parse_schedule_time(schedule.arrival_time, departure_time)
            duration_minutes = int((arrival_time - departure_time).total_seconds() / 60)
            
            # Update spy's travel state
            updated_state = self._update_spy_state(spy_id, schedule, arrival_time)
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
    
    def _get_service_schedule(self, service_id: str) -> Optional[TrainScheduleModel]:
        """
        Get service schedule by service ID.
        
        Args:
            service_id: Service identifier
            
        Returns:
            TrainScheduleModel or None if not found
        """
        return self.db.query(TrainScheduleModel).filter(
            TrainScheduleModel.service_id == service_id
        ).first()
    
    def _validate_travel_conditions(self, current_state, schedule: TrainScheduleModel) -> Dict[str, Any]:
        """
        Validate travel conditions before execution.
        
        Args:
            current_state: Current spy travel state
            schedule: Train schedule to validate
            
        Returns:
            Validation result dictionary
        """
        # Check if spy is in the origin city
        if current_state.city_id != schedule.origin_city_id:
            return {
                "valid": False,
                "error_code": "WRONG_LOCATION",
                "error_message": f"Spy is in {current_state.city_id}, but service {schedule.service_id} departs from {schedule.origin_city_id}"
            }
        
        # Parse schedule times using spy's current time as base
        departure_time = self._parse_schedule_time(schedule.departure_time, current_state.time_utc)
        
        # Check if departure time has passed in the spy's timeline
        if current_state.time_utc > departure_time + timedelta(minutes=5):  # 5 minute grace period
            return {
                "valid": False,
                "error_code": "MISSED_DEPARTURE",
                "error_message": f"Departure time {schedule.departure_time} has passed in the spy's timeline"
            }
        
        # Check for connection issues
        connection_check = self._check_connection_issues(schedule, current_state.time_utc)
        if not connection_check["valid"]:
            return {
                "valid": False,
                "error_code": "CONNECTION_ISSUE",
                "error_message": connection_check["message"]
            }
        
        return {"valid": True}
    
    def _update_spy_state(self, spy_id: str, schedule: TrainScheduleModel, arrival_time: datetime) -> Optional[Any]:
        """
        Update spy's travel state after travel execution.
        
        Args:
            spy_id: The ID of the spy
            schedule: Train schedule used for travel
            arrival_time: Calculated arrival time
            
        Returns:
            Updated travel state or None if update failed
        """
        try:
            # Get current state to preserve existing inventory
            current_state = self._travel_state_service.get_travel_state(spy_id)
            if not current_state:
                return None
            
            # Update inventory with new ticket
            updated_inventory = current_state.inventory.copy()
            updated_inventory["tickets"] = [f"Service {schedule.service_id}"]
            
            # Create update
            state_update = TravelStateUpdate(
                city_id=schedule.destination_city_id,
                time_utc=arrival_time,
                inventory=updated_inventory
            )
            
            return self._travel_state_service.update_travel_state(spy_id, state_update)
            
        except Exception as e:
            logger.error(f"Error updating spy state: {str(e)}")
            return None
    
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
