from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# SQLAlchemy ORM Base
Base = declarative_base()
__all__ = ['Spy', 'SpyBase', 'SpyCreate', 'SpyModel', 'Conversation', 'SpyProfile', 'ToolCall', 'ToolCallResponse', 'ChatRequest', 'ChatResponse', 'City', 'CityModel', 'TrainSchedule', 'TrainScheduleModel', 'TravelState', 'TravelStateCreate', 'TravelStateUpdate']

# Database Model: City
class CityModel(Base):
    __tablename__ = "cities"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    timezone = Column(String, nullable=False)
    coordinates = Column(String, nullable=False)  # "lat,long" format

# Database Model: Train Schedule
class TrainScheduleModel(Base):
    __tablename__ = "train_schedules"

    id = Column(String, primary_key=True)
    service_id = Column(String, nullable=False)  # e.g., "ICE123"
    origin_city_id = Column(String, ForeignKey("cities.id"), nullable=False)
    destination_city_id = Column(String, ForeignKey("cities.id"), nullable=False)
    departure_time = Column(String, nullable=False)  # "HH:MM" format
    arrival_time = Column(String, nullable=False)   # "HH:MM" format
    days_of_week = Column(String, nullable=False)  # "1,2,3,4,5,6,7" for daily service

# Database Model: Spy (SQLAlchemy)
class SpyModel(Base):
    __tablename__ = "spies"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    codename = Column(String, nullable=False)
    biography = Column(Text, nullable=False)
    specialty = Column(String, nullable=False)

# Database Model: Conversation
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True)
    spy_id = Column(String, nullable=False)
    messages = Column(Text, nullable=False)  # JSON-serialized message history
    mission_id = Column(String, nullable=True)

# Pydantic Models (for API)
class CityBase(BaseModel):
    """Base Pydantic model for City with common fields"""
    name: str
    country: str
    timezone: str
    coordinates: str

class CityCreate(CityBase):
    """Pydantic model for creating a new city"""
    pass

class City(CityBase):
    """Pydantic model for City responses"""
    id: str

    class Config:
        from_attributes = True

class TrainScheduleBase(BaseModel):
    """Base Pydantic model for Train Schedule with common fields"""
    service_id: str
    origin_city_id: str
    destination_city_id: str
    departure_time: str
    arrival_time: str
    days_of_week: str

class TrainScheduleCreate(TrainScheduleBase):
    """Pydantic model for creating a new train schedule"""
    pass

class TrainSchedule(TrainScheduleBase):
    """Pydantic model for Train Schedule responses"""
    id: str

    class Config:
        from_attributes = True

class TravelState(BaseModel):
    """Pydantic model for spy travel state"""
    city_id: str = Field(..., description="Current city ID")
    time_utc: datetime = Field(..., description="Current time in UTC")
    inventory: Dict[str, Any] = Field(default_factory=dict, description="Travel inventory (tickets, passport, etc.)")

class TravelStateCreate(BaseModel):
    """Pydantic model for creating travel state"""
    city_id: str
    time_utc: datetime
    inventory: Optional[Dict[str, Any]] = None

class TravelStateUpdate(BaseModel):
    """Pydantic model for updating travel state"""
    city_id: Optional[str] = None
    time_utc: Optional[datetime] = None
    inventory: Optional[Dict[str, Any]] = None

class SpyBase(BaseModel):
    """Base Pydantic model for Spy with common fields"""
    name: str
    codename: str
    biography: str
    specialty: str

class SpyCreate(SpyBase):
    """Pydantic model for creating a new spy"""
    pass

class Spy(SpyBase):
    """Pydantic model for Spy responses"""
    id: str
    travel_state: Optional[TravelState] = None

    class Config:
        from_attributes = True

class SpyProfile(BaseModel):
    id: str
    name: str
    codename: str
    biography: str
    specialty: str
    travel_state: Optional[TravelState] = None

# Tool-related Models
class ToolCall(BaseModel):
    """A tool call requested by the model."""
    id: str = Field(..., description="Unique identifier for the tool call")
    name: str = Field(..., description="Name of the tool to call")
    arguments: Dict[str, Any] = Field(..., description="Arguments for the tool call")

class ToolCallResponse(BaseModel):
    """Response from a tool call."""
    tool_call_id: str = Field(..., description="ID of the tool call being responded to")
    name: str = Field(..., description="Name of the tool that was called")
    content: Dict[str, Any] = Field(..., description="Result of the tool call")

# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for chat endpoints."""
    message: str = Field(..., description="The user's message")
    tool_calls: Optional[List[ToolCall]] = Field(
        None, 
        description="Tool calls to process before generating a response"
    )
    tool_outputs: Optional[List[ToolCallResponse]] = Field(
        None,
        description="Outputs from previous tool calls"
    )

class ChatResponse(BaseModel):
    """Response model for chat endpoints."""
    spy_id: str = Field(..., description="ID of the spy being talked to")
    spy_name: str = Field(..., description="Name of the spy being talked to")
    message: str = Field(..., description="The user's message")
    response: str = Field(..., description="The spy's response")
    tool_calls: Optional[List[ToolCall]] = Field(
        None,
        description="Tool calls requested by the model"
    )
    mission_id: Optional[str] = Field(
        None,
        description="[Deprecated] Mission ID for debriefing"
    )
    conversation_id: Optional[str] = Field(
        None,
        description="ID of the conversation, if applicable"
    )