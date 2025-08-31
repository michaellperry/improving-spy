from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import logging

# Import from our own models
from ..models import Base, CityModel, TrainScheduleModel, SpyModel, TravelStateModel

# Set up logging
logger = logging.getLogger(__name__)

# SQLite for simplicity
DATABASE_URL = "sqlite:///./spy_chat.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_cities(db):
    """Seed the cities table with European city data."""
    cities_data = [
        {
            "id": "london",
            "name": "London",
            "country": "United Kingdom",
            "timezone": "Europe/London",
            "coordinates": "51.5074,-0.1278"
        },
        {
            "id": "paris",
            "name": "Paris",
            "country": "France",
            "timezone": "Europe/Paris",
            "coordinates": "48.8566,2.3522"
        },
        {
            "id": "brussels",
            "name": "Brussels",
            "country": "Belgium",
            "timezone": "Europe/Brussels",
            "coordinates": "50.8503,4.3517"
        },
        {
            "id": "amsterdam",
            "name": "Amsterdam",
            "country": "Netherlands",
            "timezone": "Europe/Amsterdam",
            "coordinates": "52.3676,4.9041"
        },
        {
            "id": "berlin",
            "name": "Berlin",
            "country": "Germany",
            "timezone": "Europe/Berlin",
            "coordinates": "52.5200,13.4050"
        },
        {
            "id": "hamburg",
            "name": "Hamburg",
            "country": "Germany",
            "timezone": "Europe/Berlin",
            "coordinates": "53.5511,9.9937"
        },
        {
            "id": "prague",
            "name": "Prague",
            "country": "Czech Republic",
            "timezone": "Europe/Prague",
            "coordinates": "50.0755,14.4378"
        },
        {
            "id": "vienna",
            "name": "Vienna",
            "country": "Austria",
            "timezone": "Europe/Vienna",
            "coordinates": "48.2082,16.3738"
        },
        {
            "id": "budapest",
            "name": "Budapest",
            "country": "Hungary",
            "timezone": "Europe/Budapest",
            "coordinates": "47.4979,19.0402"
        },
        {
            "id": "munich",
            "name": "Munich",
            "country": "Germany",
            "timezone": "Europe/Berlin",
            "coordinates": "48.1351,11.5820"
        },
        {
            "id": "zurich",
            "name": "Zurich",
            "country": "Switzerland",
            "timezone": "Europe/Zurich",
            "coordinates": "47.3769,8.5417"
        },
        {
            "id": "milan",
            "name": "Milan",
            "country": "Italy",
            "timezone": "Europe/Rome",
            "coordinates": "45.4642,9.1900"
        },
        {
            "id": "rome",
            "name": "Rome",
            "country": "Italy",
            "timezone": "Europe/Rome",
            "coordinates": "41.9028,12.4964"
        },
        {
            "id": "frankfurt",
            "name": "Frankfurt",
            "country": "Germany",
            "timezone": "Europe/Berlin",
            "coordinates": "50.1109,8.6821"
        }
    ]
    
    for city_data in cities_data:
        city = CityModel(**city_data)
        db.add(city)
    
    logger.info(f"Seeded {len(cities_data)} cities")
    db.commit()

def seed_train_schedules(db):
    """Seed the train_schedules table with realistic train service data."""
    train_data = [
        # London to Paris (135 minutes)
        {
            "id": "london_paris_1",
            "service_id": "Eurostar901",
            "origin_city_id": "london",
            "destination_city_id": "paris",
            "departure_time": "08:00",
            "arrival_time": "10:15",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        {
            "id": "london_paris_2",
            "service_id": "Eurostar902",
            "origin_city_id": "london",
            "destination_city_id": "paris",
            "departure_time": "14:00",
            "arrival_time": "16:15",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        # Paris to Brussels (90 minutes)
        {
            "id": "paris_brussels_1",
            "service_id": "Thalys9310",
            "origin_city_id": "paris",
            "destination_city_id": "brussels",
            "departure_time": "09:00",
            "arrival_time": "10:30",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        {
            "id": "paris_brussels_2",
            "service_id": "Thalys9312",
            "origin_city_id": "paris",
            "destination_city_id": "brussels",
            "departure_time": "15:00",
            "arrival_time": "16:30",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        # Brussels to Amsterdam (110 minutes)
        {
            "id": "brussels_amsterdam_1",
            "service_id": "Thalys9400",
            "origin_city_id": "brussels",
            "destination_city_id": "amsterdam",
            "departure_time": "10:30",
            "arrival_time": "12:20",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        {
            "id": "brussels_amsterdam_2",
            "service_id": "Thalys9402",
            "origin_city_id": "brussels",
            "destination_city_id": "amsterdam",
            "departure_time": "16:30",
            "arrival_time": "18:20",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        # Amsterdam to Berlin (360 minutes)
        {
            "id": "amsterdam_berlin_1",
            "service_id": "ICE120",
            "origin_city_id": "amsterdam",
            "destination_city_id": "berlin",
            "departure_time": "08:00",
            "arrival_time": "14:00",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        {
            "id": "amsterdam_berlin_2",
            "service_id": "ICE122",
            "origin_city_id": "amsterdam",
            "destination_city_id": "berlin",
            "departure_time": "14:00",
            "arrival_time": "20:00",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        # Berlin to Hamburg (100 minutes)
        {
            "id": "berlin_hamburg_1",
            "service_id": "ICE1501",
            "origin_city_id": "berlin",
            "destination_city_id": "hamburg",
            "departure_time": "09:00",
            "arrival_time": "10:40",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        {
            "id": "berlin_hamburg_2",
            "service_id": "ICE1503",
            "origin_city_id": "berlin",
            "destination_city_id": "hamburg",
            "departure_time": "15:00",
            "arrival_time": "16:40",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        # Berlin to Prague (260 minutes)
        {
            "id": "berlin_prague_1",
            "service_id": "EC172",
            "origin_city_id": "berlin",
            "destination_city_id": "prague",
            "departure_time": "08:00",
            "arrival_time": "12:20",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        {
            "id": "berlin_prague_2",
            "service_id": "EC174",
            "origin_city_id": "berlin",
            "destination_city_id": "prague",
            "departure_time": "14:00",
            "arrival_time": "18:20",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        # Prague to Vienna (240 minutes)
        {
            "id": "prague_vienna_1",
            "service_id": "EC270",
            "origin_city_id": "prague",
            "destination_city_id": "vienna",
            "departure_time": "09:00",
            "arrival_time": "13:00",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        {
            "id": "prague_vienna_2",
            "service_id": "EC272",
            "origin_city_id": "prague",
            "destination_city_id": "vienna",
            "departure_time": "15:00",
            "arrival_time": "19:00",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        # Vienna to Budapest (140 minutes)
        {
            "id": "vienna_budapest_1",
            "service_id": "Railjet63",
            "origin_city_id": "vienna",
            "destination_city_id": "budapest",
            "departure_time": "08:00",
            "arrival_time": "10:20",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        {
            "id": "vienna_budapest_2",
            "service_id": "Railjet65",
            "origin_city_id": "vienna",
            "destination_city_id": "budapest",
            "departure_time": "14:00",
            "arrival_time": "16:20",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        # Vienna to Munich (240 minutes)
        {
            "id": "vienna_munich_1",
            "service_id": "ICE123",
            "origin_city_id": "vienna",
            "destination_city_id": "munich",
            "departure_time": "08:00",
            "arrival_time": "12:00",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        {
            "id": "vienna_munich_2",
            "service_id": "ICE456",
            "origin_city_id": "vienna",
            "destination_city_id": "munich",
            "departure_time": "14:00",
            "arrival_time": "18:00",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        # Munich to Zurich (240 minutes)
        {
            "id": "munich_zurich_1",
            "service_id": "EC108",
            "origin_city_id": "munich",
            "destination_city_id": "zurich",
            "departure_time": "09:00",
            "arrival_time": "13:00",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        {
            "id": "munich_zurich_2",
            "service_id": "EC110",
            "origin_city_id": "munich",
            "destination_city_id": "zurich",
            "departure_time": "15:00",
            "arrival_time": "19:00",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        # Zurich to Milan (210 minutes)
        {
            "id": "zurich_milan_1",
            "service_id": "EC52",
            "origin_city_id": "zurich",
            "destination_city_id": "milan",
            "departure_time": "10:00",
            "arrival_time": "13:30",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        {
            "id": "zurich_milan_2",
            "service_id": "EC54",
            "origin_city_id": "zurich",
            "destination_city_id": "milan",
            "departure_time": "16:00",
            "arrival_time": "19:30",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        # Milan to Rome (190 minutes)
        {
            "id": "milan_rome_1",
            "service_id": "Frecciarossa9600",
            "origin_city_id": "milan",
            "destination_city_id": "rome",
            "departure_time": "09:00",
            "arrival_time": "12:10",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        {
            "id": "milan_rome_2",
            "service_id": "Frecciarossa9602",
            "origin_city_id": "milan",
            "destination_city_id": "rome",
            "departure_time": "15:00",
            "arrival_time": "18:10",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        # Paris to Frankfurt (210 minutes)
        {
            "id": "paris_frankfurt_1",
            "service_id": "TGV9550",
            "origin_city_id": "paris",
            "destination_city_id": "frankfurt",
            "departure_time": "08:00",
            "arrival_time": "11:30",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        {
            "id": "paris_frankfurt_2",
            "service_id": "TGV9552",
            "origin_city_id": "paris",
            "destination_city_id": "frankfurt",
            "departure_time": "14:00",
            "arrival_time": "17:30",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        # Frankfurt to Munich (210 minutes)
        {
            "id": "frankfurt_munich_1",
            "service_id": "ICE820",
            "origin_city_id": "frankfurt",
            "destination_city_id": "munich",
            "departure_time": "09:00",
            "arrival_time": "12:30",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        {
            "id": "frankfurt_munich_2",
            "service_id": "ICE822",
            "origin_city_id": "frankfurt",
            "destination_city_id": "munich",
            "departure_time": "15:00",
            "arrival_time": "18:30",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        # Brussels to Frankfurt (200 minutes)
        {
            "id": "brussels_frankfurt_1",
            "service_id": "ICE13",
            "origin_city_id": "brussels",
            "destination_city_id": "frankfurt",
            "departure_time": "08:00",
            "arrival_time": "11:20",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        {
            "id": "brussels_frankfurt_2",
            "service_id": "ICE15",
            "origin_city_id": "brussels",
            "destination_city_id": "frankfurt",
            "departure_time": "14:00",
            "arrival_time": "17:20",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        # Paris to Zurich (240 minutes)
        {
            "id": "paris_zurich_1",
            "service_id": "TGV101",
            "origin_city_id": "paris",
            "destination_city_id": "zurich",
            "departure_time": "10:00",
            "arrival_time": "14:00",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        {
            "id": "paris_zurich_2",
            "service_id": "TGV103",
            "origin_city_id": "paris",
            "destination_city_id": "zurich",
            "departure_time": "16:00",
            "arrival_time": "20:00",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        # Paris to Milan (420 minutes)
        {
            "id": "paris_milan_1",
            "service_id": "TGV9200",
            "origin_city_id": "paris",
            "destination_city_id": "milan",
            "departure_time": "08:00",
            "arrival_time": "15:00",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        {
            "id": "paris_milan_2",
            "service_id": "TGV9202",
            "origin_city_id": "paris",
            "destination_city_id": "milan",
            "departure_time": "14:00",
            "arrival_time": "21:00",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        # Frankfurt to Berlin (240 minutes)
        {
            "id": "frankfurt_berlin_1",
            "service_id": "ICE1200",
            "origin_city_id": "frankfurt",
            "destination_city_id": "berlin",
            "departure_time": "08:00",
            "arrival_time": "12:00",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        {
            "id": "frankfurt_berlin_2",
            "service_id": "ICE1202",
            "origin_city_id": "frankfurt",
            "destination_city_id": "berlin",
            "departure_time": "14:00",
            "arrival_time": "18:00",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        # Paris to Amsterdam (190 minutes)
        {
            "id": "paris_amsterdam_1",
            "service_id": "Thalys9300",
            "origin_city_id": "paris",
            "destination_city_id": "amsterdam",
            "departure_time": "09:00",
            "arrival_time": "12:10",
            "days_of_week": "1,2,3,4,5,6,7"
        },
        {
            "id": "paris_amsterdam_2",
            "service_id": "Thalys9302",
            "origin_city_id": "paris",
            "destination_city_id": "amsterdam",
            "departure_time": "15:00",
            "arrival_time": "18:10",
            "days_of_week": "1,2,3,4,5,6,7"
        }
    ]
    
    for train_data_item in train_data:
        train = TrainScheduleModel(**train_data_item)
        db.add(train)
    
    logger.info(f"Seeded {len(train_data)} train schedules")
    db.commit()

def seed_sample_spy(db):
    """Seed a sample spy for testing purposes."""
    spy_data = {
        "id": "spy_001",
        "name": "Alexandra Petrov",
        "codename": "Shadow",
        "biography": "Former ballet dancer turned intelligence operative. Expert in cultural infiltration and disguise.",
        "specialty": "Cultural Intelligence"
    }
    
    spy = SpyModel(**spy_data)
    db.add(spy)
    
    logger.info("Seeded sample spy: Alexandra Petrov (Shadow)")
    db.commit()

def seed_travel_states(db):
    """Seed initial travel states for spies."""
    import json
    
    # Get current date and set initial time to 08:00
    from datetime import date
    current_date = date.today()
    initial_time = datetime.combine(current_date, datetime.min.time().replace(hour=8, minute=0))
    
    # Create initial travel state for the sample spy
    travel_state_data = {
        "id": "travel_state_001",
        "spy_id": "spy_001",
        "city_id": "vienna",  # Start in Vienna
        "simulated_time": initial_time,
        "inventory": json.dumps({
            "passport": "Valid",
            "tickets": [],
            "cash": "500 EUR",
            "equipment": ["disguise", "radio"]
        })
    }
    
    travel_state = TravelStateModel(**travel_state_data)
    db.add(travel_state)
    
    logger.info("Seeded initial travel state for spy_001 in Vienna")
    db.commit()

# Initialize DB
def init_db():
    """Initialize database with all tables and seed data."""
    logger.info("Initializing database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Seed data
    db = SessionLocal()
    try:
        # Check if data already exists
        city_count = db.query(CityModel).count()
        if city_count == 0:
            seed_cities(db)
            seed_train_schedules(db)
            seed_sample_spy(db)
            seed_travel_states(db)
            logger.info("Database seeded with initial data")
        else:
            logger.info("Database already contains data, skipping seeding")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()
    
    logger.info("Database initialization complete")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()