"""Travel tools package for AI agent operations."""

# Import the main TravelTools class for backward compatibility
from .travel_tools import TravelTools

# Import individual tool classes for direct access
from .travel_map_tools import MapTools
from .travel_schedule_tools import ScheduleTools
from .travel_execution_tools import TravelExecutionTools
from .travel_planning_tools import PlanningTools

# Import the base class
from .travel_base import TravelToolBase

# Import all models
from .travel_models import (
    GetMapRequest,
    GetScheduleRequest,
    TravelRequest,
    PlanRouteRequest,
    GetTravelStateRequest,
    UpdateTravelStateRequest,
    GetCitiesRequest,
    GetTrainSchedulesRequest,
    PlanJourneyRequest,
)

__all__ = [
    # Main interface
    "TravelTools",
    # Individual tool classes
    "MapTools",
    "ScheduleTools",
    "TravelExecutionTools",
    "PlanningTools",
    # Base class
    "TravelToolBase",
    # Models
    "GetMapRequest",
    "GetScheduleRequest",
    "TravelRequest",
    "PlanRouteRequest",
    "GetTravelStateRequest",
    "UpdateTravelStateRequest",
    "GetCitiesRequest",
    "GetTrainSchedulesRequest",
    "PlanJourneyRequest",
]
