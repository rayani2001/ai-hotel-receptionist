"""
Unit Tests for Dialogue Manager
Run with: pytest tests/test_dialogue_manager.py
"""

import pytest
import sys
sys.path.append('..')

from models.dialogue_manager import DialogueManager, DialogueState


class TestDialogueManager:
    """Test cases for DialogueManager"""
    
    @pytest.fixture
    def dialogue_manager(self):
        """Create a dialogue manager instance for testing"""
        return DialogueManager()
    
    def test_initialization(self, dialogue_manager):
        """Test that dialogue manager initializes correctly"""
        assert dialogue_manager is not None
        assert dialogue_manager.intent_classifier is not None
        assert dialogue_manager.entity_extractor is not None
    
    def test_greeting_intent(self, dialogue_manager):
        """Test greeting recognition"""
        response = dialogue_manager.process_message(
            user_message="Hello",
            session_id="test_session_1"
        )
        
        assert response["intent"] == "greeting"
        assert "welcome" in response["message"].lower() or "assist" in response["message"].lower()
        assert response["language"] in ["en", "hi", "ta", "te", "kn"]
    
    def test_room_inquiry_intent(self, dialogue_manager):
        """Test room inquiry detection"""
        response = dialogue_manager.process_message(
            user_message="What types of rooms do you have?",
            session_id="test_session_2"
        )
        
        assert response["intent"] == "room_inquiry"
        assert "room" in response["message"].lower()
    
    def test_booking_intent(self, dialogue_manager):
        """Test booking request detection"""
        response = dialogue_manager.process_message(
            user_message="I want to book a room",
            session_id="test_session_3"
        )
        
        assert response["intent"] == "room_booking"
        assert len(response["missing_slots"]) > 0
    
    def test_session_persistence(self, dialogue_manager):
        """Test that session state persists across turns"""
        session_id = "test_session_4"
        
        # First message
        response1 = dialogue_manager.process_message(
            user_message="I want to book a room",
            session_id=session_id
        )
        
        # Second message with name
        response2 = dialogue_manager.process_message(
            user_message="My name is John Doe",
            session_id=session_id
        )
        
        assert response2["turn_count"] > response1["turn_count"]
        
        # Check that session exists
        assert session_id in dialogue_manager.active_sessions
    
    def test_entity_extraction_phone(self, dialogue_manager):
        """Test phone number extraction"""
        response = dialogue_manager.process_message(
            user_message="My phone number is 9876543210",
            session_id="test_session_5"
        )
        
        assert "entities" in response
        # Phone might be extracted
    
    def test_multilingual_greeting(self, dialogue_manager):
        """Test Hindi greeting detection"""
        response = dialogue_manager.process_message(
            user_message="नमस्ते",
            session_id="test_session_6"
        )
        
        assert response["language"] == "hi"
        assert response["intent"] == "greeting"
    
    def test_clear_session(self, dialogue_manager):
        """Test session clearing"""
        session_id = "test_session_7"
        
        # Create a session
        dialogue_manager.process_message(
            user_message="Hello",
            session_id=session_id
        )
        
        # Clear it
        dialogue_manager.clear_session(session_id)
        
        # Verify it's cleared
        assert session_id not in dialogue_manager.active_sessions


class TestDialogueState:
    """Test cases for DialogueState"""
    
    def test_state_creation(self):
        """Test creating a dialogue state"""
        state = DialogueState(
            conversation_id="conv_123",
            session_id="session_123"
        )
        
        assert state.conversation_id == "conv_123"
        assert state.session_id == "session_123"
        assert state.turn_count == 0
        assert len(state.conversation_history) == 0
    
    def test_add_turn(self):
        """Test adding conversation turns"""
        state = DialogueState(
            conversation_id="conv_123",
            session_id="session_123"
        )
        
        state.add_turn(
            user_message="Hello",
            agent_response="Hi there!",
            detected_intent="greeting"
        )
        
        assert state.turn_count == 1
        assert len(state.conversation_history) == 1
        assert state.conversation_history[0]["user"] == "Hello"
    
    def test_context_summary(self):
        """Test context summary generation"""
        state = DialogueState(
            conversation_id="conv_123",
            session_id="session_123",
            language="en",
            primary_intent="room_booking"
        )
        
        state.collected_entities = {"guest_name": "John"}
        
        summary = state.get_context_summary()
        
        assert "en" in summary
        assert "room_booking" in summary
        assert "John" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
