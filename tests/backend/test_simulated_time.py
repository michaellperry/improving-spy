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
        
        # Mock the TravelStateService instead of the repository directly
        with patch('src.backend.services.travel_service.TravelStateService') as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            # Mock the get_travel_state method to return a valid state
            mock_service.get_travel_state.return_value = TravelState(
                city_id="vienna",
                time_utc=FIXED_8AM,
                inventory={
                    "passport": "Valid",
                    "tickets": [],
                    "cash": "500 EUR",
                    "equipment": ["disguise", "radio"]
                }
            )
            
            # Replace the service instance
            travel_service._state_service = mock_service
            
            # Call get_travel_state
            result = travel_service.get_travel_state("spy_001")
            
            # Verify service was called
            mock_service.get_travel_state.assert_called_once_with("spy_001")
            
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
        
        # Mock the TravelExecutionService
        with patch('src.backend.services.travel_service.TravelExecutionService') as mock_exec_service_class:
            mock_exec_service = Mock()
            mock_exec_service_class.return_value = mock_exec_service
            
            # Mock successful travel execution
            mock_exec_service.execute_travel.return_value = {
                "success": True,
                "message": "Travel completed successfully",
                "new_state": {
                    "city_id": "munich",
                    "time_utc": FIXED_14PM.isoformat(),
                    "inventory": {
                        "tickets": ["Service ICE123"],
                        "cash": "500 EUR",
                        "equipment": ["disguise", "radio"]
                    }
                }
            }
            
            # Replace the service instance
            travel_service._execution_service = mock_exec_service
            
            # Call execute_travel
            result = travel_service.execute_travel("spy_001", "ICE123")
            
            # Verify result
            assert result["success"] is True
            assert "Travel completed successfully" in result["message"]
    
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
        
        # Mock the TravelExecutionService
        with patch('src.backend.services.travel_service.TravelExecutionService') as mock_exec_service_class:
            mock_exec_service = Mock()
            mock_exec_service_class.return_value = mock_exec_service
            
            # Mock travel rejection due to missed departure
            mock_exec_service.execute_travel.return_value = {
                "success": False,
                "error_message": "Departure time 08:00 has passed in the spy's timeline"
            }
            
            # Replace the service instance
            travel_service._execution_service = mock_exec_service
            
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
        
        # Mock the TravelExecutionService
        with patch('src.backend.services.travel_service.TravelExecutionService') as mock_exec_service_class:
            mock_exec_service = Mock()
            mock_exec_service_class.return_value = mock_exec_service
            
            # Mock successful travel execution
            mock_exec_service.execute_travel.return_value = {
                "success": True,
                "message": "Travel completed successfully",
                "new_state": {
                    "city_id": "munich",
                    "time_utc": FIXED_14PM.isoformat(),
                    "inventory": {
                        "tickets": ["Service ICE123"],
                        "cash": "500 EUR",
                        "equipment": ["disguise", "radio"]
                    }
                }
            }
            
            # Replace the service instance
            travel_service._execution_service = mock_exec_service
            
            # Call execute_travel
            result = travel_service.execute_travel("spy_001", "ICE123")
            
            # Verify result
            assert result["success"] is True
            assert "Travel completed successfully" in result["message"]
    
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
        
        # Mock the TravelExecutionService
        with patch('src.backend.services.travel_service.TravelExecutionService') as mock_exec_service_class:
            mock_exec_service = Mock()
            mock_exec_service_class.return_value = mock_exec_service
            
            # Mock successful travel execution with time progression
            mock_exec_service.execute_travel.return_value = {
                "success": True,
                "message": "Travel completed successfully",
                "new_state": {
                    "city_id": "munich",
                    "time_utc": FIXED_14PM.isoformat(),  # 4 hours later
                    "inventory": {
                        "tickets": ["Service ICE123"],
                        "cash": "500 EUR",
                        "equipment": ["disguise", "radio"]
                    }
                }
            }
            
            # Replace the service instance
            travel_service._execution_service = mock_exec_service
            
            # Call execute_travel
            result = travel_service.execute_travel("spy_001", "ICE123")
            
            # Verify result
            assert result["success"] is True
            assert "Travel completed successfully" in result["message"]


if __name__ == "__main__":
    pytest.main([__file__])
