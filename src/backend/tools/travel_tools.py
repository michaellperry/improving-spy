"""Travel tools for AI agent operations."""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from ..services.travel_service import TravelService
from ..core.database import get_db

# Set up logging
logger = logging.getLogger(__name__)

# Tool Request/Response Models
class GetMapRequest(BaseModel):
    """Request model for getting transportation network map."""
    pass

class GetScheduleRequest(BaseModel):
    """Request model for getting train schedules."""
    origin_id: str = Field(..., description="Starting city identifier")
    date_range: str = Field(..., description="Time window for search")
    destination_id: Optional[str] = Field(None, description="Optional target city filter")

class TravelRequest(BaseModel):
    """Request model for executing travel on a service."""
    service_id: str = Field(..., description="Service identifier to travel on")

class PlanRouteRequest(BaseModel):
    """Request model for planning a route."""
    origin_id: str = Field(..., description="Starting city")
    dest_id: str = Field(..., description="Destination city")
    depart_after: str = Field(..., description="Earliest departure time (ISO 8601)")
    prefs: Dict[str, Any] = Field(default_factory=dict, description="Travel preferences")

class TravelTools:
    """Tools for travel operations."""
    
    @classmethod
    def get_map(cls) -> Dict[str, Any]:
        """
        Get the complete transportation network graph.
        
        Returns:
            Dict containing cities and route edges with timezone info
        """
        logger.debug("Getting transportation network map")
        
        try:
            # Get database session
            db = next(get_db())
            travel_service = TravelService(db)
            
            # Get map data
            map_data = travel_service.get_transportation_map()
            
            return {
                "response": "Transportation network map retrieved successfully",
                "cities": map_data["cities"],
                "edges": map_data["edges"],
                "tool_calls": []
            }
            
        except Exception as e:
            error_msg = f"Error getting transportation map: {str(e)}"
            logger.error(f"{error_msg} - {type(e).__name__}: {str(e)}")
            return {
                "response": f"Error retrieving transportation map: {str(e)}",
                "cities": [],
                "edges": [],
                "tool_calls": []
            }
    
    @classmethod
    def get_schedule(cls, origin_id: str, date_range: str, destination_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve available train services between cities.
        
        Args:
            origin_id: Starting city identifier
            date_range: Time window for search
            destination_id: Optional target city filter
            
        Returns:
            Dict containing available train services
        """
        logger.debug(f"Getting train schedules from {origin_id} to {destination_id or 'any destination'}")
        
        try:
            # Get database session
            db = next(get_db())
            travel_service = TravelService(db)
            
            # Get schedules
            services = travel_service.get_available_services(origin_id, date_range, destination_id)
            
            return {
                "response": f"Found {len(services)} available train services",
                "services": services,
                "origin_id": origin_id,
                "date_range": date_range,
                "destination_id": destination_id,
                "tool_calls": []
            }
            
        except Exception as e:
            error_msg = f"Error getting train schedules: {str(e)}"
            logger.error(f"{error_msg} - {type(e).__name__}: {str(e)}")
            return {
                "response": f"Error retrieving train schedules: {str(e)}",
                "services": [],
                "origin_id": origin_id,
                "date_range": date_range,
                "destination_id": destination_id,
                "tool_calls": []
            }
    
    @classmethod
    def travel(cls, service_id: str) -> Dict[str, Any]:
        """
        Execute travel on a specific service, updating spy state.
        
        Args:
            service_id: Service identifier to travel on
            
        Returns:
            Dict containing travel result and updated state
        """
        logger.debug(f"Executing travel on service: {service_id}")
        
        try:
            # Get database session
            db = next(get_db())
            travel_service = TravelService(db)
            
            # Execute travel
            result = travel_service.execute_travel(service_id)
            
            if result["success"]:
                return {
                    "response": f"Successfully traveled on service {service_id}",
                    "success": True,
                    "service_id": service_id,
                    "travel_result": result["travel_result"],
                    "updated_state": result["updated_state"],
                    "tool_calls": []
                }
            else:
                return {
                    "response": f"Travel failed on service {service_id}: {result['error_code']}",
                    "success": False,
                    "service_id": service_id,
                    "error_code": result["error_code"],
                    "error_message": result["error_message"],
                    "tool_calls": []
                }
            
        except Exception as e:
            error_msg = f"Error executing travel: {str(e)}"
            logger.error(f"{error_msg} - {type(e).__name__}: {str(e)}")
            return {
                "response": f"Error executing travel: {str(e)}",
                "success": False,
                "service_id": service_id,
                "error_code": "TRAVEL_ERROR",
                "error_message": str(e),
                "tool_calls": []
            }
    
    @classmethod
    def plan_route(cls, origin_id: str, dest_id: str, depart_after: str, 
                   prefs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate guaranteed valid travel itineraries.
        
        Args:
            origin_id: Starting city
            dest_id: Destination city
            depart_after: Earliest departure time (ISO 8601)
            prefs: Travel preferences including min_transfer time
            
        Returns:
            Dict containing planned route itinerary
        """
        logger.debug(f"Planning route from {origin_id} to {dest_id}")
        
        try:
            # Get database session
            db = next(get_db())
            travel_service = TravelService(db)
            
            # Parse departure time
            try:
                depart_time = datetime.fromisoformat(depart_after.replace('Z', '+00:00'))
            except ValueError:
                return {
                    "response": "Invalid departure time format. Use ISO 8601 format (e.g., 2025-08-30T08:00:00Z)",
                    "success": False,
                    "origin_id": origin_id,
                    "dest_id": dest_id,
                    "depart_after": depart_after,
                    "itinerary": None,
                    "tool_calls": []
                }
            
            # Plan route
            route_result = travel_service.plan_route(origin_id, dest_id, depart_time, prefs or {})
            
            if route_result["success"]:
                return {
                    "response": f"Route planned successfully from {origin_id} to {dest_id}",
                    "success": True,
                    "origin_id": origin_id,
                    "dest_id": dest_id,
                    "depart_after": depart_after,
                    "itinerary": route_result["itinerary"],
                    "total_duration": route_result["total_duration"],
                    "tool_calls": []
                }
            else:
                return {
                    "response": f"Route planning failed: {route_result['error_message']}",
                    "success": False,
                    "origin_id": origin_id,
                    "dest_id": dest_id,
                    "depart_after": depart_after,
                    "itinerary": None,
                    "error_message": route_result["error_message"],
                    "tool_calls": []
                }
            
        except Exception as e:
            error_msg = f"Error planning route: {str(e)}"
            logger.error(f"{error_msg} - {type(e).__name__}: {str(e)}")
            return {
                "response": f"Error planning route: {str(e)}",
                "success": False,
                "origin_id": origin_id,
                "dest_id": dest_id,
                "depart_after": depart_after,
                "itinerary": None,
                "error_message": str(e),
                "tool_calls": []
            }
    
    @classmethod
    def get_tools(cls):
        """Return the list of tools for the agent to use."""
        return [
            {
                "name": "get_map",
                "description": "Get the complete transportation network graph with cities and route information. Use this when you need to understand the available travel options and city connections.",
                "function": cls.get_map,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_schedule",
                "description": "Retrieve available train services between cities. Use this when you need to find train schedules for travel planning.",
                "function": cls.get_schedule,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "origin_id": {
                            "type": "string",
                            "description": "Starting city identifier"
                        },
                        "date_range": {
                            "type": "string",
                            "description": "Time window for search"
                        },
                        "destination_id": {
                            "type": "string",
                            "description": "Optional target city filter"
                        }
                    },
                    "required": ["origin_id", "date_range"]
                }
            },
            {
                "name": "travel",
                "description": "Execute travel on a specific service, updating spy state. Use this when you want to travel on a train service and update the spy's location and time.",
                "function": cls.travel,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service_id": {
                            "type": "string",
                            "description": "Service identifier to travel on"
                        }
                    },
                    "required": ["service_id"]
                }
            },
            {
                "name": "plan_route",
                "description": "Generate guaranteed valid travel itineraries between cities. Use this when you need to plan a complete journey with multiple connections.",
                "function": cls.plan_route,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "origin_id": {
                            "type": "string",
                            "description": "Starting city"
                        },
                        "dest_id": {
                            "type": "string",
                            "description": "Destination city"
                        },
                        "depart_after": {
                            "type": "string",
                            "description": "Earliest departure time (ISO 8601 format)"
                        },
                        "prefs": {
                            "type": "object",
                            "description": "Travel preferences including min_transfer time"
                        }
                    },
                    "required": ["origin_id", "dest_id", "depart_after"]
                }
            }
        ]
