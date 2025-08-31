"""Test the simulated time system for spy travel."""
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from src.backend.services.travel_service import TravelService
from src.backend.models import TravelState, TravelStateCreate
from src.backend.repositories.travel_state_repository import TravelStateRepository


class TestSimulatedTime:
    """Test cases for simulated time functionality."""
    
    def test_get_travel_state_creates_default_if_none_exists(self):
        """Test that a default travel state is created if none exists."""
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
                simulated_time=datetime.now(timezone.utc).replace(hour=8, minute=0, second=0, microsecond=0),
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
            assert result.simulated_time.hour == 8
            assert result.simulated_time.minute == 0
    
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
            current_time = datetime.now(timezone.utc).replace(hour=9, minute=0, second=0, microsecond=0)
            mock_repo.get_by_spy_id.return_value = TravelState(
                city_id="vienna",
                simulated_time=current_time,
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
                simulated_time=datetime.now(timezone.utc).replace(hour=14, minute=0, second=0, microsecond=0),
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
            current_time = datetime.now(timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0)
            mock_repo.get_by_spy_id.return_value = TravelState(
                city_id="vienna",
                simulated_time=current_time,
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
            assert result["error_code"] == "MISSED_DEPARTURE"
            assert "passed in the spy's timeline" in result["error_message"]
    
    def test_execute_travel_rejects_wrong_location(self):
        """Test that travel is rejected if spy is not in the origin city."""
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
            
            # Mock current travel state (spy in Munich, not Vienna)
            current_time = datetime.now(timezone.utc).replace(hour=9, minute=0, second=0, microsecond=0)
            mock_repo.get_by_spy_id.return_value = TravelState(
                city_id="munich",  # Wrong city!
                simulated_time=current_time,
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
            assert result["error_code"] == "WRONG_LOCATION"
            assert "Spy is in munich, but service ICE123 departs from vienna" in result["error_message"]


if __name__ == "__main__":
    pytest.main([__file__])
