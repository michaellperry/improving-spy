"""Travel tools for AI agent operations."""
import logging
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

from ..services.travel_service import TravelService
from ..core.database import get_db

# Set up logging
logger = logging.getLogger(__name__)

# Tool Request/Response Models
class GetTravelStateRequest(BaseModel):
    """Request model for getting travel state."""
    spy_id: str = Field(..., description="The ID of the spy to get travel state for")

class UpdateTravelStateRequest(BaseModel):
    """Request model for updating travel state."""
    spy_id: str = Field(..., description="The ID of the spy to update")
    city_id: str = Field(None, description="New city ID to travel to")
    time_utc: datetime = Field(None, description="New time in UTC")
    inventory_updates: Dict[str, Any] = Field(None, description="Inventory updates to apply")

class GetCitiesRequest(BaseModel):
    """Request model for getting available cities."""
    pass

class GetTrainSchedulesRequest(BaseModel):
    """Request model for getting train schedules."""
    origin_city_id: str = Field(..., description="ID of the origin city")
    destination_city_id: str = Field(..., description="ID of the destination city")

class PlanJourneyRequest(BaseModel):
    """Request model for planning a journey."""
    origin_city_id: str = Field(..., description="ID of the origin city")
    destination_city_id: str = Field(..., description="ID of the destination city")
    departure_date: datetime = Field(..., description="Date of departure")

class TravelTools:
    """Tools for travel operations."""
    
    @classmethod
    def get_travel_state(cls, spy_id: str) -> Dict[str, Any]:
        """
        Retrieve current travel state for a spy.
        
        Args:
            spy_id: The ID of the spy
            
        Returns:
            Dict containing travel state information
        """
        logger.debug(f"Getting travel state for spy: {spy_id}")
        
        try:
            # Get database session
            db = next(get_db())
            travel_service = TravelService(db)
            
            # Get travel state
            travel_state = travel_service.get_travel_state(spy_id)
            
            if not travel_state:
                return {
                    "response": f"No travel state found for spy {spy_id}",
                    "spy_id": spy_id,
                    "travel_state": None,
                    "tool_calls": []
                }
            
            # Convert to dict for response
            state_dict = travel_state.model_dump()
            
            return {
                "response": f"Current travel state for spy {spy_id}",
                "spy_id": spy_id,
                "travel_state": state_dict,
                "tool_calls": []
            }
            
        except Exception as e:
            error_msg = f"Error getting travel state: {str(e)}"
            logger.error(f"{error_msg} - {type(e).__name__}: {str(e)}")
            return {
                "response": f"Error retrieving travel state: {str(e)}",
                "spy_id": spy_id,
                "travel_state": None,
                "tool_calls": []
            }
    
    @classmethod
    def update_travel_state(cls, spy_id: str, city_id: str = None, 
                           time_utc: datetime = None, 
                           inventory_updates: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Update travel state for a spy.
        
        Args:
            spy_id: The ID of the spy to update
            city_id: New city ID to travel to
            time_utc: New time in UTC
            inventory_updates: Inventory updates to apply
            
        Returns:
            Dict containing update result
        """
        logger.debug(f"Updating travel state for spy {spy_id}")
        
        try:
            # Get database session
            db = next(get_db())
            travel_service = TravelService(db)
            
            # Create update object
            from ..models import TravelStateUpdate
            updates = TravelStateUpdate(
                city_id=city_id,
                time_utc=time_utc,
                inventory=inventory_updates
            )
            
            # Update travel state
            updated_state = travel_service.update_travel_state(spy_id, updates)
            
            if not updated_state:
                return {
                    "response": f"Failed to update travel state for spy {spy_id}",
                    "spy_id": spy_id,
                    "success": False,
                    "tool_calls": []
                }
            
            # Convert to dict for response
            state_dict = updated_state.model_dump()
            
            return {
                "response": f"Successfully updated travel state for spy {spy_id}",
                "spy_id": spy_id,
                "success": True,
                "travel_state": state_dict,
                "tool_calls": []
            }
            
        except Exception as e:
            error_msg = f"Error updating travel state: {str(e)}"
            logger.error(f"{error_msg} - {type(e).__name__}: {str(e)}")
            return {
                "response": f"Error updating travel state: {str(e)}",
                "spy_id": spy_id,
                "success": False,
                "tool_calls": []
            }
    
    @classmethod
    def get_available_cities(cls) -> Dict[str, Any]:
        """
        Get list of available cities for travel.
        
        Returns:
            Dict containing list of available cities
        """
        logger.debug("Getting available cities")
        
        try:
            # Get database session
            db = next(get_db())
            travel_service = TravelService(db)
            
            # Get cities
            cities = travel_service.get_available_cities()
            
            return {
                "response": f"Found {len(cities)} available cities",
                "cities": cities,
                "count": len(cities),
                "tool_calls": []
            }
            
        except Exception as e:
            error_msg = f"Error getting available cities: {str(e)}"
            logger.error(f"{error_msg} - {type(e).__name__}: {str(e)}")
            return {
                "response": f"Error retrieving cities: {str(e)}",
                "cities": [],
                "count": 0,
                "tool_calls": []
            }
    
    @classmethod
    def get_train_schedules(cls, origin_city_id: str, destination_city_id: str) -> Dict[str, Any]:
        """
        Get train schedules between two cities.
        
        Args:
            origin_city_id: ID of the origin city
            destination_city_id: ID of the destination city
            
        Returns:
            Dict containing train schedules
        """
        logger.debug(f"Getting train schedules from {origin_city_id} to {destination_city_id}")
        
        try:
            # Get database session
            db = next(get_db())
            travel_service = TravelService(db)
            
            # Get schedules
            schedules = travel_service.get_train_schedules(origin_city_id, destination_city_id)
            
            return {
                "response": f"Found {len(schedules)} train schedules from {origin_city_id} to {destination_city_id}",
                "schedules": schedules,
                "count": len(schedules),
                "origin": origin_city_id,
                "destination": destination_city_id,
                "tool_calls": []
            }
            
        except Exception as e:
            error_msg = f"Error getting train schedules: {str(e)}"
            logger.error(f"{error_msg} - {type(e).__name__}: {str(e)}")
            return {
                "response": f"Error retrieving train schedules: {str(e)}",
                "schedules": [],
                "count": 0,
                "origin": origin_city_id,
                "destination": destination_city_id,
                "tool_calls": []
            }
    
    @classmethod
    def plan_journey(cls, origin_city_id: str, destination_city_id: str, 
                     departure_date: datetime) -> Dict[str, Any]:
        """
        Plan a journey between two cities.
        
        Args:
            origin_city_id: ID of the origin city
            destination_city_id: ID of the destination city
            departure_date: Date of departure
            
        Returns:
            Dict containing journey plan
        """
        logger.debug(f"Planning journey from {origin_city_id} to {destination_city_id}")
        
        try:
            # Get database session
            db = next(get_db())
            travel_service = TravelService(db)
            
            # Plan journey
            result = travel_service.plan_journey(origin_city_id, destination_city_id, departure_date)
            
            return {
                "response": result["message"],
                "success": result["success"],
                "journey_plan": result["journey_plan"],
                "origin": origin_city_id,
                "destination": destination_city_id,
                "departure_date": departure_date.isoformat(),
                "tool_calls": []
            }
            
        except Exception as e:
            error_msg = f"Error planning journey: {str(e)}"
            logger.error(f"{error_msg} - {type(e).__name__}: {str(e)}")
            return {
                "response": f"Error planning journey: {str(e)}",
                "success": False,
                "journey_plan": None,
                "origin": origin_city_id,
                "destination": destination_city_id,
                "departure_date": departure_date.isoformat(),
                "tool_calls": []
            }
    
    @classmethod
    def get_tools(cls):
        """Return the list of tools for the agent to use."""
        return [
            {
                "name": "get_travel_state",
                "description": "Get the current travel state for a spy, including their location, time, and inventory. Use this when the user asks about a spy's current location or travel status.",
                "function": cls.get_travel_state,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "spy_id": {
                            "type": "string",
                            "description": "ID of the spy to get travel state for"
                        }
                    },
                    "required": ["spy_id"]
                }
            },
            {
                "name": "update_travel_state",
                "description": "Update a spy's travel state, including changing their location, updating time, or modifying their inventory. Use this when the user wants to move a spy to a new city or update their travel information.",
                "function": cls.update_travel_state,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "spy_id": {
                            "type": "string",
                            "description": "ID of the spy to update"
                        },
                        "city_id": {
                            "type": "string",
                            "description": "New city ID to travel to (optional)"
                        },
                        "time_utc": {
                            "type": "string",
                            "format": "date-time",
                            "description": "New time in UTC (optional)"
                        },
                        "inventory_updates": {
                            "type": "object",
                            "description": "Inventory updates to apply (optional)"
                        }
                    },
                    "required": ["spy_id"]
                }
            },
            {
                "name": "get_available_cities",
                "description": "Get a list of all available cities for travel. Use this when the user asks about travel destinations or wants to see where they can go.",
                "function": cls.get_available_cities,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_train_schedules",
                "description": "Get train schedules between two cities. Use this when the user wants to see available train services or plan travel between specific cities.",
                "function": cls.get_train_schedules,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "origin_city_id": {
                            "type": "string",
                            "description": "ID of the origin city"
                        },
                        "destination_city_id": {
                            "type": "string",
                            "description": "ID of the destination city"
                        }
                    },
                    "required": ["origin_city_id", "destination_city_id"]
                }
            },
            {
                "name": "plan_journey",
                "description": "Plan a complete journey between two cities, including finding available train schedules and calculating travel time. Use this when the user wants to plan a trip or needs travel itinerary information.",
                "function": cls.plan_journey,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "origin_city_id": {
                            "type": "string",
                            "description": "ID of the origin city"
                        },
                        "destination_city_id": {
                            "type": "string",
                            "description": "ID of the destination city"
                        },
                        "departure_date": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Date and time of departure"
                        }
                    },
                    "required": ["origin_city_id", "destination_city_id", "departure_date"]
                }
            }
        ]
