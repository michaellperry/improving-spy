"""Travel state service for managing spy location and inventory."""
import logging
from typing import Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models import TravelState, TravelStateCreate, TravelStateUpdate
from ..repositories.travel_state_repository import TravelStateRepository

# Set up logging
logger = logging.getLogger(__name__)

class TravelStateService:
    """Service for managing spy travel state and inventory."""
    
    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db
        self._repository = TravelStateRepository(db)
    
    def get_travel_state(self, spy_id: str) -> Optional[TravelState]:
        """
        Retrieve travel state for a spy.
        
        Args:
            spy_id: The ID of the spy
            
        Returns:
            TravelState object or None if not found
        """
        try:
            logger.debug(f"Getting travel state for spy: {spy_id}")
            
            travel_state = self._repository.get_by_spy_id(spy_id)
            
            if not travel_state:
                logger.debug(f"No travel state found for spy {spy_id}, creating default state")
                travel_state = self._create_default_state(spy_id)
            
            return travel_state
            
        except Exception as e:
            logger.error(f"Error getting travel state for spy {spy_id}: {str(e)}")
            return None
    
    def update_travel_state(self, spy_id: str, updates: TravelStateUpdate) -> Optional[TravelState]:
        """
        Update travel state for a spy.
        
        Args:
            spy_id: The ID of the spy
            updates: Travel state updates to apply
            
        Returns:
            Updated TravelState object or None if update failed
        """
        try:
            logger.debug(f"Updating travel state for spy: {spy_id}")
            return self._repository.update(spy_id, updates)
            
        except Exception as e:
            logger.error(f"Error updating travel state for spy {spy_id}: {str(e)}")
            return None
    
    def _create_default_state(self, spy_id: str) -> TravelState:
        """
        Create default travel state for a spy.
        
        Args:
            spy_id: The ID of the spy
            
        Returns:
            Created TravelState object
        """
        default_state = TravelStateCreate(
            city_id="vienna",
            time_utc=datetime.now(timezone.utc).replace(hour=8, minute=0, second=0, microsecond=0),
            inventory={
                "passport": "Valid",
                "tickets": [],
                "cash": "500 EUR",
                "equipment": ["disguise", "radio"]
            }
        )
        return self._repository.create(spy_id, default_state)
