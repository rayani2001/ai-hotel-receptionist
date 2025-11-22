"""
Intent Classifier
Uses pattern matching and AI to classify user intents
"""

from typing import Dict, List, Tuple
import re
from loguru import logger
import openai
from anthropic import Anthropic

from config.settings import settings


class IntentClassifier:
    """
    Classifies user intents using hybrid approach:
    1. Rule-based pattern matching for common intents
    2. AI-based classification for complex cases
    """
    
    # Intent patterns for quick classification
    INTENT_PATTERNS = {
        "greeting": [
            r"\b(hello|hi|hey|good\s+(morning|afternoon|evening)|namaste|vanakkam)\b",
            r"\b(नमस्ते|हॅलो)\b",
            r"\b(வணக்கம்|ஹலோ)\b",
        ],
        "room_booking": [
            r"\b(book|reserve|want|need)\s+(a\s+)?(room|accommodation)\b",
            r"\b(room|कमरा|அறை)\s+(booking|बुकिंग|பதிவு)\b",
            r"\b(check\s+in|stay)\b",
        ],
        "room_inquiry": [
            r"\b(available|availability)\s+(room|कमरा)\b",
            r"\b(room\s+)?(types|price|rate|cost)\b",
            r"\b(what|which|how much)\s+(rooms|room)\b",
        ],
        "dining_reservation": [
            r"\b(dining|dinner|lunch|breakfast|restaurant)\s+(reservation|booking)\b",
            r"\b(table|reserve|book)\s+(for\s+)?(dinner|lunch|breakfast)\b",
            r"\b(भोजन|खाना)\s+(बुकिंग)\b",
        ],
        "event_booking": [
            r"\b(party\s+hall|event\s+hall|conference\s+room|banquet)\b",
            r"\b(book|rent|need)\s+(hall|venue)\b",
            r"\b(wedding|birthday|corporate)\s+(event|party)\b",
        ],
        "information_request": [
            r"\b(tell\s+me|information|details|know)\s+(about)\b",
            r"\b(what|where|when|how)\s+(is|are|do|does)\b",
            r"\b(amenities|facilities|services)\b",
            r"\b(check\s+in|check\s+out)\s+(time|timing)\b",
        ],
        "booking_modification": [
            r"\b(change|modify|cancel|update)\s+(my\s+)?(booking|reservation)\b",
            r"\b(reschedule|postpone)\b",
        ],
        "complaint": [
            r"\b(complaint|problem|issue|not\s+happy|disappointed|terrible|bad)\b",
            r"\b(शिकायत|समस्या)\b",
        ],
        "farewell": [
            r"\b(bye|goodbye|thanks|thank\s+you|धन्यवाद)\b",
        ]
    }
    
    def __init__(self):
        self.use_ai = settings.AI_PROVIDER in ["openai", "anthropic"]
        
        if self.use_ai:
            if settings.AI_PROVIDER == "openai" and settings.OPENAI_API_KEY:
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("Intent classifier initialized with OpenAI")
            elif settings.AI_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
                self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                logger.info("Intent classifier initialized with Anthropic")
            else:
                logger.warning("AI provider configured but API key missing, falling back to rule-based")
                self.use_ai = False
        else:
            logger.info("Intent classifier initialized with rule-based only")
    
    def classify(self, text: str, language: str = "en") -> Dict[str, any]:
        """
        Classify intent of user message
        
        Args:
            text: User's input text
            language: Detected language
        
        Returns:
            Dict with intent and confidence score
        """
        text_lower = text.lower()
        
        # Try rule-based classification first
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    logger.debug(f"Rule-based match: {intent}")
                    return {
                        "intent": intent,
                        "confidence": 0.95,
                        "method": "rule-based"
                    }
        
        # Fall back to AI-based classification if available
        if self.use_ai:
            return self._classify_with_ai(text, language)
        
        # Default to information_request if no match
        return {
            "intent": "information_request",
            "confidence": 0.5,
            "method": "fallback"
        }
    
    def _classify_with_ai(self, text: str, language: str) -> Dict[str, any]:
        """Use AI to classify intent"""
        
        prompt = f"""Classify the intent of this hotel guest message. 

Message: "{text}"
Language: {language}

Possible intents:
- greeting: Initial greetings
- room_booking: Want to book a room
- room_inquiry: Asking about room types, prices, availability
- dining_reservation: Restaurant/dining reservations
- event_booking: Party hall or event space booking
- information_request: General questions about hotel
- booking_modification: Change or cancel existing booking
- complaint: Service complaints or issues
- farewell: Goodbye, thanks

Respond ONLY with a JSON object in this format:
{{"intent": "intent_name", "confidence": 0.95}}"""
        
        try:
            if settings.AI_PROVIDER == "openai":
                response = self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an intent classifier for a hotel receptionist AI."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=100
                )
                
                content = response.choices[0].message.content
                
            elif settings.AI_PROVIDER == "anthropic":
                response = self.anthropic_client.messages.create(
                    model=settings.ANTHROPIC_MODEL,
                    max_tokens=100,
                    temperature=0.3,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                content = response.content[0].text
            
            # Parse JSON response
            import json
            result = json.loads(content.strip())
            result["method"] = "ai-based"
            
            logger.debug(f"AI classification: {result}")
            return result
            
        except Exception as e:
            logger.error(f"AI classification error: {e}")
            return {
                "intent": "information_request",
                "confidence": 0.5,
                "method": "error_fallback"
            }
    
    def get_all_intents(self) -> List[str]:
        """Return list of all supported intents"""
        return list(self.INTENT_PATTERNS.keys())
