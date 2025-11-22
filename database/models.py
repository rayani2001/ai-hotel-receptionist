"""
Database Models
SQLAlchemy ORM models for hotel management system
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Conversation(Base):
    """Store conversation history for analytics and learning"""
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False, index=True)
    user_message = Column(Text, nullable=False)
    agent_response = Column(Text, nullable=False)
    detected_language = Column(String(10))
    detected_intent = Column(String(50))
    confidence_score = Column(Float)
    extracted_entities = Column(JSON)
    sentiment_score = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Conversation {self.id}: {self.detected_intent}>"


class Room(Base):
    """Room inventory management"""
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(10), unique=True, nullable=False)
    room_type = Column(String(50), nullable=False)  # single, double, deluxe, suite
    price_per_night = Column(Float, nullable=False)
    capacity = Column(Integer, nullable=False)
    floor = Column(Integer)
    amenities = Column(JSON)  # List of amenities
    is_available = Column(Boolean, default=True)
    status = Column(String(20), default="clean")  # clean, dirty, maintenance
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = relationship("Booking", back_populates="room")
    
    def __repr__(self):
        return f"<Room {self.room_number}: {self.room_type}>"


class Guest(Base):
    """Guest information"""
    __tablename__ = "guests"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20), nullable=False, index=True)
    address = Column(Text)
    id_proof_type = Column(String(50))  # passport, aadhar, driving_license
    id_proof_number = Column(String(50))
    preferences = Column(JSON)  # Room preferences, dietary requirements, etc.
    loyalty_points = Column(Integer, default=0)
    is_vip = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = relationship("Booking", back_populates="guest")
    
    def __repr__(self):
        return f"<Guest {self.name}: {self.phone}>"


class Booking(Base):
    """Room bookings"""
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_reference = Column(String(20), unique=True, nullable=False, index=True)
    
    # Foreign Keys
    guest_id = Column(Integer, ForeignKey("guests.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    
    # Booking Details
    check_in_date = Column(DateTime, nullable=False)
    check_out_date = Column(DateTime, nullable=False)
    number_of_guests = Column(Integer, nullable=False)
    number_of_nights = Column(Integer, nullable=False)
    
    # Pricing
    room_rate = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    final_amount = Column(Float, nullable=False)
    
    # Status
    status = Column(String(20), default="pending")  # pending, confirmed, checked_in, checked_out, cancelled
    payment_status = Column(String(20), default="pending")  # pending, paid, refunded
    
    # Additional Info
    special_requests = Column(Text)
    source = Column(String(50), default="ai_agent")  # ai_agent, website, phone, walk_in
    conversation_id = Column(String, ForeignKey("conversations.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    guest = relationship("Guest", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
    
    def __repr__(self):
        return f"<Booking {self.booking_reference}: {self.status}>"


class DiningReservation(Base):
    """Restaurant/dining reservations"""
    __tablename__ = "dining_reservations"
    
    id = Column(Integer, primary_key=True, index=True)
    reservation_code = Column(String(20), unique=True, nullable=False)
    guest_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100))
    
    reservation_date = Column(DateTime, nullable=False)
    meal_type = Column(String(20), nullable=False)  # breakfast, lunch, dinner
    number_of_people = Column(Integer, nullable=False)
    
    special_requests = Column(Text)
    status = Column(String(20), default="confirmed")  # confirmed, completed, cancelled
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<DiningReservation {self.reservation_code}: {self.meal_type}>"


class EventBooking(Base):
    """Party hall / event bookings"""
    __tablename__ = "event_bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_code = Column(String(20), unique=True, nullable=False)
    
    # Contact Info
    organizer_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100))
    
    # Event Details
    event_date = Column(DateTime, nullable=False)
    event_type = Column(String(50))  # wedding, birthday, corporate, conference
    hall_type = Column(String(50), nullable=False)  # small, medium, large
    number_of_guests = Column(Integer, nullable=False)
    duration_hours = Column(Integer, nullable=False)
    
    # Pricing
    price_per_hour = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    
    # Additional Services
    catering_required = Column(Boolean, default=False)
    decoration_required = Column(Boolean, default=False)
    special_requirements = Column(Text)
    
    status = Column(String(20), default="pending")  # pending, confirmed, completed, cancelled
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<EventBooking {self.booking_code}: {self.event_type}>"


class IntentLog(Base):
    """Log intent classification for training and improvement"""
    __tablename__ = "intent_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False, index=True)
    user_input = Column(Text, nullable=False)
    detected_intent = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    language = Column(String(10))
    actual_intent = Column(String(50))  # For manual correction/training
    is_correct = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<IntentLog {self.detected_intent}: {self.confidence}>"
