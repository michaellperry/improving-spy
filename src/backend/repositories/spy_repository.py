from sqlalchemy.orm import Session
from sqlalchemy.future import select
from ..models import Spy, SpyModel
import uuid
import json
from typing import Optional, List, Dict, Any

class SpyRepository:
    def __init__(self, db: Session):
        self.db = db
    
    # Standard CRUD operations
    def get(self, spy_id: str) -> Optional[Spy]:
        """Get a spy by ID."""
        from ..models import CityModel, TravelStateModel
        
        result = self.db.get(SpyModel, spy_id)
        if not result:
            return None
            
        # Get travel state for this spy
        travel_state = self.db.execute(
            select(TravelStateModel).where(TravelStateModel.spy_id == result.id)
        ).scalars().first()
        
        # Get city data if travel state exists
        city = None
        if travel_state:
            city = self.db.execute(
                select(CityModel).where(CityModel.id == travel_state.city_id)
            ).scalars().first()
        
        # Create a temporary object with travel state data
        spy_dict = {
            'id': result.id,
            'name': result.name,
            'codename': result.codename,
            'biography': result.biography,
            'specialty': result.specialty,
        }
        
        # Add travel state if it exists
        if travel_state and city:
            spy_dict['travel_state'] = {
                'city_id': travel_state.city_id,
                'city': {
                    'id': city.id,
                    'name': city.name,
                    'country': city.country,
                    'timezone': city.timezone,
                    'coordinates': city.coordinates
                },
                'time_utc': travel_state.time_utc,
                'inventory': json.loads(travel_state.inventory) if travel_state.inventory else {}
            }
        
        return Spy.model_validate(spy_dict)
        
    def create(self, data) -> Spy:
        """Create a new spy.
        
        Args:
            data: Either a dictionary or Pydantic model containing spy data
            
        Returns:
            Spy: The created spy
        """
        # Convert Pydantic model to dict if needed
        if hasattr(data, 'model_dump'):
            data = data.model_dump()
            
        if "id" not in data:
            data["id"] = str(uuid.uuid4())
            
        spy_model = SpyModel(**data)
        self.db.add(spy_model)
        self.db.commit()
        self.db.refresh(spy_model)
        return Spy.model_validate(spy_model, from_attributes=True)
    
    def list(self, skip: int = 0, limit: int = 100) -> List[Spy]:
        """List all spies with pagination."""
        from ..models import CityModel, TravelStateModel
        
        # Fetch spies with basic data first
        result = self.db.execute(
            select(SpyModel).offset(skip).limit(limit)
        ).scalars().all()
        
        # Manually fetch travel state and city data for each spy
        spies_with_travel_state = []
        for spy in result:
            # Get travel state for this spy
            travel_state = self.db.execute(
                select(TravelStateModel).where(TravelStateModel.spy_id == spy.id)
            ).scalars().first()
            
            # Get city data if travel state exists
            city = None
            if travel_state:
                city = self.db.execute(
                    select(CityModel).where(CityModel.id == travel_state.city_id)
                ).scalars().first()
            
            # Create a temporary object with travel state data
            spy_dict = {
                'id': spy.id,
                'name': spy.name,
                'codename': spy.codename,
                'biography': spy.biography,
                'specialty': spy.specialty,
            }
            
            # Add travel state if it exists
            if travel_state and city:
                spy_dict['travel_state'] = {
                    'city_id': travel_state.city_id,
                    'city': {
                        'id': city.id,
                        'name': city.name,
                        'country': city.country,
                        'timezone': city.timezone,
                        'coordinates': city.coordinates
                    },
                    'time_utc': travel_state.time_utc,
                    'inventory': json.loads(travel_state.inventory) if travel_state.inventory else {}
                }
            
            spies_with_travel_state.append(spy_dict)
        
        return [Spy.model_validate(spy) for spy in spies_with_travel_state]
    
    def update(self, spy_id: str, data: Dict[str, Any]) -> Optional[Spy]:
        """Update a spy."""
        spy = self.db.get(SpyModel, spy_id)
        if not spy:
            return None
            
        for key, value in data.items():
            setattr(spy, key, value)
            
        self.db.commit()
        self.db.refresh(spy)
        return Spy.model_validate(spy, from_attributes=True)
    
    def delete(self, spy_id: str) -> bool:
        """Delete a spy."""
        spy = self.db.get(SpyModel, spy_id)
        if not spy:
            return False
            
        self.db.delete(spy)
        self.db.commit()
        return True
    
    # Custom operations
    def get_by_codename(self, codename: str) -> Optional[Spy]:
        """Get a spy by codename."""
        from ..models import CityModel, TravelStateModel
        
        result = self.db.execute(
            select(SpyModel).where(SpyModel.codename == codename)
        ).scalars().first()
        if not result:
            return None
            
        # Get travel state for this spy
        travel_state = self.db.execute(
            select(TravelStateModel).where(TravelStateModel.spy_id == result.id)
        ).scalars().first()
        
        # Get city data if travel state exists
        city = None
        if travel_state:
            city = self.db.execute(
                select(CityModel).where(CityModel.id == travel_state.city_id)
            ).scalars().first()
        
        # Create a temporary object with travel state data
        spy_dict = {
            'id': result.id,
            'name': result.name,
            'codename': result.codename,
            'biography': result.biography,
            'specialty': result.specialty,
        }
        
        # Add travel state if it exists
        if travel_state and city:
            spy_dict['travel_state'] = {
                'city_id': travel_state.city_id,
                'city': {
                    'id': city.id,
                    'name': city.name,
                    'country': city.country,
                    'timezone': city.timezone,
                    'coordinates': city.coordinates
                },
                'time_utc': travel_state.time_utc,
                'inventory': json.loads(travel_state.inventory) if travel_state.inventory else {}
            }
        
        return Spy.model_validate(spy_dict)
    
    def search_by_specialty(self, specialty: str) -> List[Spy]:
        """Search spies by specialty."""
        result = self.db.execute(
            select(SpyModel).where(SpyModel.specialty == specialty)
        ).scalars().all()
        return [Spy.model_validate(spy, from_attributes=True) for spy in result]
        
    def list_sync(self, session: Session, skip: int = 0, limit: int = 100) -> List[Spy]:
        """List all spies with pagination (synchronous version)."""
        return session.query(Spy).offset(skip).limit(limit).all()
    
    def update_sync(self, session: Session, spy_id: str, data: Dict[str, Any]) -> Optional[Spy]:
        """Update a spy (synchronous version)."""
        spy = self.get_sync(session, spy_id)
        if not spy:
            return None
        
        for key, value in data.items():
            setattr(spy, key, value)
        
        session.commit()
        session.refresh(spy)
        return spy
    
    def delete_sync(self, session: Session, spy_id: str) -> bool:
        """Delete a spy (synchronous version)."""
        spy = self.get_sync(session, spy_id)
        if not spy:
            return False
        
        session.delete(spy)
        session.commit()
        return True
    
    def get_by_codename_sync(self, session: Session, codename: str) -> Optional[Spy]:
        """Get a spy by codename (synchronous version)."""
        return session.query(Spy).filter(Spy.codename == codename).first()
    
    def search_by_specialty_sync(self, session: Session, specialty: str) -> List[Spy]:
        """Search spies by specialty (synchronous version)."""
        return session.query(Spy).filter(Spy.specialty == specialty).all()
