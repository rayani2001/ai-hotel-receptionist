"""
Dialogue Manager for AI Hotel Receptionist
Handles conversation flow and intent recognition
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from loguru import logger
import json

from models.intent_classifier import IntentClassifier
from models.entity_extractor import EntityExtractor
from models.language_detector import LanguageDetector
from config.settings import settings


@dataclass
class DialogueState:
    """Maintains the state of an ongoing conversation"""
    
    conversation_id: str
    session_id: str
    language: str = "en"
    primary_intent: Optional[str] = None
    sub_intents: List[str] = field(default_factory=list)
    
    # Slot filling
    collected_entities: Dict[str, Any] = field(default_factory=dict)
    missing_slots: List[str] = field(default_factory=list)
    
    # Context
    conversation_history: List[Dict] = field(default_factory=list)
    turn_count: int = 0
    
    # State flags
    confirmation_pending: bool = False
    booking_confirmed: bool = False
    escalation_required: bool = False
    
    # Sentiment tracking
    sentiment_scores: List[float] = field(default_factory=list)
    
    def add_turn(self, user_message: str, agent_response: str, detected_intent: str):
        """Add a conversation turn to history"""
        self.conversation_history.append({
            "turn": self.turn_count,
            "user": user_message,
            "agent": agent_response,
            "intent": detected_intent,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.turn_count += 1
    
    def get_context_summary(self) -> str:
        """Generate a summary of the conversation context"""
        summary = f"Language: {self.language}\n"
        summary += f"Intent: {self.primary_intent}\n"
        summary += f"Entities collected: {json.dumps(self.collected_entities, indent=2)}\n"
        summary += f"Turn count: {self.turn_count}\n"
        return summary


class DialogueManager:
    def __init__(self):
        self.sessions = {}
        self.hotel_knowledge = self._initialize_hotel_knowledge()
        self.language_responses = self._initialize_language_responses()
        
        logger.info("DialogueManager initialized")
    
    def _initialize_hotel_knowledge(self) -> Dict:
        """Initialize comprehensive hotel knowledge base"""
        return {
            "room_types": {
                "standard": {
                    "price": 2000,
                    "capacity": 2,
                    "amenities": ["WiFi", "TV", "AC", "Mini Bar"],
                    "size": "250 sq ft"
                },
                "deluxe": {
                    "price": 3500,
                    "capacity": 3,
                    "amenities": ["WiFi", "Smart TV", "AC", "Mini Bar", "Balcony"],
                    "size": "400 sq ft"
                },
                "suite": {
                    "price": 6000,
                    "capacity": 4,
                    "amenities": ["WiFi", "Smart TV", "AC", "Mini Bar", "Balcony", "Kitchenette", "Living Room"],
                    "size": "650 sq ft"
                }
            },
            "amenities": [
                "Free WiFi throughout the hotel",
                "Swimming Pool (6 AM - 10 PM)",
                "Fitness Center (24/7)",
                "Restaurant & Bar",
                "Room Service (24/7)",
                "Spa & Wellness Center",
                "Business Center",
                "Free Parking",
                "Airport Shuttle Service",
                "Laundry Service"
            ],
            "check_in_time": "2:00 PM",
            "check_out_time": "11:00 AM",
            "cancellation_policy": "Free cancellation up to 24 hours before check-in",
            "payment_methods": ["Cash", "Credit Card", "Debit Card", "UPI", "Net Banking"],
            "pet_policy": "Pets allowed with additional charge of ₹500 per night",
            "breakfast_timing": "7:00 AM - 10:30 AM",
            "restaurant_timing": "12:00 PM - 11:00 PM"
        }
    
    def _initialize_language_responses(self) -> Dict:
        """Initialize responses in multiple languages"""
        return {
            "en": {
                "greeting": "Welcome to our hotel! How may I assist you today?",
                "room_types": "We offer Standard (₹2000), Deluxe (₹3500), and Suite (₹6000) rooms.",
                "amenities": "Our amenities include: Free WiFi, Swimming Pool, Fitness Center, Restaurant, Spa, and more!",
                "check_in": "Check-in time is 2:00 PM and check-out time is 11:00 AM.",
                "booking_help": "I can help you book a room. Please provide: check-in date, check-out date, room type, and number of guests.",
                "cancellation": "Free cancellation up to 24 hours before check-in.",
                "breakfast": "Breakfast is served from 7:00 AM to 10:30 AM.",
                "pets": "Yes, pets are allowed with an additional charge of ₹500 per night.",
                "parking": "Yes, we provide free parking for our guests.",
                "wifi": "Yes, free high-speed WiFi is available throughout the hotel.",
                "room_availability": "Let me check availability for you. Which dates are you looking at? And which room type would you prefer - Standard, Deluxe, or Suite?",
                "price_standard": "Our Standard room is ₹2000 per night. It includes WiFi, TV, AC, and Mini Bar.",
                "price_deluxe": "Our Deluxe room is ₹3500 per night. It includes all Standard amenities plus a Balcony and Smart TV.",
                "price_suite": "Our Suite is ₹6000 per night. It includes all Deluxe amenities plus a Kitchenette and Living Room.",
                "modify_booking": "I can help modify your booking. Please provide your booking reference number and what changes you'd like to make.",
                "cancel_booking": "I can help cancel your booking. Please provide your booking reference number. Note: Free cancellation is available up to 24 hours before check-in.",
                "room_features": "All our rooms include: Air Conditioning, Free WiFi, Flat-screen TV, Mini Bar, and Daily Housekeeping. Would you like details about a specific room type?",
                "early_checkin": "Early check-in is subject to availability. Please let us know your arrival time and we'll do our best to accommodate you. There may be an additional charge.",
                "late_checkout": "Late check-out is available upon request, subject to availability. There may be an additional charge depending on how late you need.",
                "group_booking": "For group bookings of 5+ rooms, we offer special rates! Please provide: number of rooms needed, check-in/out dates, and guest count.",
                "long_stay": "We offer special discounts for stays of 7+ nights! Please share your dates and I'll provide you with our long-stay rates.",
                "payment_options": "We accept: Cash, Credit Card, Debit Card, UPI, and Net Banking. Payment can be made at check-in or we can send a payment link for advance booking.",
                "deposit_required": "For confirmed bookings, we require 30% advance payment. The remaining 70% can be paid at check-in.",
                "extra_bed": "Extra beds are available at ₹800 per night. Maximum 1 extra bed can be added to Deluxe rooms and Suites.",
                "child_policy": "Children under 5 stay free. Children aged 5-12 are charged 50% of the room rate when using existing bedding.",
                "room_size": "Standard: 250 sq ft, Deluxe: 400 sq ft, Suite: 650 sq ft. Would you like to know about specific room features?",
                "nearest_attractions": "We're located near popular attractions: City Mall (2 km), Beach (5 km), Airport (15 km), Railway Station (3 km).",
                "airport_transfer": "Yes, we provide airport shuttle service at ₹500 per trip. Please inform us of your flight details in advance.",
                "special_occasion": "We'd love to make your special occasion memorable! We offer: Birthday decorations (₹1500), Anniversary packages (₹2500), and Honeymoon packages (₹3500).",
                "conference_rooms": "We have conference rooms available for business meetings. Rates start at ₹2000 for 4 hours. Includes projector, WiFi, and refreshments.",
                "loyalty_program": "Join our loyalty program! Earn points on every stay and get exclusive discounts, free upgrades, and special offers.",
                "covid_safety": "We follow strict COVID-19 safety protocols: Regular sanitization, contactless check-in/out, staff vaccination, and social distancing measures.",
                "complaint": "I sincerely apologize for any inconvenience. Please share the details and I'll ensure our team addresses your concern immediately. You can also speak to our manager."
            },
            "lv": {
                "greeting": "Laipni lūdzam mūsu viesnīcā! Kā es varu jums palīdzēt?",
                "room_types": "Mēs piedāvājam Standarta (₹2000), Deluxe (₹3500) un Suite (₹6000) istabas.",
                "amenities": "Mūsu ērtības ietver: bezmaksas WiFi, baseinu, fitnesa centru, restorānu, spa un vēl!",
                "check_in": "Reģistrēšanās laiks ir 14:00, un izrakstīšanās laiks ir 11:00.",
                "booking_help": "Es varu palīdzēt jums rezervēt istabu. Lūdzu, norādiet: ierašanās datumu, izbraukšanas datumu, istabas tipu un viesu skaitu.",
                "cancellation": "Bezmaksas atcelšana līdz 24 stundām pirms iebraukšanas.",
                "room_availability": "Ļaujiet man pārbaudīt pieejamību. Kādus datumus jūs meklējat? Un kādu istabas tipu vēlaties?",
                "price_standard": "Mūsu Standarta istaba ir ₹2000 par nakti.",
                "price_deluxe": "Mūsu Deluxe istaba ir ₹3500 par nakti.",
                "price_suite": "Mūsu Suite ir ₹6000 par nakti.",
                "payment_options": "Mēs pieņemam: skaidru naudu, kredītkarti, debetkarti, UPI un interneta banku."
            },
            "ru": {
                "greeting": "Добро пожаловать в наш отель! Чем я могу вам помочь?",
                "room_types": "Мы предлагаем номера Стандарт (₹2000), Делюкс (₹3500) и Люкс (₹6000).",
                "amenities": "Наши удобства включают: бесплатный WiFi, бассейн, фитнес-центр, ресторан, спа и многое другое!",
                "check_in": "Время заезда 14:00, время выезда 11:00.",
                "booking_help": "Я могу помочь вам забронировать номер. Пожалуйста, укажите: дату заезда, дату выезда, тип номера и количество гостей.",
                "cancellation": "Бесплатная отмена за 24 часа до заезда.",
                "room_availability": "Позвольте мне проверить наличие. На какие даты вы смотрите? И какой тип номера вы предпочитаете?",
                "price_standard": "Наш номер Стандарт стоит ₹2000 за ночь.",
                "price_deluxe": "Наш номер Делюкс стоит ₹3500 за ночь.",
                "price_suite": "Наш номер Люкс стоит ₹6000 за ночь.",
                "payment_options": "Мы принимаем: наличные, кредитные карты, дебетовые карты, UPI и интернет-банкинг."
            },
            "hi": {
                "greeting": "हमारे होटल में आपका स्वागत है! मैं आपकी कैसे सहायता कर सकता हूं?",
                "room_types": "हम स्टैंडर्ड (₹2000), डीलक्स (₹3500) और सूट (₹6000) कमरे प्रदान करते हैं।",
                "amenities": "हमारी सुविधाओं में शामिल हैं: मुफ्त WiFi, स्विमिंग पूल, फिटनेस सेंटर, रेस्तरां, स्पा और बहुत कुछ!",
                "check_in": "चेक-इन का समय दोपहर 2:00 बजे और चेक-आउट का समय सुबह 11:00 बजे है।",
                "booking_help": "मैं आपको एक कमरा बुक करने में मदद कर सकता हूं। कृपया प्रदान करें: चेक-इन तिथि, चेक-आउट तिथि, कमरे का प्रकार और मेहमानों की संख्या।",
                "cancellation": "चेक-इन से 24 घंटे पहले तक मुफ्त रद्दीकरण।",
                "room_availability": "मैं आपके लिए उपलब्धता जांचता हूं। आप कौन सी तारीखें देख रहे हैं? और आप कौन सा कमरा पसंद करेंगे?",
                "price_standard": "हमारा स्टैंडर्ड कमरा ₹2000 प्रति रात है।",
                "price_deluxe": "हमारा डीलक्स कमरा ₹3500 प्रति रात है।",
                "price_suite": "हमारा सूट ₹6000 प्रति रात है।",
                "payment_options": "हम स्वीकार करते हैं: नकद, क्रेडिट कार्ड, डेबिट कार्ड, UPI और नेट बैंकिंग।"
            },
            "si": {  # Sinhala
                "greeting": "අපගේ හෝටලයට ඔබව සාදරයෙන් පිළිගනිමු! මම ඔබට අද කෙසේ සහාය විය හැකිද?",
                "room_types": "අපි සම්මත (₹2000), ඩිලක්ස් (₹3500), සහ සූට් (₹6000) කාමර ලබා දෙමු.",
                "amenities": "අපගේ පහසුකම් ඇතුළත් වන්නේ: නොමිලේ WiFi, පිහිනුම් තටාකය, යෝග්‍යතා මධ්‍යස්ථානය, අවන්හල, ස්පා සහ තවත් බොහෝ දේ!",
                "check_in": "පිවිසීමේ කාලය පස්වරු 2:00 සහ පිටවීමේ කාලය පෙ.ව. 11:00 වේ.",
                "booking_help": "මට ඔබට කාමරයක් වෙන්කරවා ගැනීමට උදව් කළ හැකිය. කරුණාකර සපයන්න: පිවිසුම් දිනය, පිටවීමේ දිනය, කාමර වර්ගය සහ අමුත්තන් සංඛ්‍යාව.",
                "cancellation": "පිවිසීමට පැය 24කට පෙර නොමිලේ අවලංගු කිරීම.",
                "breakfast": "උදෑසන ආහාරය පෙ.ව. 7:00 සිට 10:30 දක්වා සේවය කරනු ලැබේ.",
                "pets": "ඔව්, සුරතල් සතුන්ට රාත්‍රියකට ₹500 අතිරේක ගාස්තුවක් සමඟ අවසර ඇත.",
                "parking": "ඔව්, අපි අපගේ අමුත්තන් සඳහා නොමිලේ වාහන නැවැත්වීමේ පහසුකම් සපයන්නෙමු.",
                "wifi": "ඔව්, නොමිලේ අධිවේගී WiFi මුළු හෝටලය පුරා තිබේ."
            },
            "fr": {  # French
                "greeting": "Bienvenue dans notre hôtel! Comment puis-je vous aider aujourd'hui?",
                "room_types": "Nous proposons des chambres Standard (₹2000), Deluxe (₹3500) et Suite (₹6000).",
                "amenities": "Nos équipements comprennent: WiFi gratuit, piscine, centre de fitness, restaurant, spa et plus encore!",
                "check_in": "L'enregistrement est à 14h00 et le départ à 11h00.",
                "booking_help": "Je peux vous aider à réserver une chambre. Veuillez fournir: date d'arrivée, date de départ, type de chambre et nombre d'invités.",
                "cancellation": "Annulation gratuite jusqu'à 24 heures avant l'arrivée.",
                "breakfast": "Le petit-déjeuner est servi de 7h00 à 10h30.",
                "pets": "Oui, les animaux sont acceptés moyennant un supplément de ₹500 par nuit.",
                "parking": "Oui, nous offrons un parking gratuit à nos clients.",
                "wifi": "Oui, le WiFi haut débit gratuit est disponible dans tout l'hôtel."
            },
            "it": {  # Italian
                "greeting": "Benvenuti nel nostro hotel! Come posso aiutarla oggi?",
                "room_types": "Offriamo camere Standard (₹2000), Deluxe (₹3500) e Suite (₹6000).",
                "amenities": "I nostri servizi includono: WiFi gratuito, piscina, centro fitness, ristorante, spa e altro ancora!",
                "check_in": "Il check-in è alle 14:00 e il check-out alle 11:00.",
                "booking_help": "Posso aiutarla a prenotare una camera. Fornisca: data di check-in, data di check-out, tipo di camera e numero di ospiti.",
                "cancellation": "Cancellazione gratuita fino a 24 ore prima del check-in.",
                "breakfast": "La colazione viene servita dalle 7:00 alle 10:30.",
                "pets": "Sì, gli animali domestici sono ammessi con un supplemento di ₹500 a notte.",
                "parking": "Sì, forniamo parcheggio gratuito per i nostri ospiti.",
                "wifi": "Sì, WiFi ad alta velocità gratuito è disponibile in tutto l'hotel."
            },
            "de": {  # German
                "greeting": "Willkommen in unserem Hotel! Wie kann ich Ihnen heute helfen?",
                "room_types": "Wir bieten Standard (₹2000), Deluxe (₹3500) und Suite (₹6000) Zimmer an.",
                "amenities": "Unsere Annehmlichkeiten umfassen: Kostenloses WLAN, Schwimmbad, Fitnesscenter, Restaurant, Spa und mehr!",
                "check_in": "Check-in ist um 14:00 Uhr und Check-out um 11:00 Uhr.",
                "booking_help": "Ich kann Ihnen helfen, ein Zimmer zu buchen. Bitte geben Sie an: Check-in-Datum, Check-out-Datum, Zimmertyp und Anzahl der Gäste.",
                "cancellation": "Kostenlose Stornierung bis 24 Stunden vor dem Check-in.",
                "breakfast": "Das Frühstück wird von 7:00 bis 10:30 Uhr serviert.",
                "pets": "Ja, Haustiere sind gegen einen Aufpreis von ₹500 pro Nacht erlaubt.",
                "parking": "Ja, wir bieten unseren Gästen kostenlose Parkplätze.",
                "wifi": "Ja, kostenloses Highspeed-WLAN ist im gesamten Hotel verfügbar."
            },
            "es": {  # Spanish
                "greeting": "¡Bienvenido a nuestro hotel! ¿Cómo puedo ayudarle hoy?",
                "room_types": "Ofrecemos habitaciones Estándar (₹2000), Deluxe (₹3500) y Suite (₹6000).",
                "amenities": "Nuestras comodidades incluyen: WiFi gratis, piscina, gimnasio, restaurante, spa ¡y más!",
                "check_in": "El check-in es a las 14:00 y el check-out a las 11:00.",
                "booking_help": "Puedo ayudarle a reservar una habitación. Por favor proporcione: fecha de entrada, fecha de salida, tipo de habitación y número de huéspedes.",
                "cancellation": "Cancelación gratuita hasta 24 horas antes del check-in.",
                "breakfast": "El desayuno se sirve de 7:00 a 10:30.",
                "pets": "Sí, se permiten mascotas con un cargo adicional de ₹500 por noche.",
                "parking": "Sí, ofrecemos estacionamiento gratuito para nuestros huéspedes.",
                "wifi": "Sí, WiFi de alta velocidad gratuito está disponible en todo el hotel."
            }
        }
    
    def detect_language(self, text: str) -> str:
        """Detect language from text (simple keyword-based detection)"""
        language_keywords = {
            "lv": ["laipni", "jums", "palīdzēt", "viesnīca"],
            "ru": ["привет", "помощь", "отель", "номер"],
            "hi": ["नमस्ते", "होटल", "कमरा", "मदद"],
            "si": ["හෝටලය", "කාමරය", "සහාය"],
            "fr": ["bonjour", "hôtel", "chambre", "aide"],
            "it": ["ciao", "hotel", "camera", "aiuto"],
            "de": ["hotel", "zimmer", "hilfe", "hallo"],
            "es": ["hola", "hotel", "habitación", "ayuda"]
        }
        
        text_lower = text.lower()
        for lang, keywords in language_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return lang
        return "en"  # Default to English
    
    def detect_intent(self, message: str, language: str) -> Dict:
        """Detect user intent from message"""
        message_lower = message.lower()
        
        # Enhanced intent patterns with more booking scenarios
        intents = {
            "greeting": ["hello", "hi", "hey", "good morning", "good evening", "greetings", "привет", "हैलो", "hola", "bonjour"],
            "room_inquiry": ["room", "rooms", "room types", "what rooms", "types of rooms", "room categories", "номер", "कमरा", "habitación"],
            "price_inquiry": ["price", "cost", "how much", "rate", "pricing", "charges", "tariff", "fees", "цена", "कीमत", "precio"],
            "room_availability": ["available", "availability", "vacant", "free rooms", "check availability", "any rooms", "доступность"],
            "amenities": ["amenities", "facilities", "services", "features", "what do you have", "what's included", "удобства", "सुविधाएं"],
            "check_in_out": ["check in", "check out", "timing", "time", "what time", "when can i", "заезд", "выезд"],
            "booking": ["book", "reserve", "reservation", "i want to book", "make a booking", "бронировать", "बुक"],
            "cancellation": ["cancel", "cancellation policy", "cancel booking", "refund", "отмена", "रद्द"],
            "modify_booking": ["change", "modify", "reschedule", "update booking", "change dates", "edit booking", "изменить"],
            "breakfast": ["breakfast", "food", "dining", "meal", "завтрак", "नाश्ता"],
            "pets": ["pet", "dog", "cat", "animal", "bring pet", "питомец", "पालतू"],
            "parking": ["parking", "park", "car", "vehicle", "парковка", "पार्किंग"],
            "wifi": ["wifi", "internet", "connection", "интернет", "वाईफाई"],
            "payment": ["payment", "pay", "how to pay", "payment method", "deposit", "advance", "оплата", "भुगतान"],
            "extra_bed": ["extra bed", "additional bed", "cot", "rollaway", "дополнительная кровать", "अतिरिक्त बिस्तर"],
            "child_policy": ["child", "kids", "children", "baby", "infant", "дети", "बच्चे"],
            "early_checkin": ["early check in", "arrive early", "before 2 pm", "ранний заезд"],
            "late_checkout": ["late check out", "extend stay", "later checkout", "поздний выезд"],
            "group_booking": ["group", "multiple rooms", "bulk booking", "5 rooms", "групповое бронирование"],
            "long_stay": ["long stay", "extended stay", "weekly", "monthly", "многодневное пребывание"],
            "room_features": ["room features", "what's in the room", "room details", "facilities in room"],
            "location": ["location", "where", "address", "nearby", "attractions", "местоположение"],
            "airport_transfer": ["airport", "pickup", "drop", "shuttle", "transfer", "транспорт"],
            "special_occasion": ["birthday", "anniversary", "honeymoon", "celebration", "special occasion"],
            "complaint": ["complaint", "problem", "issue", "not happy", "disappointed", "жалоба"],
            "discount": ["discount", "offer", "deal", "promotion", "coupon", "скидка", "छूट"]
        }
        
        detected_intent = "general_inquiry"
        confidence = 0.5
        max_matches = 0
        
        # Count keyword matches for better accuracy
        for intent, keywords in intents.items():
            matches = sum(1 for keyword in keywords if keyword in message_lower)
            if matches > max_matches:
                max_matches = matches
                detected_intent = intent
                confidence = min(0.95, 0.7 + (matches * 0.1))
        
        return {
            "intent": detected_intent,
            "confidence": confidence
        }
    
    def generate_response(self, intent: str, language: str) -> str:
        """Generate response based on intent and language"""
        responses = self.language_responses.get(language, self.language_responses["en"])
        
        response_map = {
            "greeting": responses["greeting"],
            "room_inquiry": responses["room_types"],
            "price_inquiry": responses.get("price_standard", responses["room_types"]) + "\n" + responses.get("price_deluxe", "") + "\n" + responses.get("price_suite", ""),
            "room_availability": responses.get("room_availability", responses["booking_help"]),
            "amenities": responses["amenities"],
            "check_in_out": responses["check_in"],
            "booking": responses["booking_help"],
            "cancellation": responses["cancellation"],
            "modify_booking": responses.get("modify_booking", responses["booking_help"]),
            "breakfast": responses.get("breakfast", responses["amenities"]),
            "pets": responses.get("pets", responses["amenities"]),
            "parking": responses.get("parking", responses["amenities"]),
            "wifi": responses.get("wifi", responses["amenities"]),
            "payment": responses.get("payment_options", responses["booking_help"]),
            "extra_bed": responses.get("extra_bed", responses["booking_help"]),
            "child_policy": responses.get("child_policy", responses["booking_help"]),
            "early_checkin": responses.get("early_checkin", responses["check_in"]),
            "late_checkout": responses.get("late_checkout", responses["check_in"]),
            "group_booking": responses.get("group_booking", responses["booking_help"]),
            "long_stay": responses.get("long_stay", responses["booking_help"]),
            "room_features": responses.get("room_features", responses["room_types"]),
            "location": responses.get("nearest_attractions", responses["greeting"]),
            "airport_transfer": responses.get("airport_transfer", responses["amenities"]),
            "special_occasion": responses.get("special_occasion", responses["booking_help"]),
            "complaint": responses.get("complaint", "I apologize for any inconvenience. How can I help resolve this?"),
            "discount": responses.get("loyalty_program", responses["booking_help"]),
            "general_inquiry": responses["greeting"]
        }
        
        return response_map.get(intent, responses["greeting"])
    
    def process_message(self, user_message: str, session_id: str) -> Dict:
        """Process user message and generate response"""
        # Detect language
        language = self.detect_language(user_message)
        
        # Detect intent
        intent_data = self.detect_intent(user_message, language)
        
        # Generate response
        response_message = self.generate_response(intent_data["intent"], language)
        
        # Update session
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "turn_count": 0,
                "language": language,
                "history": []
            }
        
        self.sessions[session_id]["turn_count"] += 1
        self.sessions[session_id]["history"].append({
            "user": user_message,
            "agent": response_message,
            "intent": intent_data["intent"],
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "message": response_message,
            "intent": intent_data["intent"],
            "confidence": intent_data["confidence"],
            "language": language,
            "session_id": session_id,
            "turn_count": self.sessions[session_id]["turn_count"],
            "state": "active",
            "missing_slots": []
        }
    
    def clear_session(self, session_id: str):
        """Clear a conversation session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Session {session_id} cleared")
