"""Repository for managing travel states in the database."""
import logging
import json
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from ..models import TravelStateModel, TravelState, TravelStateCreate, TravelStateUpdate

logger = logging.getLogger(__name__)

class TravelStateRepository:
    """Repository for travel state operations."""
    
    def __init__(self, db: Session):
        """Initialize with database session."""
        self.db = db
    
    def get_by_spy_id(self, spy_id: str) -> Optional[TravelState]:
        """
        Get travel state for a specific spy.
        
        Args:
            spy_id: The ID of the spy
            
        Returns:
            TravelState object or None if not found
        """
        try:
            db_travel_state = self.db.query(TravelStateModel).filter(
                TravelStateModel.spy_id == spy_id
            ).first()
            
            if not db_travel_state:
                return None
            
            # Convert database model to Pydantic model
            return TravelState(
                city_id=db_travel_state.city_id,
                simulated_time=db_travel_state.simulated_time,
                inventory=json.loads(db_travel_state.inventory)
            )
            
        except Exception as e:
            logger.error(f"Error getting travel state for spy {spy_id}: {str(e)}")
            return None
    
    def create(self, spy_id: str, travel_state: TravelStateCreate) -> Optional[TravelState]:
        """
        Create a new travel state for a spy.
        
        Args:
            spy_id: The ID of the spy
            travel_state: Travel state data to create
            
        Returns:
            Created TravelState object or None if creation failed
        """
        try:
            db_travel_state = TravelStateModel(
                id=f"travel_state_{spy_id}",
                spy_id=spy_id,
                city_id=travel_state.city_id,
                simulated_time=travel_state.simulated_time,
                inventory=json.dumps(travel_state.inventory or {})
            )
            
            self.db.add(db_travel_state)
            self.db.commit()
            self.db.refresh(db_travel_state)
            
            logger.info(f"Created travel state for spy {spy_id}")
            
            return TravelState(
                city_id=db_travel_state.city_id,
                simulated_time=db_travel_state.simulated_time,
                inventory=json.loads(db_travel_state.inventory)
            )
            
        except Exception as e:
            logger.error(f"Error creating travel state for spy {spy_id}: {str(e)}")
            self.db.rollback()
            return None
    
    def update(self, spy_id: str, updates: TravelStateUpdate) -> Optional[TravelState]:
        """
        Update travel state for a spy.
        
        Args:
            spy_id: The ID of the spy
            updates: Updates to apply to the travel state
            
        Returns:
            Updated TravelState object or None if update failed
        """
        try:
            db_travel_state = self.db.query(TravelStateModel).filter(
                TravelStateModel.spy_id == spy_id
            ).first()
            
            if not db_travel_state:
                logger.warning(f"No travel state found for spy {spy_id}")
                return None
            
            # Apply updates
            if updates.city_id is not None:
                db_travel_state.city_id = updates.city_id
            
            if updates.simulated_time is not None:
                db_travel_state.simulated_time = updates.simulated_time
            
            if updates.inventory is not None:
                # Merge with existing inventory
                current_inventory = json.loads(db_travel_state.inventory)
                current_inventory.update(updates.inventory)
                db_travel_state.inventory = json.dumps(current_inventory)
            
            # Update timestamp
            db_travel_state.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(db_travel_state)
            
            logger.info(f"Updated travel state for spy {spy_id}")
            
            return TravelState(
                city_id=db_travel_state.city_id,
                simulated_time=db_travel_state.simulated_time,
                inventory=json.loads(db_travel_state.inventory)
            )
            
        except Exception as e:
            logger.error(f"Error updating travel state for spy {spy_id}: {str(e)}")
            self.db.rollback()
            return None
    
    def delete(self, spy_id: str) -> bool:
        """
        Delete travel state for a spy.
        
        Args:
            spy_id: The ID of the spy
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            db_travel_state = self.db.query(TravelStateModel).filter(
                TravelStateModel.spy_id == spy_id
            ).first()
            
            if not db_travel_state:
                logger.warning(f"No travel state found for spy {spy_id}")
                return False
            
            self.db.delete(db_travel_state)
            self.db.commit()
            
            logger.info(f"Deleted travel state for spy {spy_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting travel state for spy {spy_id}: {str(e)}")
            self.db.rollback()
            return False
    
    def get_all(self) -> List[TravelState]:
        """
        Get all travel states.
        
        Returns:
            List of all TravelState objects
        """
        try:
            db_travel_states = self.db.query(TravelStateModel).all()
            
            return [
                TravelState(
                    city_id=ts.city_id,
                    simulated_time=ts.simulated_time,
                    inventory=json.loads(ts.inventory)
                )
                for ts in db_travel_states
            ]
            
        except Exception as e:
            logger.error(f"Error getting all travel states: {str(e)}")
            return []
    
    def get_by_city(self, city_id: str) -> List[TravelState]:
        """
        Get all travel states for spies in a specific city.
        
        Args:
            city_id: The city ID to filter by
            
        Returns:
            List of TravelState objects for spies in the specified city
        """
        try:
            db_travel_states = self.db.query(TravelStateModel).filter(
                TravelStateModel.city_id == city_id
            ).all()
            
            return [
                TravelState(
                    city_id=ts.city_id,
                    simulated_time=ts.simulated_time,
                    inventory=json.loads(ts.inventory)
                )
                for ts in db_travel_states
            ]
            
        except Exception as e:
            logger.error(f"Error getting travel states for city {city_id}: {str(e)}")
            return []
