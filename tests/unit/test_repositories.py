"""
Unit tests for database repositories.

This module contains tests for all repository classes to ensure proper
data access patterns and CRUD operations.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.db.models.user import DBUser
from tgbot.db.models.mentor import DBMentor
from tgbot.db.models.conversation import DBConversationMessage
from tgbot.db.repositories.repository import Repository


class TestUserRepository:
    """Test cases for user repository operations."""

    @pytest.mark.asyncio
    async def test_create_user(self, test_repository: Repository):
        """Test creating a new user."""
        user_data = {
            "name": "Test User",
            "username": "testuser",
            "telegram_id": "123456789",
            "brief_background": "Software developer",
            "goal": "Learn AI",
        }
        
        user = await test_repository.users.create(DBUser(**user_data))
        
        assert user.id is not None
        assert user.name == "Test User"
        assert user.telegram_id == "123456789"

    @pytest.mark.asyncio
    async def test_get_user_by_telegram_id(self, test_repository: Repository):
        """Test getting user by Telegram ID."""
        # Create user
        user = DBUser(
            name="Test User",
            telegram_id="123456789",
        )
        await test_repository.users.create(user)
        
        # Get user by Telegram ID
        found_user = await test_repository.users.get(telegram_id="123456789")
        
        assert found_user is not None
        assert found_user.telegram_id == "123456789"
        assert found_user.name == "Test User"

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, test_repository: Repository):
        """Test getting user by ID."""
        # Create user
        user = DBUser(
            name="Test User",
            telegram_id="123456789",
        )
        created_user = await test_repository.users.create(user)
        
        # Get user by ID
        found_user = await test_repository.users.get(id=created_user.id)
        
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.name == "Test User"

    @pytest.mark.asyncio
    async def test_update_user(self, test_repository: Repository):
        """Test updating user information."""
        # Create user
        user = DBUser(
            name="Test User",
            telegram_id="123456789",
        )
        created_user = await test_repository.users.create(user)
        
        # Update user
        created_user.name = "Updated User"
        created_user.is_reg = True
        updated_user = await test_repository.users.update(created_user)
        
        assert updated_user.name == "Updated User"
        assert updated_user.is_reg is True

    @pytest.mark.asyncio
    async def test_get_all_users(self, test_repository: Repository):
        """Test getting all users."""
        # Create multiple users
        users = [
            DBUser(name="User 1", telegram_id="111111111"),
            DBUser(name="User 2", telegram_id="222222222"),
            DBUser(name="User 3", telegram_id="333333333"),
        ]
        
        for user in users:
            await test_repository.users.create(user)
        
        # Get all users
        all_users = await test_repository.users.get_all()
        
        assert len(all_users) == 3
        assert all(user.name in ["User 1", "User 2", "User 3"] for user in all_users)

    @pytest.mark.asyncio
    async def test_user_subscription_management(self, test_repository: Repository):
        """Test user subscription management."""
        # Create user
        user = DBUser(
            name="Test User",
            telegram_id="123456789",
        )
        created_user = await test_repository.users.create(user)
        
        # Set subscription
        created_user.is_sub = True
        created_user.sub_until = datetime.utcnow() + timedelta(days=30)
        await test_repository.users.update(created_user)
        
        # Verify subscription
        updated_user = await test_repository.users.get(id=created_user.id)
        assert updated_user.is_sub is True
        assert updated_user.sub_until is not None


class TestMentorRepository:
    """Test cases for mentor repository operations."""

    @pytest.mark.asyncio
    async def test_create_mentor(self, test_repository: Repository):
        """Test creating a new mentor."""
        # Create user first
        user = DBUser(
            name="Test User",
            telegram_id="123456789",
        )
        created_user = await test_repository.users.create(user)
        
        # Create mentor
        mentor_data = {
            "name": "Test Mentor",
            "mentor_age": 35,
            "background": "Experienced software engineer",
            "recent_events": "Completed AI course",
            "personality_style": "Friendly and encouraging",
            "greeting": "Hello! I'm here to help you learn.",
            "sys_prompt_summary": "You are a helpful AI mentor.",
            "user_id": created_user.id,
        }
        
        mentor = await test_repository.mentors.create(DBMentor(**mentor_data))
        
        assert mentor.id is not None
        assert mentor.name == "Test Mentor"
        assert mentor.user_id == created_user.id

    @pytest.mark.asyncio
    async def test_get_mentor_by_user_id(self, test_repository: Repository):
        """Test getting mentor by user ID."""
        # Create user and mentor
        user = DBUser(name="Test User", telegram_id="123456789")
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
        await test_repository.mentors.create(mentor)
        
        # Get mentor by user ID
        found_mentor = await test_repository.mentors.get_by_user_id(created_user.id)
        
        assert found_mentor is not None
        assert found_mentor.user_id == created_user.id
        assert found_mentor.name == "Test Mentor"

    @pytest.mark.asyncio
    async def test_get_all_mentors_for_user(self, test_repository: Repository):
        """Test getting all mentors for a user."""
        # Create user
        user = DBUser(name="Test User", telegram_id="123456789")
        created_user = await test_repository.users.create(user)
        
        # Create multiple mentors for the user
        mentors = [
            DBMentor(
                name="Mentor 1",
                mentor_age=30,
                background="Background 1",
                recent_events="Events 1",
                personality_style="Style 1",
                greeting="Greeting 1",
                sys_prompt_summary="Prompt 1",
                user_id=created_user.id,
            ),
            DBMentor(
                name="Mentor 2",
                mentor_age=40,
                background="Background 2",
                recent_events="Events 2",
                personality_style="Style 2",
                greeting="Greeting 2",
                sys_prompt_summary="Prompt 2",
                user_id=created_user.id,
            ),
        ]
        
        for mentor in mentors:
            await test_repository.mentors.create(mentor)
        
        # Get all mentors for user
        user_mentors = await test_repository.mentors.get_all(user_id=created_user.id)
        
        assert len(user_mentors) == 2
        assert all(mentor.user_id == created_user.id for mentor in user_mentors)

    @pytest.mark.asyncio
    async def test_update_mentor(self, test_repository: Repository):
        """Test updating mentor information."""
        # Create user and mentor
        user = DBUser(name="Test User", telegram_id="123456789")
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
        
        # Update mentor
        created_mentor.name = "Updated Mentor"
        created_mentor.personality_style = "Updated style"
        updated_mentor = await test_repository.mentors.update(created_mentor)
        
        assert updated_mentor.name == "Updated Mentor"
        assert updated_mentor.personality_style == "Updated style"


class TestConversationRepository:
    """Test cases for conversation repository operations."""

    @pytest.mark.asyncio
    async def test_create_message(self, test_repository: Repository):
        """Test creating a conversation message."""
        # Create user
        user = DBUser(name="Test User", telegram_id="123456789")
        created_user = await test_repository.users.create(user)
        
        # Create message
        message = DBConversationMessage(
            user_id=created_user.id,
            role="user",
            content="Hello, I want to learn about AI",
        )
        
        created_message = await test_repository.conversations.create_message(message)
        
        assert created_message.id is not None
        assert created_message.user_id == created_user.id
        assert created_message.role == "user"
        assert created_message.content == "Hello, I want to learn about AI"

    @pytest.mark.asyncio
    async def test_count_messages_for_user(self, test_repository: Repository):
        """Test counting messages for a user."""
        # Create user
        user = DBUser(name="Test User", telegram_id="123456789")
        created_user = await test_repository.users.create(user)
        
        # Create multiple messages
        messages = [
            DBConversationMessage(
                user_id=created_user.id,
                role="user",
                content="Message 1",
            ),
            DBConversationMessage(
                user_id=created_user.id,
                role="assistant",
                content="Response 1",
            ),
            DBConversationMessage(
                user_id=created_user.id,
                role="user",
                content="Message 2",
            ),
        ]
        
        for message in messages:
            await test_repository.conversations.create_message(message)
        
        # Count messages
        count = await test_repository.conversations.count(user_id=created_user.id)
        
        assert count == 3

    @pytest.mark.asyncio
    async def test_get_messages_for_user(self, test_repository: Repository):
        """Test getting messages for a user."""
        # Create user
        user = DBUser(name="Test User", telegram_id="123456789")
        created_user = await test_repository.users.create(user)
        
        # Create messages
        messages = [
            DBConversationMessage(
                user_id=created_user.id,
                role="user",
                content="First message",
            ),
            DBConversationMessage(
                user_id=created_user.id,
                role="assistant",
                content="First response",
            ),
        ]
        
        for message in messages:
            await test_repository.conversations.create_message(message)
        
        # Get messages
        user_messages = await test_repository.conversations.get_messages(user_id=created_user.id)
        
        assert len(user_messages) == 2
        assert all(msg.user_id == created_user.id for msg in user_messages)

    @pytest.mark.asyncio
    async def test_get_messages_with_mentor(self, test_repository: Repository):
        """Test getting messages with mentor."""
        # Create user and mentor
        user = DBUser(name="Test User", telegram_id="123456789")
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
        
        # Create messages with mentor
        messages = [
            DBConversationMessage(
                user_id=created_user.id,
                mentor_id=created_mentor.id,
                role="user",
                content="Hello mentor!",
            ),
            DBConversationMessage(
                user_id=created_user.id,
                mentor_id=created_mentor.id,
                role="assistant",
                content="Hello! How can I help you?",
            ),
        ]
        
        for message in messages:
            await test_repository.conversations.create_message(message)
        
        # Get messages with mentor
        mentor_messages = await test_repository.conversations.get_messages(
            user_id=created_user.id,
            mentor_id=created_mentor.id
        )
        
        assert len(mentor_messages) == 2
        assert all(msg.mentor_id == created_mentor.id for msg in mentor_messages)