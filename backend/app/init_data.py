"""
Initialize database with sample smart meters and renewable energy sources
"""

import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.smart_meter import SmartMeter, Base

logger = logging.getLogger(__name__)


def init_smart_meters(db: Session):
    """Initialize smart meters if they don't exist"""
    
    # Check if meters already exist
    existing_count = db.query(SmartMeter).count()
    if existing_count > 0:
        logger.info(f"Smart meters already initialized ({existing_count} meters found)")
        return
    
    logger.info("Initializing smart meters...")
    
    meters = [
        {
            "meter_id": "SM001",
            "location": "Residential Area A - House 1",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "meter_type": "residential",
            "installation_date": datetime(2023, 1, 15, 10, 0, 0),
            "firmware_version": "v2.1.3",
            "is_active": True
        },
        {
            "meter_id": "SM002",
            "location": "Residential Area A - House 2",
            "latitude": 40.7130,
            "longitude": -74.0058,
            "meter_type": "residential",
            "installation_date": datetime(2023, 1, 16, 11, 0, 0),
            "firmware_version": "v2.1.3",
            "is_active": True
        },
        {
            "meter_id": "SM003",
            "location": "Commercial District - Office Building",
            "latitude": 40.7589,
            "longitude": -73.9851,
            "meter_type": "commercial",
            "installation_date": datetime(2023, 2, 1, 9, 0, 0),
            "firmware_version": "v2.2.1",
            "is_active": True
        },
        {
            "meter_id": "SM004",
            "location": "Industrial Zone - Factory 1",
            "latitude": 40.6892,
            "longitude": -74.0445,
            "meter_type": "industrial",
            "installation_date": datetime(2023, 2, 15, 14, 0, 0),
            "firmware_version": "v2.2.1",
            "is_active": True
        },
        {
            "meter_id": "SM005",
            "location": "Residential Area B - Apartment Complex",
            "latitude": 40.7505,
            "longitude": -73.9934,
            "meter_type": "residential",
            "installation_date": datetime(2023, 3, 1, 12, 0, 0),
            "firmware_version": "v2.1.3",
            "is_active": True
        }
    ]
    
    for meter_data in meters:
        meter = SmartMeter(**meter_data)
        db.add(meter)
    
    db.commit()
    logger.info(f"Successfully initialized {len(meters)} smart meters")


def initialize_database():
    """Initialize database with sample data"""
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # Create session
        db = SessionLocal()
        
        try:
            # Initialize smart meters
            init_smart_meters(db)
            
            logger.info("Database initialization completed successfully")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    initialize_database()

