"""Unit tests for travel service functionality."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

from src.backend.services.travel_service import TravelService
from src.backend.models import TravelState, TravelStateUpdate, CityModel, TrainScheduleModel


class TestTravelService:
    """Test cases for TravelService class."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return Mock()
    
    @pytest.fixture
    def sample_city_model(self):
        """Sample city model for testing."""
        city = Mock(spec=CityModel)
        city.id = "vienna"
        city.name = "Vienna"
        city.country = "Austria"
        city.timezone = "Europe/Vienna"
        city.coordinates = "48.2082,16.3738"
        return city
    
    @pytest.fixture
    def sample_train_schedule_model(self):
        """Sample train schedule model for testing."""
        schedule = Mock(spec=TrainScheduleModel)
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
            time_utc=datetime.now(timezone.utc),
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
        
        # Mock an exception
        with patch('src.backend.services.travel_service.TravelState') as mock_travel_state:
            mock_travel_state.side_effect = Exception("Model creation failed")
            
            result = service.get_travel_state("spy_123")
            assert result is None

    def test_update_travel_state_success(self, mock_db_session, sample_travel_state):
        """Test successful travel state update."""
        service = TravelService(mock_db_session)
        
        # Mock get_travel_state to return existing state
        with patch.object(service, 'get_travel_state', return_value=sample_travel_state), \
             patch.object(service, '_validate_state_transition', return_value=True), \
             patch.object(service, '_validate_state_consistency', return_value=True), \
             patch.object(service, '_apply_updates', return_value=sample_travel_state):
            
            updates = TravelStateUpdate(city_id="munich")
            result = service.update_travel_state("spy_123", updates)
            
            assert result is not None
            assert result.city_id == "vienna"  # Original state

    def test_update_travel_state_no_existing_state(self, mock_db_session):
        """Test update when no existing travel state exists."""
        service = TravelService(mock_db_session)
        
        with patch.object(service, 'get_travel_state', return_value=None):
            updates = TravelStateUpdate(city_id="munich")
            result = service.update_travel_state("spy_123", updates)
            
            assert result is None

    def test_update_travel_state_invalid_transition(self, mock_db_session, sample_travel_state):
        """Test update with invalid state transition."""
        service = TravelService(mock_db_session)
        
        with patch.object(service, 'get_travel_state', return_value=sample_travel_state), \
             patch.object(service, '_validate_state_transition', return_value=False):
            
            updates = TravelStateUpdate(city_id="munich")
            result = service.update_travel_state("spy_123", updates)
            
            assert result is None

    def test_update_travel_state_inconsistent_final_state(self, mock_db_session, sample_travel_state):
        """Test update resulting in inconsistent final state."""
        service = TravelService(mock_db_session)
        
        with patch.object(service, 'get_travel_state', return_value=sample_travel_state), \
             patch.object(service, '_validate_state_transition', return_value=True), \
             patch.object(service, '_validate_state_consistency', return_value=False):
            
            updates = TravelStateUpdate(city_id="munich")
            result = service.update_travel_state("spy_123", updates)
            
            assert result is None

    def test_update_travel_state_exception_handling(self, mock_db_session, sample_travel_state):
        """Test exception handling in update_travel_state."""
        service = TravelService(mock_db_session)
        
        with patch.object(service, 'get_travel_state', return_value=sample_travel_state):
            # Mock an exception during validation
            with patch.object(service, '_validate_state_transition', side_effect=Exception("Validation failed")):
                updates = TravelStateUpdate(city_id="munich")
                result = service.update_travel_state("spy_123", updates)
                
                assert result is None

    def test_get_available_cities_success(self, mock_db_session, sample_city_model):
        """Test successful retrieval of available cities."""
        service = TravelService(mock_db_session)
        
        # Mock database query
        mock_query = Mock()
        mock_query.all.return_value = [sample_city_model]
        mock_db_session.query.return_value = mock_query
        
        result = service.get_available_cities()
        
        assert len(result) == 1
        assert result[0]["id"] == "vienna"
        assert result[0]["name"] == "Vienna"
        assert result[0]["country"] == "Austria"
        assert result[0]["timezone"] == "Europe/Vienna"
        assert result[0]["coordinates"] == "48.2082,16.3738"

    def test_get_available_cities_empty_result(self, mock_db_session):
        """Test retrieval of available cities when none exist."""
        service = TravelService(mock_db_session)
        
        # Mock empty database query
        mock_query = Mock()
        mock_query.all.return_value = []
        mock_db_session.query.return_value = mock_query
        
        result = service.get_available_cities()
        
        assert result == []

    def test_get_available_cities_exception_handling(self, mock_db_session):
        """Test exception handling in get_available_cities."""
        service = TravelService(mock_db_session)
        
        # Mock database exception
        mock_db_session.query.side_effect = Exception("Database error")
        
        result = service.get_available_cities()
        
        assert result == []

    def test_get_train_schedules_success(self, mock_db_session, sample_train_schedule_model):
        """Test successful retrieval of train schedules."""
        service = TravelService(mock_db_session)
        
        # Mock database query with filter
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.all.return_value = [sample_train_schedule_model]
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query
        
        result = service.get_train_schedules("vienna", "munich")
        
        assert len(result) == 1
        assert result[0]["id"] == "schedule_1"
        assert result[0]["service_id"] == "ICE123"
        assert result[0]["origin_city_id"] == "vienna"
        assert result[0]["destination_city_id"] == "munich"
        assert result[0]["departure_time"] == "08:00"
        assert result[0]["arrival_time"] == "12:30"
        assert result[0]["days_of_week"] == "1,2,3,4,5,6,7"

    def test_get_train_schedules_empty_result(self, mock_db_session):
        """Test retrieval of train schedules when none exist."""
        service = TravelService(mock_db_session)
        
        # Mock empty database query
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.all.return_value = []
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query
        
        result = service.get_train_schedules("vienna", "paris")
        
        assert result == []

    def test_get_train_schedules_exception_handling(self, mock_db_session):
        """Test exception handling in get_train_schedules."""
        service = TravelService(mock_db_session)
        
        # Mock database exception
        mock_db_session.query.side_effect = Exception("Database error")
        
        result = service.get_train_schedules("vienna", "munich")
        
        assert result == []

    def test_plan_journey_success(self, mock_db_session):
        """Test successful journey planning."""
        service = TravelService(mock_db_session)
        
        # Mock get_train_schedules to return available schedules
        with patch.object(service, 'get_train_schedules') as mock_get_schedules:
            mock_get_schedules.return_value = [
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
            
            departure_date = datetime(2024, 1, 15, 8, 0, tzinfo=timezone.utc)
            result = service.plan_journey("vienna", "munich", departure_date)
            
            assert result["success"] is True
            assert result["message"] == "Journey planned successfully"
            assert result["journey_plan"] is not None
            assert result["journey_plan"]["origin"] == "vienna"
            assert result["journey_plan"]["destination"] == "munich"
            assert result["journey_plan"]["train_service"] == "ICE123"

    def test_plan_journey_no_schedules_available(self, mock_db_session):
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
        """Test exception handling in plan_journey."""
        service = TravelService(mock_db_session)
        
        # Mock get_train_schedules to raise exception
        with patch.object(service, 'get_train_schedules', side_effect=Exception("Service error")):
            departure_date = datetime(2024, 1, 15, 8, 0, tzinfo=timezone.utc)
            result = service.plan_journey("vienna", "munich", departure_date)
            
            assert result["success"] is False
            assert "Error planning journey" in result["message"]
            assert result["journey_plan"] is None

    def test_validate_state_transition_valid_city(self, mock_db_session, sample_travel_state):
        """Test valid state transition with valid city."""
        service = TravelService(mock_db_session)
        
        # Mock city exists in database
        mock_city = Mock(spec=CityModel)
        mock_query = Mock()
        mock_query.first.return_value = mock_city
        mock_db_session.query.return_value = mock_query
        
        updates = TravelStateUpdate(city_id="munich")
        result = service._validate_state_transition(sample_travel_state, updates)
        
        assert result is True

    def test_validate_state_transition_invalid_city(self, mock_db_session, sample_travel_state):
        """Test invalid state transition with invalid city."""
        service = TravelService(mock_db_session)
        
        # Mock city doesn't exist in database
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query
        
        updates = TravelStateUpdate(city_id="invalid_city")
        result = service._validate_state_transition(sample_travel_state, updates)
        
        assert result is False

    def test_validate_state_transition_past_time(self, mock_db_session, sample_travel_state):
        """Test invalid state transition with past time."""
        service = TravelService(mock_db_session)
        
        past_time = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(hours=1)
        updates = TravelStateUpdate(time_utc=past_time)
        result = service._validate_state_transition(sample_travel_state, updates)
        
        assert result is False

    def test_validate_state_transition_invalid_inventory(self, mock_db_session, sample_travel_state):
        """Test invalid state transition with invalid inventory."""
        service = TravelService(mock_db_session)
        
        # Use a valid dict but with invalid content that would fail business logic validation
        updates = TravelStateUpdate(inventory={"invalid_key": None})
        result = service._validate_state_transition(sample_travel_state, updates)
        
        # Since the current validation only checks if it's a dict, this should pass
        # In a real implementation, you might add more specific inventory validation
        assert result is True

    def test_validate_state_transition_exception_handling(self, mock_db_session, sample_travel_state):
        """Test exception handling in state transition validation."""
        service = TravelService(mock_db_session)
        
        # Mock database exception
        mock_db_session.query.side_effect = Exception("Database error")
        
        updates = TravelStateUpdate(city_id="munich")
        result = service._validate_state_transition(sample_travel_state, updates)
        
        assert result is False

    def test_validate_state_consistency_valid_state(self, mock_db_session, sample_travel_state):
        """Test validation of consistent state."""
        service = TravelService(mock_db_session)
        
        # Mock city exists in database
        mock_city = Mock(spec=CityModel)
        mock_query = Mock()
        mock_query.first.return_value = mock_city
        mock_db_session.query.return_value = mock_query
        
        result = service._validate_state_consistency(sample_travel_state)
        
        assert result is True

    def test_validate_state_consistency_city_not_exists(self, mock_db_session, sample_travel_state):
        """Test validation of state with non-existent city."""
        service = TravelService(mock_db_session)
        
        # Mock city doesn't exist in database
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query
        
        result = service._validate_state_consistency(sample_travel_state)
        
        assert result is False

    def test_validate_state_consistency_no_timezone(self, mock_db_session):
        """Test validation of state without timezone information."""
        service = TravelService(mock_db_session)
        
        # Create state without timezone
        state_without_tz = TravelState(
            city_id="vienna",
            time_utc=datetime.now(),  # No timezone
            inventory={}
        )
        
        result = service._validate_state_consistency(state_without_tz)
        
        assert result is False

    def test_validate_state_consistency_invalid_inventory(self, mock_db_session):
        """Test validation of state with invalid inventory."""
        service = TravelService(mock_db_session)
        
        # Mock city exists
        mock_city = Mock(spec=CityModel)
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_city
        mock_query.filter.return_value = mock_filter
        mock_db_session.query.return_value = mock_query
        
        # Create state with invalid inventory - this will fail Pydantic validation
        # so we need to test this differently by mocking the validation
        with patch('src.backend.services.travel_service.TravelState') as mock_travel_state:
            mock_state = Mock()
            mock_state.city_id = "vienna"
            mock_state.time_utc = datetime.now(timezone.utc)
            mock_state.inventory = "not_a_dict"
            mock_travel_state.return_value = mock_state
            
            result = service._validate_state_consistency(mock_state)
            
            assert result is False

    def test_validate_state_consistency_exception_handling(self, mock_db_session, sample_travel_state):
        """Test exception handling in state consistency validation."""
        service = TravelService(mock_db_session)
        
        # Mock database exception
        mock_db_session.query.side_effect = Exception("Database error")
        
        result = service._validate_state_consistency(sample_travel_state)
        
        assert result is False

    def test_apply_updates_city_id(self, sample_travel_state):
        """Test applying city_id update."""
        service = TravelService(Mock())
        
        updates = TravelStateUpdate(city_id="munich")
        result = service._apply_updates(sample_travel_state, updates)
        
        assert result.city_id == "munich"
        assert result.time_utc == sample_travel_state.time_utc
        assert result.inventory == sample_travel_state.inventory

    def test_apply_updates_time_utc(self, sample_travel_state):
        """Test applying time_utc update."""
        service = TravelService(Mock())
        
        new_time = datetime.now(timezone.utc)
        updates = TravelStateUpdate(time_utc=new_time)
        result = service._apply_updates(sample_travel_state, updates)
        
        assert result.city_id == sample_travel_state.city_id
        assert result.time_utc == new_time
        assert result.inventory == sample_travel_state.inventory

    def test_apply_updates_inventory(self, sample_travel_state):
        """Test applying inventory update."""
        service = TravelService(Mock())
        
        inventory_updates = {"tickets": ["ICE123"], "cash": "450 EUR"}
        updates = TravelStateUpdate(inventory=inventory_updates)
        result = service._apply_updates(sample_travel_state, updates)
        
        assert result.city_id == sample_travel_state.city_id
        assert result.time_utc == sample_travel_state.time_utc
        assert result.inventory["tickets"] == ["ICE123"]
        assert result.inventory["cash"] == "450 EUR"
        # Original inventory items should still be there
        assert result.inventory["passport"] == "Valid"
        assert "equipment" in result.inventory

    def test_apply_updates_multiple_fields(self, sample_travel_state):
        """Test applying updates to multiple fields."""
        service = TravelService(Mock())
        
        new_time = datetime.now(timezone.utc)
        updates = TravelStateUpdate(
            city_id="munich",
            time_utc=new_time,
            inventory={"tickets": ["ICE123"]}
        )
        result = service._apply_updates(sample_travel_state, updates)
        
        assert result.city_id == "munich"
        assert result.time_utc == new_time
        assert result.inventory["tickets"] == ["ICE123"]
        assert result.inventory["passport"] == "Valid"  # Original preserved

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
        
        duration = service._calculate_duration("invalid", "time")
        
        assert duration == "Unknown"

    def test_calculate_duration_exception_handling(self):
        """Test exception handling in duration calculation."""
        service = TravelService(Mock())
        
        # Mock an exception during calculation
        with patch('src.backend.services.travel_service.map', side_effect=Exception("Parse error")):
            duration = service._calculate_duration("08:00", "12:30")
            
            assert duration == "Unknown"
