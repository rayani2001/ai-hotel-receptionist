"""
Language Detector
Automatically detects the language of user input
"""

from typing import Optional
from langdetect import detect, LangDetectException
from loguru import logger

from config.settings import settings


class LanguageDetector:
    """
    Detects language from user input
    Supports: English, Hindi, Tamil, Telugu, Kannada
    """
    
    # Language code mapping
    LANGUAGE_MAP = {
        "en": "English",
        "hi": "Hindi",
        "ta": "Tamil",
        "te": "Telugu",
        "kn": "Kannada",
        "ml": "Malayalam",
        "mr": "Marathi"
    }
    
    # Common phrases for identification
    LANGUAGE_INDICATORS = {
        "hi": ["नमस्ते", "धन्यवाद", "कमरा", "बुकिंग", "मुझे", "क्या", "है"],
        "ta": ["வணக்கம்", "நன்றி", "அறை", "பதிவு", "என்ன", "எப்படி"],
        "te": ["నమస్కారం", "ధన్యవాదాలు", "గది", "బుకింగ్", "ఏమిటి"],
        "kn": ["ನಮಸ್ಕಾರ", "ಧನ್ಯವಾದ", "ಕೋಣೆ", "ಬುಕಿಂಗ್"],
    }
    
    def __init__(self):
        logger.info("LanguageDetector initialized")
    
    def detect(self, text: str) -> str:
        """
        Detect language of input text
        
        Args:
            text: Input text to analyze
        
        Returns:
            Language code (e.g., 'en', 'hi', 'ta')
        """
        if not text or len(text.strip()) < 2:
            return "en"  # Default to English
        
        # First try pattern-based detection (more reliable for Indian languages)
        detected_lang = self._detect_by_patterns(text)
        if detected_lang:
            logger.debug(f"Pattern-based detection: {detected_lang}")
            return detected_lang
        
        # Fall back to langdetect library
        try:
            lang_code = detect(text)
            
            # Map to supported languages
            if lang_code in settings.SUPPORTED_LANGUAGES:
                logger.debug(f"Library detection: {lang_code}")
                return lang_code
            else:
                logger.warning(f"Detected unsupported language: {lang_code}, defaulting to English")
                return "en"
                
        except LangDetectException as e:
            logger.warning(f"Language detection failed: {e}, defaulting to English")
            return "en"
    
    def _detect_by_patterns(self, text: str) -> Optional[str]:
        """
        Detect language by checking for common phrases/characters
        More reliable for Indian languages
        """
        # Check for script-specific characters
        for lang_code, indicators in self.LANGUAGE_INDICATORS.items():
            for indicator in indicators:
                if indicator in text:
                    return lang_code
        
        # Check Unicode ranges for Indian scripts
        if self._contains_devanagari(text):
            return "hi"
        elif self._contains_tamil(text):
            return "ta"
        elif self._contains_telugu(text):
            return "te"
        elif self._contains_kannada(text):
            return "kn"
        
        return None
    
    def _contains_devanagari(self, text: str) -> bool:
        """Check if text contains Devanagari script (Hindi)"""
        return any('\u0900' <= char <= '\u097F' for char in text)
    
    def _contains_tamil(self, text: str) -> bool:
        """Check if text contains Tamil script"""
        return any('\u0B80' <= char <= '\u0BFF' for char in text)
    
    def _contains_telugu(self, text: str) -> bool:
        """Check if text contains Telugu script"""
        return any('\u0C00' <= char <= '\u0C7F' for char in text)
    
    def _contains_kannada(self, text: str) -> bool:
        """Check if text contains Kannada script"""
        return any('\u0C80' <= char <= '\u0CFF' for char in text)
    
    def get_language_name(self, lang_code: str) -> str:
        """
        Get full language name from code
        
        Args:
            lang_code: Language code (e.g., 'en')
        
        Returns:
            Full language name (e.g., 'English')
        """
        return self.LANGUAGE_MAP.get(lang_code, "English")
    
    def is_supported(self, lang_code: str) -> bool:
        """Check if language is supported"""
        return lang_code in settings.SUPPORTED_LANGUAGES
