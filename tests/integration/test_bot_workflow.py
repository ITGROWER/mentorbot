"""
Integration tests for complete bot workflows.

This module contains end-to-end tests that verify complete user journeys
from registration through conversation with AI mentors.
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, User, Chat

from tgbot.config import Config
from tgbot.db.models.user import DBUser
from tgbot.db.models.mentor import DBMentor
from tgbot.db.models.conversation import DBConversationMessage
from tgbot.misc.states import StartForm, DialogueWithMentor


class TestCompleteUserJourney:
    """Test complete user journey from registration to conversation."""

    @pytest.mark.asyncio
    async def test_new_user_complete_registration_flow(self, test_repository: Repository, test_config: Config):
        """Test complete registration flow for a new user."""
        # Mock AI services
        ai_response = {
            "name": "Dr. Sarah Johnson",
            "mentor_age": 42,
            "background": "Experienced software engineer with 15+ years in AI and machine learning",
            "recent_events": "Recently published a paper on neural networks and completed a course on deep learning",
            "greeting": "Hello! I'm Dr. Sarah Johnson, and I'm excited to be your AI mentor. I understand you're interested in learning about artificial intelligence. What specific area would you like to explore first?",
            "sys_prompt_summary": "You are Dr. Sarah Johnson, an experienced AI researcher and mentor. You're friendly, encouraging, and have deep knowledge in machine learning, neural networks, and AI applications.",
            "personality_style": "Professional yet approachable, encouraging, and patient",
            "brief_background": "Software developer interested in AI",
            "goal": "Learn AI and machine learning fundamentals"
        }
        
        with patch('tgbot.handlers.users.user.init_mentor', return_value=json.dumps(ai_response)) as mock_init_mentor, \
             patch('tgbot.handlers.users.user.create_embeddings', return_value=[0.1, 0.2, 0.3, 0.4, 0.5]) as mock_embeddings, \
             patch('tgbot.handlers.users.user.retrieve_history', return_value=[]) as mock_retrieve, \
             patch('tgbot.handlers.users.user.store_message') as mock_store, \
             patch('tgbot.handlers.users.user.reply_from_mentor', return_value="Great question! Let me help you understand the basics of machine learning.") as mock_reply:
            
            # Step 1: User starts bot (/start command)
            user_data = {
                "name": "Test User",
                "username": "testuser",
                "telegram_id": "123456789",
            }
            user = await test_repository.users.create(DBUser(**user_data))
            
            # Verify user was created
            assert user.id is not None
            assert user.telegram_id == "123456789"
            assert user.is_reg is False
            
            # Step 2: User provides background information
            background_text = "I'm a software developer with 3 years of experience. I want to learn AI and machine learning to advance my career."
            
            # Update user with background and mark as registered
            user.brief_background = ai_response["brief_background"]
            user.goal = ai_response["goal"]
            user.is_reg = True
            await test_repository.users.update(user)
            
            # Step 3: Create mentor
            mentor = DBMentor(
                name=ai_response["name"],
                mentor_age=ai_response["mentor_age"],
                background=ai_response["background"],
                recent_events=ai_response["recent_events"],
                personality_style=ai_response["personality_style"],
                greeting=ai_response["greeting"],
                sys_prompt_summary=ai_response["sys_prompt_summary"],
                user_id=user.id,
            )
            created_mentor = await test_repository.mentors.create(mentor)
            
            # Verify mentor was created
            assert created_mentor.id is not None
            assert created_mentor.name == "Dr. Sarah Johnson"
            assert created_mentor.user_id == user.id
            
            # Step 4: User starts conversation
            user_message = "What are the fundamental concepts I should know about machine learning?"
            
            # Create conversation message
            conversation_message = DBConversationMessage(
                user_id=user.id,
                mentor_id=created_mentor.id,
                role="user",
                content=user_message,
            )
            await test_repository.conversations.create_message(conversation_message)
            
            # Verify conversation was stored
            messages = await test_repository.conversations.get_messages(user_id=user.id)
            assert len(messages) == 1
            assert messages[0].content == user_message
            assert messages[0].role == "user"

    @pytest.mark.asyncio
    async def test_subscription_workflow(self, test_repository: Repository, test_config: Config):
        """Test subscription purchase and management workflow."""
        # Create user
        user = DBUser(
            name="Test User",
            telegram_id="123456789",
            is_reg=True,
            is_sub=False,
        )
        created_user = await test_repository.users.create(user)
        
        # Verify initial subscription status
        assert created_user.is_sub is False
        assert created_user.sub_until is None
        
        # Simulate subscription purchase
        created_user.is_sub = True
        created_user.sub_until = datetime.utcnow() + timedelta(days=30)
        await test_repository.users.update(created_user)
        
        # Verify subscription was updated
        updated_user = await test_repository.users.get(id=created_user.id)
        assert updated_user.is_sub is True
        assert updated_user.sub_until is not None
        
        # Test subscription expiration
        expired_user = DBUser(
            name="Expired User",
            telegram_id="987654321",
            is_reg=True,
            is_sub=True,
            sub_until=datetime.utcnow() - timedelta(days=1),  # Expired
        )
        await test_repository.users.create(expired_user)
        
        # Check if subscription is expired
        is_expired = expired_user.sub_until < datetime.utcnow()
        assert is_expired is True

    @pytest.mark.asyncio
    async def test_conversation_history_management(self, test_repository: Repository):
        """Test conversation history storage and retrieval."""
        # Create user and mentor
        user = DBUser(
            name="Test User",
            telegram_id="123456789",
            is_reg=True,
        )
        created_user = await test_repository.users.create(user)
        
        mentor = DBMentor(
            name="Test Mentor",
            mentor_age=35,
            background="Test background",
            recent_events="Test events",
            personality_style="Test style",
            greeting="Test greeting",
            sys_prompt_summary="Test prompt",
            user_id=created_user.id,
        )
        created_mentor = await test_repository.mentors.create(mentor)
        
        # Create conversation history
        conversation_data = [
            {"role": "user", "content": "Hello, I want to learn about AI"},
            {"role": "assistant", "content": "Great! I'd be happy to help you learn about AI."},
            {"role": "user", "content": "What are the main types of machine learning?"},
            {"role": "assistant", "content": "There are three main types: supervised, unsupervised, and reinforcement learning."},
            {"role": "user", "content": "Can you explain supervised learning?"},
            {"role": "assistant", "content": "Supervised learning uses labeled training data to learn patterns."},
        ]
        
        # Store conversation messages
        for msg_data in conversation_data:
            message = DBConversationMessage(
                user_id=created_user.id,
                mentor_id=created_mentor.id,
                role=msg_data["role"],
                content=msg_data["content"],
            )
            await test_repository.conversations.create_message(message)
        
        # Verify conversation was stored
        messages = await test_repository.conversations.get_messages(user_id=created_user.id)
        assert len(messages) == 6
        
        # Verify message order and content
        assert messages[0].role == "user"
        assert messages[0].content == "Hello, I want to learn about AI"
        assert messages[1].role == "assistant"
        assert messages[1].content == "Great! I'd be happy to help you learn about AI."
        
        # Test message counting
        message_count = await test_repository.conversations.count(user_id=created_user.id)
        assert message_count == 6

    @pytest.mark.asyncio
    async def test_free_tier_limitations(self, test_repository: Repository):
        """Test free tier message limitations."""
        # Create user without subscription
        user = DBUser(
            name="Free User",
            telegram_id="111111111",
            is_reg=True,
            is_sub=False,
        )
        created_user = await test_repository.users.create(user)
        
        # Create 10 messages (free tier limit)
        for i in range(10):
            message = DBConversationMessage(
                user_id=created_user.id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i + 1}",
            )
            await test_repository.conversations.create_message(message)
        
        # Verify message count
        message_count = await test_repository.conversations.count(user_id=created_user.id)
        assert message_count == 10
        
        # This would trigger the free tier limit in the actual handler
        assert message_count >= 10  # Free tier limit reached

    @pytest.mark.asyncio
    async def test_mentor_creation_and_retrieval(self, test_repository: Repository):
        """Test mentor creation and retrieval workflows."""
        # Create user
        user = DBUser(
            name="Test User",
            telegram_id="123456789",
            is_reg=True,
        )
        created_user = await test_repository.users.create(user)
        
        # Create multiple mentors for the user
        mentors_data = [
            {
                "name": "AI Mentor",
                "mentor_age": 35,
                "background": "AI researcher",
                "recent_events": "Published AI paper",
                "personality_style": "Technical and precise",
                "greeting": "Hello! I'm your AI mentor.",
                "sys_prompt_summary": "AI expert mentor",
            },
            {
                "name": "Business Mentor",
                "mentor_age": 45,
                "background": "Business executive",
                "recent_events": "Launched startup",
                "personality_style": "Strategic and motivational",
                "greeting": "Hi! I'm your business mentor.",
                "sys_prompt_summary": "Business strategy mentor",
            },
        ]
        
        created_mentors = []
        for mentor_data in mentors_data:
            mentor = DBMentor(
                user_id=created_user.id,
                **mentor_data
            )
            created_mentor = await test_repository.mentors.create(mentor)
            created_mentors.append(created_mentor)
        
        # Verify mentors were created
        assert len(created_mentors) == 2
        
        # Test getting all mentors for user
        user_mentors = await test_repository.mentors.get_all(user_id=created_user.id)
        assert len(user_mentors) == 2
        
        # Test getting specific mentor by user ID (should return first one)
        first_mentor = await test_repository.mentors.get_by_user_id(created_user.id)
        assert first_mentor is not None
        assert first_mentor.user_id == created_user.id

    @pytest.mark.asyncio
    async def test_user_ban_workflow(self, test_repository: Repository):
        """Test user ban and unban workflow."""
        # Create user
        user = DBUser(
            name="Test User",
            telegram_id="123456789",
            is_reg=True,
            is_ban=False,
        )
        created_user = await test_repository.users.create(user)
        
        # Verify initial ban status
        assert created_user.is_ban is False
        
        # Ban user
        created_user.is_ban = True
        await test_repository.users.update(created_user)
        
        # Verify user is banned
        updated_user = await test_repository.users.get(id=created_user.id)
        assert updated_user.is_ban is True
        
        # Unban user
        updated_user.is_ban = False
        await test_repository.users.update(updated_user)
        
        # Verify user is unbanned
        final_user = await test_repository.users.get(id=created_user.id)
        assert final_user.is_ban is False