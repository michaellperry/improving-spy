"""Pydantic models for travel tool requests and responses."""

from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class GetMapRequest(BaseModel):
    """Request model for getting transportation network map."""


class GetScheduleRequest(BaseModel):
    """Request model for getting train schedules."""

    origin_id: str = Field(..., description="Starting city identifier")
    date_range: str = Field(..., description="Time window for search")
    destination_id: Optional[str] = Field(
        None, description="Optional target city filter"
    )


class TravelRequest(BaseModel):
    """Request model for executing travel on a service."""

    service_id: str = Field(..., description="Service identifier to travel on")


class PlanRouteRequest(BaseModel):
    """Request model for planning a route."""

    origin_id: str = Field(..., description="Starting city")
    dest_id: str = Field(..., description="Destination city")
    depart_after: str = Field(..., description="Earliest departure time (ISO 8601)")
    prefs: Dict[str, Any] = Field(
        default_factory=dict, description="Travel preferences"
    )


class GetTravelStateRequest(BaseModel):
    """Request model for getting travel state."""


class UpdateTravelStateRequest(BaseModel):
    """Request model for updating travel state."""

    city_id: str = Field(..., description="New city ID")
    time_utc: datetime = Field(..., description="New time in UTC")
    inventory_updates: Optional[Dict[str, Any]] = Field(
        None, description="Inventory updates"
    )


class GetCitiesRequest(BaseModel):
    """Request model for getting available cities."""


class GetTrainSchedulesRequest(BaseModel):
    """Request model for getting train schedules."""

    origin_city_id: str = Field(..., description="Origin city ID")
    destination_city_id: Optional[str] = Field(
        None,
        description="Optional destination city ID. If not provided, returns all "
        "schedules from origin city",
    )


class PlanJourneyRequest(BaseModel):
    """Request model for planning a journey."""

    origin_city_id: str = Field(..., description="Origin city ID")
    destination_city_id: str = Field(..., description="Destination city ID")
    departure_date: datetime = Field(..., description="Departure date and time")
