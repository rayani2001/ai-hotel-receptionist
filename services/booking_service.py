"""
Booking Service
Handles all booking-related business logic
"""

from typing import Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from loguru import logger
import uuid

from database.models import Booking, Guest, Room
from config.settings import settings


class BookingService:
    """Service class for managing bookings"""
    
    def __init__(self):
        logger.info("BookingService initialized")
    
    def create_booking(
        self,
        db: Session,
        guest_name: str,
        phone: str,
        check_in_date: str,
        check_out_date: str,
        room_type: str,
        guest_count: int,
        email: Optional[str] = None,
        special_requests: Optional[str] = None
    ) -> Dict:
        """
        Create a new room booking
        
        Args:
            db: Database session
            guest_name: Guest's full name
            phone: Contact phone number
            check_in_date: Check-in date (YYYY-MM-DD)
            check_out_date: Check-out date (YYYY-MM-DD)
            room_type: Type of room (single, double, deluxe, suite)
            guest_count: Number of guests
            email: Guest's email (optional)
            special_requests: Any special requests
        
        Returns:
            Dictionary with booking details
        """
        try:
            # Parse dates
            check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
            check_out = datetime.strptime(check_out_date, "%Y-%m-%d")
            
            # Calculate nights
            nights = (check_out - check_in).days
            
            if nights <= 0:
                raise ValueError("Check-out date must be after check-in date")
            
            # Get or create guest
            guest = db.query(Guest).filter(Guest.phone == phone).first()
            
            if not guest:
                guest = Guest(
                    name=guest_name,
                    phone=phone,
                    email=email
                )
                db.add(guest)
                db.flush()
            
            # Find available room
            available_room = self._find_available_room(
                db, check_in, check_out, room_type
            )
            
            if not available_room:
                raise ValueError(f"No {room_type} rooms available for the selected dates")
            
            # Calculate pricing
            room_info = settings.ROOM_TYPES[room_type]
            room_rate = room_info["price"]
            total_amount = room_rate * nights
            tax_amount = total_amount * 0.12  # 12% tax
            final_amount = total_amount + tax_amount
            
            # Generate booking reference
            booking_reference = self._generate_booking_reference()
            
            # Create booking
            booking = Booking(
                booking_reference=booking_reference,
                guest_id=guest.id,
                room_id=available_room.id,
                check_in_date=check_in,
                check_out_date=check_out,
                number_of_guests=guest_count,
                number_of_nights=nights,
                room_rate=room_rate,
                total_amount=total_amount,
                tax_amount=tax_amount,
                final_amount=final_amount,
                status="confirmed",
                payment_status="pending",
                special_requests=special_requests,
                source="ai_agent"
            )
            
            db.add(booking)
            db.commit()
            db.refresh(booking)
            
            logger.success(f"Booking created: {booking_reference}")
            
            return {
                "success": True,
                "booking_reference": booking_reference,
                "guest_name": guest_name,
                "room_type": room_type,
                "room_number": available_room.room_number,
                "check_in_date": check_in_date,
                "check_out_date": check_out_date,
                "nights": nights,
                "total_amount": final_amount,
                "booking_id": booking.id
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Booking creation failed: {e}")
            raise
    
    def _find_available_room(
        self,
        db: Session,
        check_in: datetime,
        check_out: datetime,
        room_type: str
    ) -> Optional[Room]:
        """Find an available room of the specified type"""
        
        # Get all rooms of the specified type
        rooms = db.query(Room).filter(
            Room.room_type == room_type,
            Room.status == "clean",
            Room.is_available == True
        ).all()
        
        # Check each room for availability
        for room in rooms:
            # Check if room is booked during the requested dates
            conflicting_bookings = db.query(Booking).filter(
                Booking.room_id == room.id,
                Booking.status.in_(["pending", "confirmed", "checked_in"]),
                Booking.check_out_date > check_in,
                Booking.check_in_date < check_out
            ).first()
            
            if not conflicting_bookings:
                return room
        
        return None
    
    def _generate_booking_reference(self) -> str:
        """Generate unique booking reference"""
        timestamp = datetime.now().strftime("%y%m%d")
        random_part = str(uuid.uuid4())[:4].upper()
        return f"BK{timestamp}{random_part}"
    
    def cancel_booking(
        self,
        db: Session,
        booking_reference: str
    ) -> Dict:
        """Cancel a booking"""
        try:
            booking = db.query(Booking).filter(
                Booking.booking_reference == booking_reference
            ).first()
            
            if not booking:
                raise ValueError("Booking not found")
            
            if booking.status == "cancelled":
                raise ValueError("Booking is already cancelled")
            
            booking.status = "cancelled"
            db.commit()
            
            logger.info(f"Booking cancelled: {booking_reference}")
            
            return {
                "success": True,
                "message": "Booking cancelled successfully",
                "booking_reference": booking_reference
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Cancellation failed: {e}")
            raise
    
    def modify_booking(
        self,
        db: Session,
        booking_reference: str,
        new_check_in: Optional[str] = None,
        new_check_out: Optional[str] = None
    ) -> Dict:
        """Modify booking dates"""
        try:
            booking = db.query(Booking).filter(
                Booking.booking_reference == booking_reference
            ).first()
            
            if not booking:
                raise ValueError("Booking not found")
            
            if booking.status not in ["pending", "confirmed"]:
                raise ValueError(f"Cannot modify booking with status: {booking.status}")
            
            # Update dates if provided
            if new_check_in:
                booking.check_in_date = datetime.strptime(new_check_in, "%Y-%m-%d")
            
            if new_check_out:
                booking.check_out_date = datetime.strptime(new_check_out, "%Y-%m-%d")
            
            # Recalculate nights and pricing
            nights = (booking.check_out_date - booking.check_in_date).days
            booking.number_of_nights = nights
            booking.total_amount = booking.room_rate * nights
            booking.tax_amount = booking.total_amount * 0.12
            booking.final_amount = booking.total_amount + booking.tax_amount
            
            db.commit()
            
            logger.info(f"Booking modified: {booking_reference}")
            
            return {
                "success": True,
                "message": "Booking modified successfully",
                "booking_reference": booking_reference,
                "new_check_in": booking.check_in_date.strftime("%Y-%m-%d"),
                "new_check_out": booking.check_out_date.strftime("%Y-%m-%d")
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Modification failed: {e}")
            raise
