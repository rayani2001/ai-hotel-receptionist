"""
Database Initialization Script
Creates tables and populates with sample data
"""

import sys
sys.path.append('..')

from database.database import init_database, SessionLocal
from database.models import Room, Guest, Booking
from config.settings import settings
from loguru import logger
from datetime import datetime, timedelta


def seed_rooms():
    """Create sample room inventory"""
    db = SessionLocal()
    
    try:
        # Check if rooms already exist
        existing = db.query(Room).first()
        if existing:
            logger.info("Rooms already exist, skipping seeding")
            return
        
        logger.info("Creating sample rooms...")
        
        # Create rooms for each type
        room_configs = [
            # Single rooms (101-105)
            ("101", "single", 1, settings.ROOM_TYPES["single"]["price"]),
            ("102", "single", 1, settings.ROOM_TYPES["single"]["price"]),
            ("103", "single", 1, settings.ROOM_TYPES["single"]["price"]),
            ("104", "single", 1, settings.ROOM_TYPES["single"]["price"]),
            ("105", "single", 1, settings.ROOM_TYPES["single"]["price"]),
            
            # Double rooms (201-210)
            ("201", "double", 2, settings.ROOM_TYPES["double"]["price"]),
            ("202", "double", 2, settings.ROOM_TYPES["double"]["price"]),
            ("203", "double", 2, settings.ROOM_TYPES["double"]["price"]),
            ("204", "double", 2, settings.ROOM_TYPES["double"]["price"]),
            ("205", "double", 2, settings.ROOM_TYPES["double"]["price"]),
            ("206", "double", 2, settings.ROOM_TYPES["double"]["price"]),
            ("207", "double", 2, settings.ROOM_TYPES["double"]["price"]),
            ("208", "double", 2, settings.ROOM_TYPES["double"]["price"]),
            ("209", "double", 2, settings.ROOM_TYPES["double"]["price"]),
            ("210", "double", 2, settings.ROOM_TYPES["double"]["price"]),
            
            # Deluxe rooms (301-308)
            ("301", "deluxe", 3, settings.ROOM_TYPES["deluxe"]["price"]),
            ("302", "deluxe", 3, settings.ROOM_TYPES["deluxe"]["price"]),
            ("303", "deluxe", 3, settings.ROOM_TYPES["deluxe"]["price"]),
            ("304", "deluxe", 3, settings.ROOM_TYPES["deluxe"]["price"]),
            ("305", "deluxe", 3, settings.ROOM_TYPES["deluxe"]["price"]),
            ("306", "deluxe", 3, settings.ROOM_TYPES["deluxe"]["price"]),
            ("307", "deluxe", 3, settings.ROOM_TYPES["deluxe"]["price"]),
            ("308", "deluxe", 3, settings.ROOM_TYPES["deluxe"]["price"]),
            
            # Suites (401-404)
            ("401", "suite", 4, settings.ROOM_TYPES["suite"]["price"]),
            ("402", "suite", 4, settings.ROOM_TYPES["suite"]["price"]),
            ("403", "suite", 4, settings.ROOM_TYPES["suite"]["price"]),
            ("404", "suite", 4, settings.ROOM_TYPES["suite"]["price"]),
        ]
        
        for room_number, room_type, floor, price in room_configs:
            room_info = settings.ROOM_TYPES[room_type]
            
            room = Room(
                room_number=room_number,
                room_type=room_type,
                price_per_night=price,
                capacity=room_info["capacity"],
                floor=floor,
                amenities=room_info["amenities"],
                is_available=True,
                status="clean"
            )
            db.add(room)
        
        db.commit()
        logger.success(f"Created {len(room_configs)} rooms")
        
    except Exception as e:
        logger.error(f"Error seeding rooms: {e}")
        db.rollback()
    finally:
        db.close()


def seed_sample_bookings():
    """Create some sample bookings for testing"""
    db = SessionLocal()
    
    try:
        # Check if bookings exist
        existing = db.query(Booking).first()
        if existing:
            logger.info("Bookings already exist, skipping")
            return
        
        logger.info("Creating sample bookings...")
        
        # Create sample guest
        guest = Guest(
            name="John Doe",
            email="john.doe@example.com",
            phone="+911234567890",
            address="123 Sample Street, Mumbai",
            id_proof_type="passport",
            id_proof_number="A1234567"
        )
        db.add(guest)
        db.flush()
        
        # Create a sample booking
        room = db.query(Room).filter(Room.room_type == "double").first()
        
        if room:
            check_in = datetime.now() + timedelta(days=7)
            check_out = check_in + timedelta(days=3)
            
            booking = Booking(
                booking_reference="BK2501010001",
                guest_id=guest.id,
                room_id=room.id,
                check_in_date=check_in,
                check_out_date=check_out,
                number_of_guests=2,
                number_of_nights=3,
                room_rate=room.price_per_night,
                total_amount=room.price_per_night * 3,
                tax_amount=(room.price_per_night * 3) * 0.12,
                final_amount=(room.price_per_night * 3) * 1.12,
                status="confirmed",
                payment_status="pending",
                source="website"
            )
            db.add(booking)
            db.commit()
            
            logger.success("Created sample booking")
        
    except Exception as e:
        logger.error(f"Error creating sample bookings: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Main initialization function"""
    logger.info("="*60)
    logger.info("AI HOTEL RECEPTIONIST - DATABASE INITIALIZATION")
    logger.info("="*60)
    
    try:
        # Create tables
        logger.info("Creating database tables...")
        init_database()
        
        # Seed data
        logger.info("Seeding initial data...")
        seed_rooms()
        seed_sample_bookings()
        
        logger.success("="*60)
        logger.success("DATABASE INITIALIZATION COMPLETE!")
        logger.success("="*60)
        logger.info(f"Hotel Name: {settings.HOTEL_NAME}")
        logger.info("You can now start the application with: python main.py")
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
