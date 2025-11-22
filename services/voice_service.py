"""
Voice Service
Handles speech-to-text and text-to-speech processing
"""

from typing import Optional
import base64
from io import BytesIO
from loguru import logger
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment

from config.settings import settings


class VoiceService:
    """Service class for voice processing"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        logger.info("VoiceService initialized")
    
    def speech_to_text(
        self,
        audio_base64: str,
        language: str = "en-IN"
    ) -> Optional[str]:
        """
        Convert speech to text
        
        Args:
            audio_base64: Base64 encoded audio data
            language: Language code for recognition
        
        Returns:
            Transcribed text or None if failed
        """
        try:
            # Decode base64 audio
            audio_data = base64.b64decode(audio_base64)
            
            # Convert to AudioSegment
            audio = AudioSegment.from_file(BytesIO(audio_data))
            
            # Export as WAV
            wav_io = BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)
            
            # Recognize speech
            with sr.AudioFile(wav_io) as source:
                audio_data = self.recognizer.record(source)
                
                try:
                    # Try Google Speech Recognition
                    text = self.recognizer.recognize_google(
                        audio_data,
                        language=language
                    )
                    logger.success(f"Transcribed: {text}")
                    return text
                    
                except sr.UnknownValueError:
                    logger.warning("Could not understand audio")
                    return None
                    
                except sr.RequestError as e:
                    logger.error(f"Speech recognition error: {e}")
                    return None
                    
        except Exception as e:
            logger.error(f"Speech-to-text error: {e}")
            return None
    
    def text_to_speech(
        self,
        text: str,
        language: str = "en"
    ) -> str:
        """
        Convert text to speech
        
        Args:
            text: Text to convert
            language: Language code
        
        Returns:
            Base64 encoded audio data
        """
        try:
            # Map language codes for gTTS
            lang_map = {
                "en": "en",
                "hi": "hi",
                "ta": "ta",
                "te": "te",
                "kn": "kn"
            }
            
            gtts_lang = lang_map.get(language, "en")
            
            # Generate speech
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            
            # Save to BytesIO
            audio_io = BytesIO()
            tts.write_to_fp(audio_io)
            audio_io.seek(0)
            
            # Encode to base64
            audio_base64 = base64.b64encode(audio_io.read()).decode('utf-8')
            
            logger.success("Text-to-speech generated")
            return audio_base64
            
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
            raise
    
    def process_audio_file(
        self,
        file_path: str,
        language: str = "en-IN"
    ) -> Optional[str]:
        """
        Process audio file and return transcription
        
        Args:
            file_path: Path to audio file
            language: Language for recognition
        
        Returns:
            Transcribed text
        """
        try:
            with sr.AudioFile(file_path) as source:
                audio_data = self.recognizer.record(source)
                
                text = self.recognizer.recognize_google(
                    audio_data,
                    language=language
                )
                
                return text
                
        except Exception as e:
            logger.error(f"Audio file processing error: {e}")
            return None
