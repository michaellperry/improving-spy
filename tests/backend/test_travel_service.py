"""Unit tests for travel service functionality."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

from src.backend.services.travel_service import TravelService
from src.backend.models import TravelState, TrainSchedule

# Fixed timestamp for deterministic testing
FIXED_TEST_TIME = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)


class TestTravelService:
    """Test cases for TravelService class."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock()
    
    @pytest.fixture
    def sample_train_schedule(self):
        """Sample train schedule for testing."""
        schedule = Mock(spec=TrainSchedule)
        schedule.id = "schedule_1"
        schedule.service_id = "ICE123"
        schedule.origin_city_id = "vienna"
        schedule.destination_city_id = "munich"
        schedule.departure_time = "08:00"
        schedule.arrival_time = "12:30"
        schedule.days_of_week = "1,2,3,4,5,6,7"
        return schedule
    
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

    def test_get_travel_state_returns_default_state(self, mock_db_session):
        """Test that get_travel_state returns a default state."""
        service = TravelService(mock_db_session)
        result = service.get_travel_state("spy_123")
        
        assert result is not None
        assert result.city_id == "vienna"
        assert result.time_utc is not None
        assert result.inventory is not None
        assert "passport" in result.inventory
        assert "tickets" in result.inventory
        assert "cash" in result.inventory
        assert "equipment" in result.inventory

    def test_get_travel_state_exception_handling(self, mock_db_session):
        """Test exception handling in get_travel_state."""
        service = TravelService(mock_db_session)
        
        # Mock an exception in the repository
        with patch('src.backend.services.travel_service.TravelStateRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_repo.get_by_spy_id.side_effect = Exception("Database error")
            mock_repo_class.return_value = mock_repo
            
            result = service.get_travel_state("spy_123")
            assert result is None

    def test_get_available_cities_success(self, mock_db_session):
        """Test successful retrieval of available cities."""
        service = TravelService(mock_db_session)
        
        # Mock database query - CityModel objects
        mock_city1 = Mock()
        mock_city1.id = "vienna"
        mock_city1.name = "Vienna"
        mock_city1.country = "Austria"
        mock_city1.timezone = "Europe/Vienna"
        mock_city1.coordinates = "48.2082,16.3738"
        
        mock_city2 = Mock()
        mock_city2.id = "munich"
        mock_city2.name = "Munich"
        mock_city2.country = "Germany"
        mock_city2.timezone = "Europe/Berlin"
        mock_city2.coordinates = "48.1351,11.5820"
        
        mock_db_session.query.return_value.all.return_value = [mock_city1, mock_city2]
        
        result = service.get_available_cities()
        
        assert len(result) == 2
        assert result[0]["id"] == "vienna"
        assert result[0]["name"] == "Vienna"
        assert result[0]["timezone"] == "Europe/Vienna"
        assert result[1]["id"] == "munich"
        assert result[1]["name"] == "Munich"
        assert result[1]["timezone"] == "Europe/Berlin"

    def test_get_available_cities_empty_list(self, mock_db_session):
        """Test retrieval of available cities when none exist."""
        service = TravelService(mock_db_session)
        
        mock_db_session.query.return_value.all.return_value = []
        
        result = service.get_available_cities()
        
        assert len(result) == 0

    def test_get_available_cities_exception_handling(self, mock_db_session):
        """Test exception handling in cities retrieval."""
        service = TravelService(mock_db_session)
        
        mock_db_session.query.side_effect = Exception("Database connection failed")
        
        result = service.get_available_cities()
        
        assert len(result) == 0

    def test_get_train_schedules_success(self, mock_db_session):
        """Test successful retrieval of train schedules."""
        service = TravelService(mock_db_session)
        
        # Mock database query
        mock_query = Mock()
        mock_filter = Mock()
        mock_all = Mock()
        
        # Create a mock schedule object
        mock_schedule = Mock()
        mock_schedule.id = "schedule_1"
        mock_schedule.service_id = "ICE123"
        mock_schedule.origin_city_id = "vienna"
        mock_schedule.destination_city_id = "munich"
        mock_schedule.departure_time = "08:00"
        mock_schedule.arrival_time = "12:30"
        mock_schedule.days_of_week = "1,2,3,4,5,6,7"
        
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = [mock_schedule]
        
        result = service.get_train_schedules("vienna", "munich")
        
        assert len(result) == 1
        assert result[0]["service_id"] == "ICE123"
        assert result[0]["origin_city_id"] == "vienna"
        assert result[0]["destination_city_id"] == "munich"

    def test_get_train_schedules_no_schedules(self, mock_db_session):
        """Test train schedules retrieval when none exist."""
        service = TravelService(mock_db_session)
        
        # Mock empty result
        mock_query = Mock()
        mock_filter = Mock()
        mock_all = Mock()
        
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = []
        
        result = service.get_train_schedules("vienna", "paris")
        
        assert len(result) == 0

    def test_get_train_schedules_exception_handling(self, mock_db_session):
        """Test exception handling in train schedules retrieval."""
        service = TravelService(mock_db_session)
        
        mock_db_session.query.side_effect = Exception("Database connection failed")
        
        result = service.get_train_schedules("vienna", "munich")
        
        assert len(result) == 0

    def test_plan_journey_success(self, mock_db_session):
        """Test successful journey planning."""
        service = TravelService(mock_db_session)
        
        # Mock get_train_schedules to return schedules
        with patch.object(service, 'get_train_schedules', return_value=[{
            "service_id": "ICE123",
            "departure_time": "08:00",
            "arrival_time": "12:30"
        }]):
            departure_date = datetime(2024, 1, 15, 8, 0, tzinfo=timezone.utc)
            result = service.plan_journey("vienna", "munich", departure_date)
            
            assert result["success"] is True
            assert "Journey planned successfully" in result["message"]
            assert result["journey_plan"] is not None
            assert result["journey_plan"]["origin"] == "vienna"
            assert result["journey_plan"]["destination"] == "munich"

    def test_plan_journey_no_schedules(self, mock_db_session):
        """Test journey planning when no schedules are available."""
        service = TravelService(mock_db_session)
        
        # Mock get_train_schedules to return empty list
        with patch.object(service, 'get_train_schedules', return_value=[]):
            departure_date = datetime(2024, 1, 15, 8, 0, tzinfo=timezone.utc)
            result = service.plan_journey("vienna", "paris", departure_date)
            
            assert result["success"] is False
            assert "No direct train service available" in result["message"]
            assert result["journey_plan"] is None

    def test_plan_journey_exception_handling(self, mock_db_session):
        """Test exception handling in journey planning."""
        service = TravelService(mock_db_session)
        
        # Mock exception in get_train_schedules
        with patch.object(service, 'get_train_schedules', side_effect=Exception("Database error")):
            departure_date = datetime(2024, 1, 15, 8, 0, tzinfo=timezone.utc)
            result = service.plan_journey("vienna", "munich", departure_date)
            
            assert result["success"] is False
            assert "Error planning journey" in result["message"]
            assert result["journey_plan"] is None

    def test_calculate_duration_same_day(self):
        """Test duration calculation for same-day journey."""
        service = TravelService(Mock())
        
        duration = service._calculate_duration("08:00", "12:30")
        
        assert duration == "4h 30m"

    def test_calculate_duration_overnight(self):
        """Test duration calculation for overnight journey."""
        service = TravelService(Mock())
        
        duration = service._calculate_duration("23:00", "02:00")
        
        assert duration == "3h 0m"

    def test_calculate_duration_short_journey(self):
        """Test duration calculation for short journey."""
        service = TravelService(Mock())
        
        duration = service._calculate_duration("08:00", "08:45")
        
        assert duration == "45m"

    def test_calculate_duration_invalid_format(self):
        """Test duration calculation with invalid time format."""
        service = TravelService(Mock())
        
        duration = service._calculate_duration("invalid", "format")
        
        assert duration == "Unknown"
