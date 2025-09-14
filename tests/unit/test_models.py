"""
Unit tests for database models.

This module contains tests for all database models including User, Mentor,
and Conversation models to ensure proper data validation and relationships.
"""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.db.models.user import DBUser
from tgbot.db.models.mentor import DBMentor
from tgbot.db.models.conversation import DBConversationMessage


class TestDBUser:
    """Test cases for DBUser model."""

    @pytest.mark.asyncio
    async def test_user_creation(self, test_session: AsyncSession):
        """Test creating a new user."""
        user = DBUser(
            name="Test User",
            username="testuser",
            telegram_id="123456789",
            brief_background="Software developer",
            goal="Learn AI",
        )
        
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        assert user.id is not None
        assert user.name == "Test User"
        assert user.username == "testuser"
        assert user.telegram_id == "123456789"
        assert user.brief_background == "Software developer"
        assert user.goal == "Learn AI"
        assert user.is_sub is False
        assert user.is_reg is False
        assert user.is_ban is False
        assert user.sub_until is None

    @pytest.mark.asyncio
    async def test_user_from_aiogram(self, test_session: AsyncSession):
        """Test creating user from aiogram User object."""
        # Mock aiogram User object
        class MockUser:
            def __init__(self):
                self.full_name = "Test User"
                self.username = "testuser"
                self.id = 123456789

        aiogram_user = MockUser()
        user = DBUser.from_aiogram(aiogram_user)
        
        assert user.name == "Test User"
        assert user.username == "testuser"
        assert user.telegram_id == "123456789"

    @pytest.mark.asyncio
    async def test_user_subscription_status(self, test_session: AsyncSession):
        """Test user subscription status management."""
        user = DBUser(
            name="Test User",
            telegram_id="123456789",
        )
        
        # Test initial subscription status
        assert user.is_sub is False
        assert user.sub_until is None
        
        # Test setting subscription
        user.is_sub = True
        user.sub_until = datetime(2024, 12, 31, 23, 59, 59)
        
        assert user.is_sub is True
        assert user.sub_until is not None

    @pytest.mark.asyncio
    async def test_user_ban_status(self, test_session: AsyncSession):
        """Test user ban status management."""
        user = DBUser(
            name="Test User",
            telegram_id="123456789",
        )
        
        # Test initial ban status
        assert user.is_ban is False
        
        # Test setting ban status
        user.is_ban = True
        assert user.is_ban is True


class TestDBMentor:
    """Test cases for DBMentor model."""

    @pytest.mark.asyncio
    async def test_mentor_creation(self, test_session: AsyncSession, sample_user_data):
        """Test creating a new mentor."""
        # Create user first
        user = DBUser(**sample_user_data)
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # Create mentor
        mentor = DBMentor(
            name="Test Mentor",
            mentor_age=35,
            background="Experienced software engineer",
            recent_events="Completed AI course",
            personality_style="Friendly and encouraging",
            greeting="Hello! I'm here to help you learn.",
            sys_prompt_summary="You are a helpful AI mentor.",
            user_id=user.id,
        )
        
        test_session.add(mentor)
        await test_session.commit()
        await test_session.refresh(mentor)
        
        assert mentor.id is not None
        assert mentor.name == "Test Mentor"
        assert mentor.mentor_age == 35
        assert mentor.background == "Experienced software engineer"
        assert mentor.recent_events == "Completed AI course"
        assert mentor.personality_style == "Friendly and encouraging"
        assert mentor.greeting == "Hello! I'm here to help you learn."
        assert mentor.sys_prompt_summary == "You are a helpful AI mentor."
        assert mentor.user_id == user.id

    @pytest.mark.asyncio
    async def test_mentor_user_relationship(self, test_session: AsyncSession, sample_user_data):
        """Test mentor-user relationship."""
        # Create user
        user = DBUser(**sample_user_data)
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # Create mentor
        mentor = DBMentor(
            name="Test Mentor",
            mentor_age=35,
            background="Test background",
            recent_events="Test events",
            personality_style="Test style",
            greeting="Test greeting",
            sys_prompt_summary="Test prompt",
            user_id=user.id,
        )
        
        test_session.add(mentor)
        await test_session.commit()
        await test_session.refresh(mentor)
        
        # Test relationship
        assert mentor.user.id == user.id
        assert mentor in user.mentors


class TestDBConversationMessage:
    """Test cases for DBConversationMessage model."""

    @pytest.mark.asyncio
    async def test_conversation_message_creation(self, test_session: AsyncSession, sample_user_data):
        """Test creating a conversation message."""
        # Create user
        user = DBUser(**sample_user_data)
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # Create conversation message
        message = DBConversationMessage(
            user_id=user.id,
            role="user",
            content="Hello, I want to learn about AI",
        )
        
        test_session.add(message)
        await test_session.commit()
        await test_session.refresh(message)
        
        assert message.id is not None
        assert message.user_id == user.id
        assert message.role == "user"
        assert message.content == "Hello, I want to learn about AI"
        assert message.created_at is not None

    @pytest.mark.asyncio
    async def test_conversation_message_with_mentor(self, test_session: AsyncSession, sample_user_data):
        """Test creating a conversation message with mentor."""
        # Create user
        user = DBUser(**sample_user_data)
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # Create mentor
        mentor = DBMentor(
            name="Test Mentor",
            mentor_age=35,
            background="Test background",
            recent_events="Test events",
            personality_style="Test style",
            greeting="Test greeting",
            sys_prompt_summary="Test prompt",
            user_id=user.id,
        )
        test_session.add(mentor)
        await test_session.commit()
        await test_session.refresh(mentor)
        
        # Create conversation message with mentor
        message = DBConversationMessage(
            user_id=user.id,
            mentor_id=mentor.id,
            role="assistant",
            content="I'd be happy to help you learn about AI!",
        )
        
        test_session.add(message)
        await test_session.commit()
        await test_session.refresh(message)
        
        assert message.id is not None
        assert message.user_id == user.id
        assert message.mentor_id == mentor.id
        assert message.role == "assistant"
        assert message.content == "I'd be happy to help you learn about AI!"

    @pytest.mark.asyncio
    async def test_conversation_message_relationships(self, test_session: AsyncSession, sample_user_data):
        """Test conversation message relationships."""
        # Create user
        user = DBUser(**sample_user_data)
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # Create mentor
        mentor = DBMentor(
            name="Test Mentor",
            mentor_age=35,
            background="Test background",
            recent_events="Test events",
            personality_style="Test style",
            greeting="Test greeting",
            sys_prompt_summary="Test prompt",
            user_id=user.id,
        )
        test_session.add(mentor)
        await test_session.commit()
        await test_session.refresh(mentor)
        
        # Create conversation messages
        user_message = DBConversationMessage(
            user_id=user.id,
            mentor_id=mentor.id,
            role="user",
            content="Hello!",
        )
        assistant_message = DBConversationMessage(
            user_id=user.id,
            mentor_id=mentor.id,
            role="assistant",
            content="Hi there!",
        )
        
        test_session.add_all([user_message, assistant_message])
        await test_session.commit()
        
        # Test relationships
        await test_session.refresh(user)
        await test_session.refresh(mentor)
        
        assert len(user.conversation_messages) == 2
        assert len(mentor.conversation_messages) == 2
        assert user_message in user.conversation_messages
        assert assistant_message in user.conversation_messages
        assert user_message in mentor.conversation_messages
        assert assistant_message in mentor.conversation_messages