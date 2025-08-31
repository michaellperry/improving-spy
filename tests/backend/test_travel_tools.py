"""Unit tests for travel tools functionality."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from typing import Dict, Any

from src.backend.tools.travel_tools import TravelTools, GetTravelStateRequest
from src.backend.tools.travel_tools import GetCitiesRequest, GetTrainSchedulesRequest, PlanJourneyRequest
from src.backend.models import TravelState, TravelStateUpdate

# Fixed timestamp for deterministic testing
FIXED_TEST_TIME = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)


class TestTravelTools:
    """Test cases for TravelTools class."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock()
    
    @pytest.fixture
    def mock_travel_service(self):
        """Mock travel service."""
        service = Mock()
        service.get_travel_state.return_value = TravelState(
            city_id="vienna",
            time_utc=FIXED_TEST_TIME,
            inventory={
                "passport": "Valid",
                "tickets": [],
                "cash": "500 EUR",
                "equipment": ["disguise", "radio"]
            }
        )
        return service
    
    @pytest.fixture
    def sample_travel_state(self):
        """Sample travel state for testing."""
        return TravelState(
            city_id="vienna",
            time_utc=FIXED_TEST_TIME,
            inventory={
                "passport": "Valid",
                "tickets": [],
                "cash": "500 EUR",
                "equipment": ["disguise", "radio"]
            }
        )
    
    @pytest.fixture
    def sample_cities(self):
        """Sample cities data for testing."""
        return [
            {
                "id": "vienna",
                "name": "Vienna",
                "country": "Austria",
                "timezone": "Europe/Vienna",
                "coordinates": "48.2082,16.3738"
            },
            {
                "id": "munich",
                "name": "Munich",
                "country": "Germany",
                "timezone": "Europe/Berlin",
                "coordinates": "48.1351,11.5820"
            }
        ]
    
    @pytest.fixture
    def sample_train_schedules(self):
        """Sample train schedules for testing."""
        return [
            {
                "id": "schedule_1",
                "service_id": "ICE123",
                "origin_city_id": "vienna",
                "destination_city_id": "munich",
                "departure_time": "08:00",
                "arrival_time": "12:30",
                "days_of_week": "1,2,3,4,5,6,7"
            }
        ]

    def test_get_travel_state_success(self, mock_db_session, mock_travel_service):
        """Test successful retrieval of travel state."""
        with patch('src.backend.tools.travel_tools.get_db') as mock_get_db, \
             patch('src.backend.tools.travel_tools.TravelService') as mock_service_class:
            
            mock_get_db.return_value = iter([mock_db_session])
            mock_service_class.return_value = mock_travel_service
            
            result = TravelTools.get_travel_state("spy_123")
            
            assert result["response"] == "Current travel state for spy spy_123"
            assert result["spy_id"] == "spy_123"
            assert result["travel_state"] is not None
            assert result["travel_state"]["city_id"] == "vienna"
            assert "passport" in result["travel_state"]["inventory"]
            assert result["tool_calls"] == []

    def test_get_travel_state_no_state_found(self, mock_db_session):
        """Test travel state retrieval when no state exists."""
        with patch('src.backend.tools.travel_tools.get_db') as mock_get_db, \
             patch('src.backend.tools.travel_tools.TravelService') as mock_service_class:
            
            mock_get_db.return_value = iter([mock_db_session])
            mock_service = Mock()
            mock_service.get_travel_state.return_value = None
            mock_service_class.return_value = mock_service
            
            result = TravelTools.get_travel_state("spy_456")
            
            assert result["response"] == "No travel state found for spy spy_456"
            assert result["spy_id"] == "spy_456"
            assert result["travel_state"] is None
            assert result["tool_calls"] == []

    def test_get_travel_state_error_handling(self, mock_db_session):
        """Test error handling in travel state retrieval."""
        with patch('src.backend.tools.travel_tools.get_db') as mock_get_db:
            mock_get_db.side_effect = Exception("Database connection failed")
            
            result = TravelTools.get_travel_state("spy_789")
            
            assert "Error getting travel state" in result["response"]
            assert result["spy_id"] == "spy_789"
            assert result["travel_state"] is None
            assert result["tool_calls"] == []

    def test_get_available_cities_success(self, mock_db_session, sample_cities):
        """Test successful retrieval of available cities."""
        with patch('src.backend.tools.travel_tools.get_db') as mock_get_db, \
             patch('src.backend.tools.travel_tools.TravelService') as mock_service_class:
            
            mock_get_db.return_value = iter([mock_db_session])
            mock_service = Mock()
            mock_service.get_available_cities.return_value = sample_cities
            mock_service_class.return_value = mock_service
            
            result = TravelTools.get_available_cities()
            
            assert result["response"] == "Found 2 available cities"
            assert result["cities"] == sample_cities
            assert result["count"] == 2
            assert result["tool_calls"] == []

    def test_get_available_cities_empty_list(self, mock_db_session):
        """Test retrieval of available cities when none exist."""
        with patch('src.backend.tools.travel_tools.get_db') as mock_get_db, \
             patch('src.backend.tools.travel_tools.TravelService') as mock_service_class:
            
            mock_get_db.return_value = iter([mock_db_session])
            mock_service = Mock()
            mock_service.get_available_cities.return_value = []
            mock_service_class.return_value = mock_service
            
            result = TravelTools.get_available_cities()
            
            assert result["response"] == "Found 0 available cities"
            assert result["cities"] == []
            assert result["count"] == 0
            assert result["tool_calls"] == []

    def test_get_available_cities_error_handling(self, mock_db_session):
        """Test error handling in cities retrieval."""
        with patch('src.backend.tools.travel_tools.get_db') as mock_get_db:
            mock_get_db.side_effect = Exception("Database connection failed")
            
            result = TravelTools.get_available_cities()
            
            assert "Error retrieving cities" in result["response"]
            assert result["cities"] == []
            assert result["count"] == 0
            assert result["tool_calls"] == []

    def test_get_train_schedules_success(self, mock_db_session, sample_train_schedules):
        """Test successful retrieval of train schedules."""
        with patch('src.backend.tools.travel_tools.get_db') as mock_get_db, \
             patch('src.backend.tools.travel_tools.TravelService') as mock_service_class:
            
            mock_get_db.return_value = iter([mock_db_session])
            mock_service = Mock()
            mock_service.get_train_schedules.return_value = sample_train_schedules
            mock_service_class.return_value = mock_service
            
            result = TravelTools.get_train_schedules("vienna", "munich")
            
            assert result["response"] == "Found 1 train schedules from vienna to munich"
            assert result["schedules"] == sample_train_schedules
            assert result["count"] == 1
            assert result["origin"] == "vienna"
            assert result["destination"] == "munich"
            assert result["tool_calls"] == []

    def test_get_train_schedules_no_schedules(self, mock_db_session):
        """Test train schedules retrieval when none exist."""
        with patch('src.backend.tools.travel_tools.get_db') as mock_get_db, \
             patch('src.backend.tools.travel_tools.TravelService') as mock_service_class:
            
            mock_get_db.return_value = iter([mock_db_session])
            mock_service = Mock()
            mock_service.get_train_schedules.return_value = []
            mock_service_class.return_value = mock_service
            
            result = TravelTools.get_train_schedules("vienna", "paris")
            
            assert result["response"] == "Found 0 train schedules from vienna to paris"
            assert result["schedules"] == []
            assert result["count"] == 0
            assert result["origin"] == "vienna"
            assert result["destination"] == "paris"
            assert result["tool_calls"] == []

    def test_get_train_schedules_error_handling(self, mock_db_session):
        """Test error handling in train schedules retrieval."""
        with patch('src.backend.tools.travel_tools.get_db') as mock_get_db:
            mock_get_db.side_effect = Exception("Database connection failed")
            
            result = TravelTools.get_train_schedules("vienna", "munich")
            
            assert "Error retrieving train schedules" in result["response"]
            assert result["schedules"] == []
            assert result["count"] == 0
            assert result["origin"] == "vienna"
            assert result["destination"] == "munich"
            assert result["tool_calls"] == []

    def test_plan_journey_success(self, mock_db_session):
        """Test successful journey planning."""
        with patch('src.backend.tools.travel_tools.get_db') as mock_get_db, \
             patch('src.backend.tools.travel_tools.TravelService') as mock_service_class:
            
            mock_get_db.return_value = iter([mock_db_session])
            mock_service = Mock()
            mock_service.plan_journey.return_value = {
                "success": True,
                "message": "Journey planned successfully",
                "journey_plan": {
                    "origin": "vienna",
                    "destination": "munich",
                    "departure_date": "2024-01-15T08:00:00",
                    "train_service": "ICE123",
                    "departure_time": "08:00",
                    "arrival_time": "12:30",
                    "estimated_duration": "4h 30m"
                }
            }
            mock_service_class.return_value = mock_service
            
            departure_date = datetime(2024, 1, 15, 8, 0, tzinfo=timezone.utc)
            result = TravelTools.plan_journey("vienna", "munich", departure_date)
            
            assert result["response"] == "Journey planned successfully"
            assert result["success"] is True
            assert result["journey_plan"] is not None
            assert result["origin"] == "vienna"
            assert result["destination"] == "munich"
            assert result["departure_date"] == "2024-01-15T08:00:00+00:00"
            assert result["tool_calls"] == []

    def test_plan_journey_failure(self, mock_db_session):
        """Test journey planning failure."""
        with patch('src.backend.tools.travel_tools.get_db') as mock_get_db, \
             patch('src.backend.tools.travel_tools.TravelService') as mock_service_class:
            
            mock_get_db.return_value = iter([mock_db_session])
            mock_service = Mock()
            mock_service.plan_journey.return_value = {
                "success": False,
                "message": "No direct train service available from vienna to paris",
                "journey_plan": None
            }
            mock_service_class.return_value = mock_service
            
            departure_date = datetime(2024, 1, 15, 8, 0, tzinfo=timezone.utc)
            result = TravelTools.plan_journey("vienna", "paris", departure_date)
            
            assert result["response"] == "No direct train service available from vienna to paris"
            assert result["success"] is False
            assert result["journey_plan"] is None
            assert result["origin"] == "vienna"
            assert result["destination"] == "paris"
            assert result["tool_calls"] == []

    def test_plan_journey_error_handling(self, mock_db_session):
        """Test error handling in journey planning."""
        with patch('src.backend.tools.travel_tools.get_db') as mock_get_db:
            mock_get_db.side_effect = Exception("Database connection failed")
            
            departure_date = datetime(2024, 1, 15, 8, 0, tzinfo=timezone.utc)
            result = TravelTools.plan_journey("vienna", "munich", departure_date)
            
            assert "Error planning journey" in result["response"]
            assert result["success"] is False
            assert result["journey_plan"] is None
            assert result["origin"] == "vienna"
            assert result["destination"] == "munich"
            assert result["tool_calls"] == []

    def test_get_tools_returns_correct_structure(self):
        """Test that get_tools returns the correct tool structure."""
        tools = TravelTools.get_tools("test_spy_123")
        
        assert len(tools) == 8  # Should have 8 tools
        
        # Check tool names
        tool_names = [tool["name"] for tool in tools]
        expected_names = [
            "get_map",
            "get_schedule",
            "travel",
            "plan_route",
            "get_travel_state",
            "get_available_cities",
            "get_train_schedules",
            "plan_journey"
        ]
        assert set(tool_names) == set(expected_names)
        
        # Check each tool has required fields
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "function" in tool
            assert "parameters" in tool
            assert "type" in tool["parameters"]
            assert "properties" in tool["parameters"]
            assert "required" in tool["parameters"]

    def test_tool_parameters_validation(self):
        """Test that tool parameters are correctly defined."""
        tools = TravelTools.get_tools("test_spy_123")
        
        # Test get_travel_state parameters (no spy_id needed - bound to context)
        travel_state_tool = next(t for t in tools if t["name"] == "get_travel_state")
        assert "spy_id" not in travel_state_tool["parameters"]["properties"]
        assert "spy_id" not in travel_state_tool["parameters"]["required"]
        
        # Test get_train_schedules parameters
        schedules_tool = next(t for t in tools if t["name"] == "get_train_schedules")
        assert "origin_city_id" in schedules_tool["parameters"]["properties"]
        assert "destination_city_id" in schedules_tool["parameters"]["properties"]
        assert "origin_city_id" in schedules_tool["parameters"]["required"]
        assert "destination_city_id" in schedules_tool["parameters"]["required"]


class TestTravelToolsRequestModels:
    """Test cases for travel tools request models."""
    
    def test_get_travel_state_request(self):
        """Test GetTravelStateRequest model."""
        request = GetTravelStateRequest()
        # No fields needed - spy_id is bound to context
    
    def test_get_cities_request(self):
        """Test GetCitiesRequest model."""
        request = GetCitiesRequest()
        # Should not raise any errors
    
    def test_get_train_schedules_request(self):
        """Test GetTrainSchedulesRequest model."""
        request = GetTrainSchedulesRequest(
            origin_city_id="vienna",
            destination_city_id="munich"
        )
        assert request.origin_city_id == "vienna"
        assert request.destination_city_id == "munich"
    
    def test_plan_journey_request(self):
        """Test PlanJourneyRequest model."""
        departure_date = datetime(2024, 1, 15, 8, 0, tzinfo=timezone.utc)
        request = PlanJourneyRequest(
            origin_city_id="vienna",
            destination_city_id="munich",
            departure_date=departure_date
        )
        assert request.origin_city_id == "vienna"
        assert request.destination_city_id == "munich"
        assert request.departure_date == departure_date
