"""
Entity Extractor
Extracts named entities from user messages (dates, names, phone numbers, etc.)
"""

from typing import Dict, Any, Optional, List
import re
from datetime import datetime, timedelta
from loguru import logger
import phonenumbers


class EntityExtractor:
    """
    Extracts entities using regex patterns and NLP
    Supports: names, phone numbers, dates, numbers, room types, etc.
    """
    
    # Regex patterns for entity extraction
    PATTERNS = {
        "phone_number": [
            r"\b\d{10}\b",  # 10 digit number
            r"\+?\d{1,3}[\s-]?\d{10}\b",  # With country code
            r"\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"  # Formatted
        ],
        "email": [
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        ],
        "date_patterns": [
            r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b",  # DD/MM/YYYY or MM/DD/YYYY
            r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b",  # YYYY-MM-DD
        ],
        "number": [
            r"\b\d+\b"
        ]
    }
    
    # Temporal expressions
    TEMPORAL_EXPRESSIONS = {
        "today": lambda: datetime.now(),
        "tomorrow": lambda: datetime.now() + timedelta(days=1),
        "day after tomorrow": lambda: datetime.now() + timedelta(days=2),
        "next week": lambda: datetime.now() + timedelta(weeks=1),
        "next month": lambda: datetime.now() + timedelta(days=30),
        "this weekend": lambda: datetime.now() + timedelta(days=(5 - datetime.now().weekday())),
    }
    
    # Room type keywords
    ROOM_TYPES = {
        "single": ["single", "solo", "one", "1"],
        "double": ["double", "two", "2", "couple"],
        "deluxe": ["deluxe", "luxury", "premium"],
        "suite": ["suite", "executive", "family"]
    }
    
    # Meal types
    MEAL_TYPES = ["breakfast", "lunch", "dinner"]
    
    # Hall sizes
    HALL_SIZES = {
        "small": ["small", "intimate", "50"],
        "medium": ["medium", "moderate", "150"],
        "large": ["large", "big", "grand", "300"]
    }
    
    def __init__(self):
        logger.info("EntityExtractor initialized")
    
    def extract(self, text: str, language: str = "en") -> Dict[str, Any]:
        """
        Extract all entities from text
        
        Args:
            text: Input text
            language: Language code
        
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        
        # Extract phone number
        phone = self._extract_phone(text)
        if phone:
            entities["phone_number"] = phone
        
        # Extract email
        email = self._extract_email(text)
        if email:
            entities["email"] = email
        
        # Extract dates
        date = self._extract_date(text)
        if date:
            # Determine if it's check-in or reservation date based on context
            if "check" in text.lower() or "book" in text.lower():
                entities["check_in_date"] = date
            elif "dining" in text.lower() or "dinner" in text.lower() or "lunch" in text.lower():
                entities["reservation_date"] = date
            elif "event" in text.lower() or "party" in text.lower():
                entities["event_date"] = date
        
        # Extract room type
        room_type = self._extract_room_type(text)
        if room_type:
            entities["room_type"] = room_type
        
        # Extract guest count
        guest_count = self._extract_guest_count(text)
        if guest_count:
            entities["guest_count"] = guest_count
        
        # Extract name (basic approach - can be enhanced)
        name = self._extract_name(text)
        if name:
            entities["guest_name"] = name
            entities["organizer_name"] = name  # Can be same for now
        
        # Extract meal type
        meal_type = self._extract_meal_type(text)
        if meal_type:
            entities["meal_type"] = meal_type
        
        # Extract hall type
        hall_type = self._extract_hall_type(text)
        if hall_type:
            entities["hall_type"] = hall_type
        
        # Extract duration (hours)
        duration = self._extract_duration(text)
        if duration:
            entities["duration"] = duration
        
        logger.debug(f"Extracted entities: {entities}")
        return entities
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number"""
        for pattern in self.PATTERNS["phone_number"]:
            match = re.search(pattern, text)
            if match:
                phone = match.group(0)
                # Validate using phonenumbers library
                try:
                    # Try parsing as Indian number
                    parsed = phonenumbers.parse(phone, "IN")
                    if phonenumbers.is_valid_number(parsed):
                        return phonenumbers.format_number(
                            parsed, 
                            phonenumbers.PhoneNumberFormat.E164
                        )
                except:
                    # Return as-is if parsing fails
                    return re.sub(r'\D', '', phone)  # Keep only digits
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address"""
        for pattern in self.PATTERNS["email"]:
            match = re.search(pattern, text)
            if match:
                return match.group(0).lower()
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text"""
        text_lower = text.lower()
        
        # Check for temporal expressions first
        for expression, date_func in self.TEMPORAL_EXPRESSIONS.items():
            if expression in text_lower:
                date_obj = date_func()
                return date_obj.strftime("%Y-%m-%d")
        
        # Check for explicit date patterns
        for pattern in self.PATTERNS["date_patterns"]:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(0)
                # Try to parse the date
                try:
                    # Try different formats
                    for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%m/%d/%Y"]:
                        try:
                            date_obj = datetime.strptime(date_str, fmt)
                            return date_obj.strftime("%Y-%m-%d")
                        except:
                            continue
                except:
                    pass
        
        return None
    
    def _extract_room_type(self, text: str) -> Optional[str]:
        """Extract room type"""
        text_lower = text.lower()
        
        for room_type, keywords in self.ROOM_TYPES.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return room_type
        
        return None
    
    def _extract_guest_count(self, text: str) -> Optional[int]:
        """Extract number of guests"""
        # Look for patterns like "2 people", "for 3 guests", "5 persons"
        patterns = [
            r"(\d+)\s*(people|persons?|guests?|pax)",
            r"for\s+(\d+)",
            r"(\d+)\s*(adult|person)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        
        # Look for standalone numbers in context
        if any(word in text.lower() for word in ["guest", "people", "person"]):
            numbers = re.findall(r'\b(\d+)\b', text)
            if numbers:
                return int(numbers[0])
        
        return None
    
    def _extract_name(self, text: str) -> Optional[str]:
        """
        Extract name from text
        Basic implementation - looks for capitalized words after "my name is", "I am", etc.
        """
        # Common name introduction patterns
        patterns = [
            r"(?:my name is|i am|this is|i'm)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"([A-Z][a-z]+\s+[A-Z][a-z]+)",  # Two capitalized words
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                # Validate it's not a common word
                if name.lower() not in ["yes", "no", "thank", "please", "hello"]:
                    return name
        
        return None
    
    def _extract_meal_type(self, text: str) -> Optional[str]:
        """Extract meal type"""
        text_lower = text.lower()
        
        for meal in self.MEAL_TYPES:
            if meal in text_lower:
                return meal
        
        return None
    
    def _extract_hall_type(self, text: str) -> Optional[str]:
        """Extract hall size type"""
        text_lower = text.lower()
        
        for hall_type, keywords in self.HALL_SIZES.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return hall_type
        
        return None
    
    def _extract_duration(self, text: str) -> Optional[int]:
        """Extract duration in hours"""
        patterns = [
            r"(\d+)\s*hours?",
            r"for\s+(\d+)\s*hours?",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return None
    
    def validate_entity(self, entity_type: str, value: Any) -> bool:
        """
        Validate extracted entity
        
        Args:
            entity_type: Type of entity
            value: Extracted value
        
        Returns:
            True if valid, False otherwise
        """
        if entity_type == "phone_number":
            # Check if it's 10 digits or more
            digits = re.sub(r'\D', '', str(value))
            return len(digits) >= 10
        
        elif entity_type == "email":
            # Basic email validation
            return re.match(r"[^@]+@[^@]+\.[^@]+", value) is not None
        
        elif entity_type in ["check_in_date", "check_out_date", "reservation_date", "event_date"]:
            # Check if date is in future
            try:
                date_obj = datetime.strptime(value, "%Y-%m-%d")
                return date_obj >= datetime.now()
            except:
                return False
        
        elif entity_type == "guest_count":
            # Check reasonable range
            return 1 <= int(value) <= 100
        
        elif entity_type == "duration":
            # Check reasonable hours
            return 1 <= int(value) <= 24
        
        return True
