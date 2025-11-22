"""
API Routes for AI Hotel Receptionist
Handles all HTTP endpoints for the application
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from datetime import datetime
from loguru import logger
import io
import base64

from database.database import get_db
from database.models import Conversation, Booking, Guest, Room
from models.dialogue_manager import DialogueManager
from services.booking_service import BookingService
from services.room_service import RoomService
from services.voice_service import VoiceService
from config.settings import settings

# Initialize router
router = APIRouter()

# Initialize services
dialogue_manager = DialogueManager()
booking_service = BookingService()
room_service = RoomService()
voice_service = VoiceService()

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message")
    session_id: Optional[str] = Field(None, description="Session ID for continuing conversation")
    
class ChatResponse(BaseModel):
    message: str
    intent: str
    confidence: float
    language: str
    session_id: str
    turn_count: int
    state: str
    missing_slots: List[str]

class VoiceInputRequest(BaseModel):
    audio_base64: str = Field(..., description="Base64 encoded audio data")
    session_id: Optional[str] = None

class BookingCreateRequest(BaseModel):
    guest_name: str
    phone: str
    email: Optional[str] = None
    check_in_date: str
    check_out_date: str
    room_type: str
    guest_count: int
    special_requests: Optional[str] = None


# ==================== CHAT ENDPOINTS ====================

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Main chat endpoint for text-based conversation
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"Chat request - Session: {session_id}, Message: {request.message}")
        
        # Process message through dialogue manager
        response = dialogue_manager.process_message(
            user_message=request.message,
            session_id=session_id
        )
        
        # Log conversation to database
        conversation = Conversation(
            id=str(uuid.uuid4()),
            session_id=session_id,
            user_message=request.message,
            agent_response=response["message"],
            detected_language=response.get("language", "en"),
            detected_intent=response.get("intent"),
            confidence_score=response.get("confidence"),
            extracted_entities=response.get("entities", {}),
            timestamp=datetime.utcnow()
        )
        db.add(conversation)
        db.commit()
        
        logger.success(f"Chat response generated - Intent: {response['intent']}")
        
        return ChatResponse(
            message=response["message"],
            intent=response["intent"],
            confidence=response["confidence"],
            language=response["language"],
            session_id=session_id,
            turn_count=response["turn_count"],
            state=response["state"],
            missing_slots=response.get("missing_slots", [])
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/chat-ui", response_class=HTMLResponse)
async def chat_ui():
    """Web-based chat interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Hotel Receptionist - Chat</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .chat-container {
                width: 90%;
                max-width: 800px;
                height: 90vh;
                background: white;
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                display: flex;
                flex-direction: column;
            }
            .chat-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 20px 20px 0 0;
                text-align: center;
            }
            .quick-questions {
                padding: 10px 20px;
                background: #f0f0f0;
                border-bottom: 1px solid #ddd;
                overflow-x: auto;
                white-space: nowrap;
            }
            .quick-question {
                display: inline-block;
                padding: 8px 15px;
                margin: 5px;
                background: white;
                border: 1px solid #667eea;
                border-radius: 20px;
                cursor: pointer;
                font-size: 12px;
                transition: all 0.3s;
            }
            .quick-question:hover {
                background: #667eea;
                color: white;
            }
            .chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .message {
                margin-bottom: 15px;
                display: flex;
                align-items: flex-start;
            }
            .message.user {
                justify-content: flex-end;
            }
            .message-bubble {
                max-width: 70%;
                padding: 12px 16px;
                border-radius: 18px;
                word-wrap: break-word;
            }
            .message.user .message-bubble {
                background: #667eea;
                color: white;
            }
            .message.agent .message-bubble {
                background: white;
                color: #333;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .chat-input-container {
                display: flex;
                padding: 20px;
                background: white;
                border-radius: 0 0 20px 20px;
                border-top: 1px solid #e0e0e0;
            }
            .chat-input {
                flex: 1;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 25px;
                font-size: 14px;
                outline: none;
            }
            .chat-input:focus {
                border-color: #667eea;
            }
            .send-button {
                margin-left: 10px;
                padding: 12px 24px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-weight: bold;
            }
            .send-button:hover {
                transform: scale(1.05);
            }
            .typing-indicator {
                display: none;
                align-items: center;
                padding: 10px;
            }
            .typing-indicator.active {
                display: flex;
            }
            .dot {
                width: 8px;
                height: 8px;
                margin: 0 3px;
                background: #999;
                border-radius: 50%;
                animation: typing 1.4s infinite;
            }
            .dot:nth-child(2) { animation-delay: 0.2s; }
            .dot:nth-child(3) { animation-delay: 0.4s; }
            @keyframes typing {
                0%, 60%, 100% { transform: translateY(0); }
                30% { transform: translateY(-10px); }
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                <h2>🏨 AI Hotel Receptionist</h2>
                <p>How may I assist you today?</p>
            </div>
            <div class="quick-questions">
                <span class="quick-question" onclick="askQuestion('What room types do you have?')">Room Types</span>
                <span class="quick-question" onclick="askQuestion('Check room availability for tomorrow')">Check Availability</span>
                <span class="quick-question" onclick="askQuestion('What is the price of a deluxe room?')">Room Prices</span>
                <span class="quick-question" onclick="askQuestion('I want to book a room')">Book Now</span>
                <span class="quick-question" onclick="askQuestion('What are your check-in and check-out times?')">Check-in/out Times</span>
                <span class="quick-question" onclick="askQuestion('Do you offer early check-in?')">Early Check-in</span>
                <span class="quick-question" onclick="askQuestion('What amenities do you provide?')">Amenities</span>
                <span class="quick-question" onclick="askQuestion('Is breakfast included?')">Breakfast</span>
                <span class="quick-question" onclick="askQuestion('Can I bring my pet?')">Pet Policy</span>
                <span class="quick-question" onclick="askQuestion('Do you have parking?')">Parking</span>
                <span class="quick-question" onclick="askQuestion('What is your cancellation policy?')">Cancellation</span>
                <span class="quick-question" onclick="askQuestion('How do I modify my booking?')">Modify Booking</span>
                <span class="quick-question" onclick="askQuestion('What payment methods do you accept?')">Payment Options</span>
                <span class="quick-question" onclick="askQuestion('Do you offer airport shuttle?')">Airport Transfer</span>
                <span class="quick-question" onclick="askQuestion('Are group discounts available?')">Group Booking</span>
                <span class="quick-question" onclick="askQuestion('Do you have extra bed facility?')">Extra Bed</span>
                <span class="quick-question" onclick="askQuestion('What is your child policy?')">Child Policy</span>
                <span class="quick-question" onclick="askQuestion('Any discounts for long stays?')">Long Stay Discount</span>
            </div>
            <div class="chat-messages" id="chatMessages">
                <div class="message agent">
                    <div class="message-bubble">
                        Welcome to our hotel! I'm here to help you with room bookings, availability checks, pricing information, and any questions about our services. You can click on the quick questions above or type your own question below. How can I assist you today?
                    </div>
                </div>
            </div>
            <div class="typing-indicator" id="typingIndicator">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
            <div class="chat-input-container">
                <input 
                    type="text" 
                    class="chat-input" 
                    id="messageInput" 
                    placeholder="Type your question here or click a quick question above..."
                    onkeypress="handleKeyPress(event)"
                />
                <button class="send-button" onclick="sendMessage()">Send</button>
            </div>
        </div>
        
        <script>
            let sessionId = null;
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
            
            function askQuestion(question) {
                document.getElementById('messageInput').value = question;
                sendMessage();
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                
                if (!message) return;
                
                // Display user message
                addMessage(message, 'user');
                input.value = '';
                
                // Show typing indicator
                document.getElementById('typingIndicator').classList.add('active');
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            message: message,
                            session_id: sessionId
                        })
                    });
                    
                    const data = await response.json();
                    sessionId = data.session_id;
                    
                    // Hide typing indicator
                    document.getElementById('typingIndicator').classList.remove('active');
                    
                    // Display agent response
                    addMessage(data.message, 'agent');
                    
                } catch (error) {
                    console.error('Error:', error);
                    document.getElementById('typingIndicator').classList.remove('active');
                    addMessage('Sorry, I encountered an error. Please try again.', 'agent');
                }
            }
            
            function addMessage(text, sender) {
                const messagesDiv = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}`;
                
                const bubbleDiv = document.createElement('div');
                bubbleDiv.className = 'message-bubble';
                bubbleDiv.textContent = text;
                
                messageDiv.appendChild(bubbleDiv);
                messagesDiv.appendChild(messageDiv);
                
                // Scroll to bottom
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
        </script>
    </body>
    </html>
    """


# ==================== VOICE ENDPOINTS ====================

@router.post("/voice/input")
async def voice_input(
    request: VoiceInputRequest,
    db: Session = Depends(get_db)
):
    """Process voice input"""
    try:
        session_id = request.session_id or str(uuid.uuid4())
        
        # Convert audio to text
        text = voice_service.speech_to_text(request.audio_base64)
        
        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not transcribe audio"
            )
        
        # Process through dialogue manager
        response = dialogue_manager.process_message(
            user_message=text,
            session_id=session_id
        )
        
        # Convert response to speech
        audio_response = voice_service.text_to_speech(
            response["message"],
            response["language"]
        )
        
        return {
            "transcribed_text": text,
            "response_text": response["message"],
            "response_audio": audio_response,
            "session_id": session_id,
            "intent": response["intent"],
            "language": response["language"]
        }
        
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== BOOKING ENDPOINTS ====================

@router.post("/bookings")
async def create_booking(
    booking: BookingCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new booking"""
    try:
        result = booking_service.create_booking(
            db=db,
            guest_name=booking.guest_name,
            phone=booking.phone,
            email=booking.email,
            check_in_date=booking.check_in_date,
            check_out_date=booking.check_out_date,
            room_type=booking.room_type,
            guest_count=booking.guest_count,
            special_requests=booking.special_requests
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Booking creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/bookings")
async def list_bookings(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """List recent bookings"""
    bookings = db.query(Booking).order_by(Booking.created_at.desc()).limit(limit).all()
    return {"bookings": bookings}


@router.get("/bookings/{booking_id}")
async def get_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):
    """Get booking details"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    return booking


# ==================== ROOM ENDPOINTS ====================

@router.get("/rooms/availability")
async def check_availability(
    check_in: str,
    check_out: str,
    room_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Check room availability"""
    try:
        available_rooms = room_service.check_availability(
            db=db,
            check_in_date=check_in,
            check_out_date=check_out,
            room_type=room_type
        )
        
        return {
            "available": len(available_rooms) > 0,
            "rooms": available_rooms
        }
        
    except Exception as e:
        logger.error(f"Availability check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/rooms")
async def list_rooms(db: Session = Depends(get_db)):
    """List all rooms"""
    rooms = db.query(Room).all()
    return {"rooms": rooms}


# ==================== ANALYTICS ENDPOINTS ====================

@router.get("/analytics/conversations")
async def get_conversation_analytics(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get conversation analytics"""
    conversations = db.query(Conversation).order_by(
        Conversation.timestamp.desc()
    ).limit(limit).all()
    
    # Aggregate statistics
    total_conversations = len(conversations)
    intents = {}
    languages = {}
    avg_confidence = 0
    
    for conv in conversations:
        # Count intents
        intent = conv.detected_intent
        intents[intent] = intents.get(intent, 0) + 1
        
        # Count languages
        lang = conv.detected_language
        languages[lang] = languages.get(lang, 0) + 1
        
        # Sum confidence
        if conv.confidence_score:
            avg_confidence += conv.confidence_score
    
    if total_conversations > 0:
        avg_confidence /= total_conversations
    
    return {
        "total_conversations": total_conversations,
        "intents": intents,
        "languages": languages,
        "average_confidence": round(avg_confidence, 2)
    }


# ==================== UTILITY ENDPOINTS ====================

@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a conversation session"""
    dialogue_manager.clear_session(session_id)
    return {"message": "Session cleared", "session_id": session_id}


@router.get("/voice-ui", response_class=HTMLResponse)
async def voice_ui():
    """Voice interface with speech recognition and synthesis"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Hotel Receptionist - Voice Interface</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                padding: 40px;
                max-width: 600px;
                width: 90%;
            }
            h1 {
                color: #667eea;
                text-align: center;
                margin-bottom: 10px;
            }
            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 30px;
            }
            .voice-button {
                width: 150px;
                height: 150px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                cursor: pointer;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                margin: 30px auto;
                transition: all 0.3s;
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
            }
            .voice-button:hover {
                transform: scale(1.05);
                box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6);
            }
            .voice-button.listening {
                animation: pulse 1.5s infinite;
            }
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
            .mic-icon {
                font-size: 60px;
                color: white;
            }
            .status {
                color: white;
                margin-top: 10px;
                font-weight: bold;
            }
            .transcript-area {
                margin: 20px 0;
            }
            .transcript-box {
                background: #f5f5f5;
                border-radius: 10px;
                padding: 20px;
                min-height: 100px;
                margin-bottom: 10px;
            }
            .transcript-label {
                font-weight: bold;
                color: #667eea;
                margin-bottom: 10px;
            }
            .transcript-text {
                color: #333;
                line-height: 1.6;
            }
            .language-selector {
                text-align: center;
                margin: 20px 0;
            }
            .language-selector select {
                padding: 10px 20px;
                border-radius: 20px;
                border: 2px solid #667eea;
                font-size: 16px;
                cursor: pointer;
            }
            .info-box {
                background: #e8f4f8;
                border-left: 4px solid #667eea;
                padding: 15px;
                border-radius: 5px;
                margin-top: 20px;
            }
            .error-box {
                background: #fee;
                border-left: 4px solid #f00;
                padding: 15px;
                border-radius: 5px;
                margin-top: 20px;
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎤 Voice Receptionist</h1>
            <p class="subtitle">Click the microphone and speak naturally</p>
            
            <div class="language-selector">
                <label for="language">Language: </label>
                <select id="language">
                    <option value="en-US">English</option>
                    <option value="lv-LV">Latvian (Latviešu)</option>
                    <option value="ru-RU">Russian (Русский)</option>
                    <option value="hi-IN">Hindi (हिंदी)</option>
                    <option value="si-LK">Sinhala (සිංහල)</option>
                    <option value="fr-FR">French (Français)</option>
                    <option value="it-IT">Italian (Italiano)</option>
                    <option value="de-DE">German (Deutsch)</option>
                    <option value="es-ES">Spanish (Español)</option>
                </select>
            </div>
            
            <button class="voice-button" id="voiceBtn">
                <div class="mic-icon">🎤</div>
                <div class="status" id="status">Click to Speak</div>
            </button>
            
            <div class="transcript-area">
                <div class="transcript-box">
                    <div class="transcript-label">You said:</div>
                    <div class="transcript-text" id="userTranscript">...</div>
                </div>
                
                <div class="transcript-box">
                    <div class="transcript-label">Receptionist:</div>
                    <div class="transcript-text" id="aiResponse">...</div>
                </div>
            </div>
            
            <div class="info-box">
                <strong>💡 Common Questions:</strong>
                <ul style="margin: 10px 0 0 0; padding-left: 20px;">
                    <li>"What room types do you have?"</li>
                    <li>"How much does a deluxe room cost?"</li>
                    <li>"What amenities do you offer?"</li>
                    <li>"What is the check-in time?"</li>
                    <li>"I want to book a room"</li>
                    <li>"Do you allow pets?"</li>
                    <li>"Is parking available?"</li>
                    <li>"What time is breakfast?"</li>
                </ul>
            </div>
            
            <div class="error-box" id="errorBox"></div>
        </div>
        
        <script>
            const voiceBtn = document.getElementById('voiceBtn');
            const status = document.getElementById('status');
            const userTranscript = document.getElementById('userTranscript');
            const aiResponse = document.getElementById('aiResponse');
            const languageSelect = document.getElementById('language');
            const errorBox = document.getElementById('errorBox');
            
            let recognition;
            let synthesis = window.speechSynthesis;
            let isListening = false;
            
            // Check browser support
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                showError('Speech recognition not supported in this browser. Please use Chrome or Edge.');
            }
            
            // Initialize speech recognition
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            
            languageSelect.addEventListener('change', () => {
                recognition.lang = languageSelect.value;
            });
            recognition.lang = languageSelect.value;
            
            recognition.onstart = () => {
                isListening = true;
                voiceBtn.classList.add('listening');
                status.textContent = 'Listening...';
                userTranscript.textContent = '...';
                errorBox.style.display = 'none';
            };
            
            recognition.onresult = async (event) => {
                const transcript = event.results[0][0].transcript;
                userTranscript.textContent = transcript;
                status.textContent = 'Processing...';
                
                // Send to AI backend
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: transcript,
                            language: languageSelect.value.split('-')[0]
                        })
                    });
                    
                    const data = await response.json();
                    aiResponse.textContent = data.response || data.message || 'No response';
                    
                    // Speak the response
                    speakText(data.response || data.message);
                    
                } catch (error) {
                    console.error('Error:', error);
                    showError('Failed to get response from AI. Please try again.');
                    aiResponse.textContent = 'Error communicating with AI service.';
                }
            };
            
            recognition.onerror = (event) => {
                showError('Speech recognition error: ' + event.error);
                resetButton();
            };
            
            recognition.onend = () => {
                resetButton();
            };
            
            voiceBtn.addEventListener('click', () => {
                if (isListening) {
                    recognition.stop();
                } else {
                    try {
                        recognition.start();
                    } catch (error) {
                        showError('Could not start speech recognition. Please try again.');
                    }
                }
            });
            
            function speakText(text) {
                // Cancel any ongoing speech
                synthesis.cancel();
                
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = languageSelect.value;
                utterance.rate = 0.9;
                utterance.pitch = 1;
                
                utterance.onstart = () => {
                    status.textContent = 'Speaking...';
                };
                
                utterance.onend = () => {
                    status.textContent = 'Click to Speak';
                };
                
                synthesis.speak(utterance);
            }
            
            function resetButton() {
                isListening = false;
                voiceBtn.classList.remove('listening');
                status.textContent = 'Click to Speak';
            }
            
            function showError(message) {
                errorBox.textContent = message;
                errorBox.style.display = 'block';
            }
        </script>
    </body>
    </html>
    """


@router.post("/voice-process")
async def process_voice(audio: UploadFile = File(...)):
    """Process uploaded voice audio file"""
    try:
        # Read audio file
        audio_data = await audio.read()
        
        # Here you would integrate with speech-to-text service
        # For now, return a placeholder
        
        return {
            "success": True,
            "transcript": "Voice processing integrated",
            "message": "Audio received successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
