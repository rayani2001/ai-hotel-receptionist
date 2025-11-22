"""
Room Service
Handles room inventory and availability management
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from loguru import logger

from database.models import Room, Booking
from config.settings import settings


class RoomService:
    """Service class for managing rooms"""
    
    def __init__(self):
        logger.info("RoomService initialized")
    
    def check_availability(
        self,
        db: Session,
        check_in_date: str,
        check_out_date: str,
        room_type: Optional[str] = None
    ) -> List[Room]:
        """
        Check room availability for given dates
        
        Args:
            db: Database session
            check_in_date: Check-in date (YYYY-MM-DD)
            check_out_date: Check-out date (YYYY-MM-DD)
            room_type: Filter by room type (optional)
        
        Returns:
            List of available rooms
        """
        try:
            check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
            check_out = datetime.strptime(check_out_date, "%Y-%m-%d")
            
            # Build query
            query = db.query(Room).filter(
                Room.is_available == True,
                Room.status == "clean"
            )
            
            if room_type:
                query = query.filter(Room.room_type == room_type)
            
            all_rooms = query.all()
            
            # Filter out rooms with conflicting bookings
            available_rooms = []
            for room in all_rooms:
                conflicting = db.query(Booking).filter(
                    Booking.room_id == room.id,
                    Booking.status.in_(["pending", "confirmed", "checked_in"]),
                    Booking.check_out_date > check_in,
                    Booking.check_in_date < check_out
                ).first()
                
                if not conflicting:
                    available_rooms.append(room)
            
            logger.debug(f"Found {len(available_rooms)} available rooms")
            return available_rooms
            
        except Exception as e:
            logger.error(f"Availability check failed: {e}")
            raise
    
    def get_room_info(self, room_type: str) -> dict:
        """Get information about a room type"""
        if room_type not in settings.ROOM_TYPES:
            raise ValueError(f"Unknown room type: {room_type}")
        
        return settings.ROOM_TYPES[room_type]
    
    def get_all_room_types(self) -> dict:
        """Get information about all room types"""
        return settings.ROOM_TYPES
    
    def create_room(
        self,
        db: Session,
        room_number: str,
        room_type: str,
        floor: int,
        capacity: int = None
    ) -> Room:
        """Create a new room entry"""
        try:
            room_info = self.get_room_info(room_type)
            
            room = Room(
                room_number=room_number,
                room_type=room_type,
                price_per_night=room_info["price"],
                capacity=capacity or room_info["capacity"],
                floor=floor,
                amenities=room_info["amenities"],
                is_available=True,
                status="clean"
            )
            
            db.add(room)
            db.commit()
            db.refresh(room)
            
            logger.success(f"Room created: {room_number}")
            return room
            
        except Exception as e:
            db.rollback()
            logger.error(f"Room creation failed: {e}")
            raise
    
    def update_room_status(
        self,
        db: Session,
        room_id: int,
        status: str
    ) -> Room:
        """Update room status (clean, dirty, maintenance)"""
        try:
            room = db.query(Room).filter(Room.id == room_id).first()
            
            if not room:
                raise ValueError("Room not found")
            
            room.status = status
            db.commit()
            
            logger.info(f"Room {room.room_number} status updated to {status}")
            return room
            
        except Exception as e:
            db.rollback()
            logger.error(f"Status update failed: {e}")
            raise
