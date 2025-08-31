"""Unit tests for simulated time functionality in travel service."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta

from src.backend.services.travel_service import TravelService
from src.backend.models import TravelState

# Fixed timestamps for deterministic testing
FIXED_BASE_TIME = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
FIXED_8AM = FIXED_BASE_TIME.replace(hour=8, minute=0, second=0, microsecond=0)
FIXED_9AM = FIXED_BASE_TIME.replace(hour=9, minute=0, second=0, microsecond=0)
FIXED_10AM = FIXED_BASE_TIME.replace(hour=10, minute=0, second=0, microsecond=0)
FIXED_14PM = FIXED_BASE_TIME.replace(hour=14, minute=0, second=0, microsecond=0)


class TestSimulatedTime:
    """Test cases for simulated time functionality."""
    
    def test_get_travel_state_creates_default_with_simulated_time(self):
        """Test that get_travel_state creates a default state with simulated time."""
        # Mock database session
        mock_db = Mock()
        travel_service = TravelService(mock_db)
        
        # Mock repository to return None initially
        with patch('src.backend.services.travel_service.TravelStateRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_by_spy_id.return_value = None
            
            # Mock the create method to return a valid state
            mock_repo.create.return_value = TravelState(
                city_id="vienna",
                time_utc=FIXED_8AM,
                inventory={
                    "passport": "Valid",
                    "tickets": [],
                    "cash": "500 EUR",
                    "equipment": ["disguise", "radio"]
                }
            )
            
            # Call get_travel_state
            result = travel_service.get_travel_state("spy_001")
            
            # Verify repository was called
            mock_repo.get_by_spy_id.assert_called_once_with("spy_001")
            mock_repo.create.assert_called_once()
            
            # Verify result
            assert result is not None
            assert result.city_id == "vienna"
            assert result.time_utc.hour == 8
            assert result.time_utc.minute == 0
    
    def test_execute_travel_uses_simulated_time(self):
        """Test that travel execution uses simulated time, not real clock time."""
        # Mock database session
        mock_db = Mock()
        travel_service = TravelService(mock_db)
        
        # Mock train schedule
        mock_schedule = Mock()
        mock_schedule.service_id = "ICE123"
        mock_schedule.origin_city_id = "vienna"
        mock_schedule.destination_city_id = "munich"
        mock_schedule.departure_time = "10:00"
        mock_schedule.arrival_time = "14:00"
        
        # Mock database query
        mock_db.query.return_value.filter.return_value.first.return_value = mock_schedule
        
        # Mock travel state repository
        with patch('src.backend.services.travel_service.TravelStateRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            
            # Mock current travel state (spy in Vienna at 09:00)
            current_time = FIXED_9AM
            mock_repo.get_by_spy_id.return_value = TravelState(
                city_id="vienna",
                time_utc=current_time,
                inventory={
                    "passport": "Valid",
                    "tickets": [],
                    "cash": "500 EUR",
                    "equipment": ["disguise", "radio"]
                }
            )
            
            # Mock successful update
            updated_state = TravelState(
                city_id="munich",
                time_utc=FIXED_14PM,
                inventory={
                    "tickets": ["Service ICE123"],
                    "cash": "500 EUR",
                    "equipment": ["disguise", "radio"]
                }
            )
            mock_repo.update.return_value = updated_state
            
            # Call execute_travel
            result = travel_service.execute_travel("spy_001", "ICE123")
            
            # Verify result
            assert result["success"] is True
            assert result["travel_result"]["origin"] == "vienna"
            assert result["travel_result"]["destination"] == "munich"
            assert result["travel_result"]["departure_time"] is not None
            assert result["travel_result"]["arrival_time"] is not None
    
    def test_execute_travel_rejects_missed_departure(self):
        """Test that travel is rejected if departure time has passed in simulated time."""
        # Mock database session
        mock_db = Mock()
        travel_service = TravelService(mock_db)
        
        # Mock train schedule
        mock_schedule = Mock()
        mock_schedule.service_id = "ICE123"
        mock_schedule.origin_city_id = "vienna"
        mock_schedule.destination_city_id = "munich"
        mock_schedule.departure_time = "08:00"  # 8 AM departure
        mock_schedule.arrival_time = "12:00"
        
        # Mock database query
        mock_db.query.return_value.filter.return_value.first.return_value = mock_schedule
        
        # Mock travel state repository
        with patch('src.backend.services.travel_service.TravelStateRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            
            # Mock current travel state (spy in Vienna at 10:00 - missed 8 AM train)
            current_time = FIXED_10AM
            mock_repo.get_by_spy_id.return_value = TravelState(
                city_id="vienna",
                time_utc=current_time,
                inventory={
                    "passport": "Valid",
                    "tickets": [],
                    "cash": "500 EUR",
                    "equipment": ["disguise", "radio"]
                }
            )
            
            # Call execute_travel
            result = travel_service.execute_travel("spy_001", "ICE123")
            
            # Verify result
            assert result["success"] is False
            assert "passed in the spy's timeline" in result["error_message"]
    
    def test_execute_travel_allows_future_departure(self):
        """Test that travel is allowed if departure time is in the future in simulated time."""
        # Mock database session
        mock_db = Mock()
        travel_service = TravelService(mock_db)
        
        # Mock train schedule
        mock_schedule = Mock()
        mock_schedule.service_id = "ICE123"
        mock_schedule.origin_city_id = "vienna"
        mock_schedule.destination_city_id = "munich"
        mock_schedule.departure_time = "12:00"  # 12 PM departure
        mock_schedule.arrival_time = "16:00"
        
        # Mock database query
        mock_db.query.return_value.filter.return_value.first.return_value = mock_schedule
        
        # Mock travel state repository
        with patch('src.backend.services.travel_service.TravelStateRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            
            # Mock current travel state (spy in Vienna at 09:00 - before 12 PM train)
            current_time = FIXED_9AM
            mock_repo.get_by_spy_id.return_value = TravelState(
                city_id="vienna",
                time_utc=current_time,
                inventory={
                    "passport": "Valid",
                    "tickets": [],
                    "cash": "500 EUR",
                    "equipment": ["disguise", "radio"]
                }
            )
            
            # Mock successful update
            updated_state = TravelState(
                city_id="munich",
                time_utc=FIXED_14PM,
                inventory={
                    "tickets": ["Service ICE123"],
                    "cash": "500 EUR",
                    "equipment": ["disguise", "radio"]
                }
            )
            mock_repo.update.return_value = updated_state
            
            # Call execute_travel
            result = travel_service.execute_travel("spy_001", "ICE123")
            
            # Verify result
            assert result["success"] is True
            assert result["travel_result"]["origin"] == "vienna"
            assert result["travel_result"]["destination"] == "munich"
    
    def test_simulated_time_progression(self):
        """Test that simulated time progresses correctly during travel."""
        # Mock database session
        mock_db = Mock()
        travel_service = TravelService(mock_db)
        
        # Mock train schedule
        mock_schedule = Mock()
        mock_schedule.service_id = "ICE123"
        mock_schedule.origin_city_id = "vienna"
        mock_schedule.destination_city_id = "munich"
        mock_schedule.departure_time = "10:00"
        mock_schedule.arrival_time = "14:00"
        
        # Mock database query
        mock_db.query.return_value.filter.return_value.first.return_value = mock_schedule
        
        # Mock travel state repository
        with patch('src.backend.services.travel_service.TravelStateRepository') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            
            # Mock current travel state (spy in Vienna at 09:00)
            current_time = FIXED_9AM
            mock_repo.get_by_spy_id.return_value = TravelState(
                city_id="vienna",
                time_utc=current_time,
                inventory={
                    "passport": "Valid",
                    "tickets": [],
                    "cash": "500 EUR",
                    "equipment": ["disguise", "radio"]
                }
            )
            
            # Mock successful update with progressed time
            updated_state = TravelState(
                city_id="munich",
                time_utc=FIXED_14PM,  # 4 hours later
                inventory={
                    "tickets": ["Service ICE123"],
                    "cash": "500 EUR",
                    "equipment": ["disguise", "radio"]
                }
            )
            mock_repo.update.return_value = updated_state
            
            # Call execute_travel
            result = travel_service.execute_travel("spy_001", "ICE123")
            
            # Verify result
            assert result["success"] is True
            assert result["travel_result"]["origin"] == "vienna"
            assert result["travel_result"]["destination"] == "munich"
            assert result["travel_result"]["departure_time"] is not None
            assert result["travel_result"]["arrival_time"] is not None
            
            # Verify that the spy's simulated time has progressed
            # The arrival time should be after the departure time
            departure_time = result["travel_result"]["departure_time"]
            arrival_time = result["travel_result"]["arrival_time"]
            
            # Handle both string and datetime formats
            if isinstance(departure_time, str):
                # If it's a string, parse it
                if ":" in departure_time and not "T" in departure_time:
                    # Simple HH:MM format
                    departure_hour = int(departure_time.split(":")[0])
                else:
                    # Handle ISO format (e.g., "2024-01-15T10:00:00+00:00")
                    time_part = departure_time.split("T")[1]
                    departure_hour = int(time_part.split(":")[0])
            else:
                # If it's a datetime object
                departure_hour = departure_time.hour
            
            if isinstance(arrival_time, str):
                # If it's a string, parse it
                if ":" in arrival_time and not "T" in arrival_time:
                    # Simple HH:MM format
                    arrival_hour = int(arrival_time.split(":")[0])
                else:
                    # Handle ISO format (e.g., "2024-01-15T14:00:00+00:00")
                    time_part = arrival_time.split("T")[1]
                    arrival_hour = int(time_part.split(":")[0])
            else:
                # If it's a datetime object
                arrival_hour = arrival_time.hour
            
            # Arrival should be after departure
            assert arrival_hour > departure_hour


if __name__ == "__main__":
    pytest.main([__file__])
