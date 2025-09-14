"""
Test utilities and helper functions.

This module provides utility functions and helpers that can be used
across different test modules to reduce code duplication and improve
test maintainability.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, User, Chat, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.config import Config
from tgbot.db.models.user import DBUser
from tgbot.db.models.mentor import DBMentor
from tgbot.db.models.conversation import DBConversationMessage


class MockTelegramObjects:
    """Factory for creating mock Telegram objects for testing."""

    @staticmethod
    def create_user(
        user_id: int = 123456789,
        full_name: str = "Test User",
        username: str = "testuser",
        is_bot: bool = False
    ) -> User:
        """
        Create a mock Telegram User object.
        
        Args:
            user_id: Telegram user ID
            full_name: User's full name
            username: User's username
            is_bot: Whether the user is a bot
            
        Returns:
            User: Mock User object
        """
        user = MagicMock(spec=User)
        user.id = user_id
        user.full_name = full_name
        user.username = username
        user.is_bot = is_bot
        return user

    @staticmethod
    def create_chat(
        chat_id: int = 123456789,
        chat_type: str = "private"
    ) -> Chat:
        """
        Create a mock Telegram Chat object.
        
        Args:
            chat_id: Chat ID
            chat_type: Type of chat (private, group, supergroup, channel)
            
        Returns:
            Chat: Mock Chat object
        """
        chat = MagicMock(spec=Chat)
        chat.id = chat_id
        chat.type = chat_type
        return chat

    @staticmethod
    def create_message(
        text: str = "Hello, world!",
        user: Optional[User] = None,
        chat: Optional[Chat] = None,
        message_id: int = 1
    ) -> Message:
        """
        Create a mock Telegram Message object.
        
        Args:
            text: Message text content
            user: Message sender (User object)
            chat: Chat where message was sent
            message_id: Unique message identifier
            
        Returns:
            Message: Mock Message object
        """
        if user is None:
            user = MockTelegramObjects.create_user()
        if chat is None:
            chat = MockTelegramObjects.create_chat()
            
        message = MagicMock(spec=Message)
        message.text = text
        message.from_user = user
        message.chat = chat
        message.message_id = message_id
        message.answer = AsyncMock()
        message.reply = AsyncMock()
        message.edit_text = AsyncMock()
        return message

    @staticmethod
    def create_callback_query(
        data: str = "test_callback",
        user: Optional[User] = None,
        message: Optional[Message] = None
    ) -> CallbackQuery:
        """
        Create a mock Telegram CallbackQuery object.
        
        Args:
            data: Callback data
            user: User who triggered the callback
            message: Original message
            
        Returns:
            CallbackQuery: Mock CallbackQuery object
        """
        if user is None:
            user = MockTelegramObjects.create_user()
        if message is None:
            message = MockTelegramObjects.create_message()
            
        callback = MagicMock(spec=CallbackQuery)
        callback.data = data
        callback.from_user = user
        callback.message = message
        callback.answer = AsyncMock()
        return callback


class DatabaseTestHelpers:
    """Helper functions for database testing."""

    @staticmethod
    async def create_test_user(
        session: AsyncSession,
        telegram_id: str = "123456789",
        name: str = "Test User",
        **kwargs
    ) -> DBUser:
        """
        Create a test user in the database.
        
        Args:
            session: Database session
            telegram_id: Telegram user ID
            name: User's name
            **kwargs: Additional user attributes
            
        Returns:
            DBUser: Created user instance
        """
        user_data = {
            "name": name,
            "telegram_id": telegram_id,
            "username": "testuser",
            "brief_background": "Test background",
            "goal": "Test goal",
            **kwargs
        }
        
        user = DBUser(**user_data)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        return user

    @staticmethod
    async def create_test_mentor(
        session: AsyncSession,
        user_id: int,
        name: str = "Test Mentor",
        **kwargs
    ) -> DBMentor:
        """
        Create a test mentor in the database.
        
        Args:
            session: Database session
            user_id: ID of the user who owns this mentor
            name: Mentor's name
            **kwargs: Additional mentor attributes
            
        Returns:
            DBMentor: Created mentor instance
        """
        mentor_data = {
            "name": name,
            "mentor_age": 35,
            "background": "Test background",
            "recent_events": "Test events",
            "personality_style": "Test style",
            "greeting": "Test greeting",
            "sys_prompt_summary": "Test prompt",
            "user_id": user_id,
            **kwargs
        }
        
        mentor = DBMentor(**mentor_data)
        session.add(mentor)
        await session.commit()
        await session.refresh(mentor)
        
        return mentor

    @staticmethod
    async def create_test_conversation(
        session: AsyncSession,
        user_id: int,
        mentor_id: Optional[int] = None,
        message_count: int = 3
    ) -> List[DBConversationMessage]:
        """
        Create test conversation messages in the database.
        
        Args:
            session: Database session
            user_id: ID of the user
            mentor_id: ID of the mentor (optional)
            message_count: Number of messages to create
            
        Returns:
            List[DBConversationMessage]: Created conversation messages
        """
        messages = []
        
        for i in range(message_count):
            role = "user" if i % 2 == 0 else "assistant"
            content = f"Test message {i + 1}"
            
            message = DBConversationMessage(
                user_id=user_id,
                mentor_id=mentor_id,
                role=role,
                content=content,
            )
            session.add(message)
            messages.append(message)
        
        await session.commit()
        
        for message in messages:
            await session.refresh(message)
        
        return messages


class MockAIServices:
    """Mock AI services for testing."""

    @staticmethod
    def mock_openai_responses():
        """
        Create mock OpenAI API responses.
        
        Returns:
            Dict containing mock responses for different AI services
        """
        return {
            "mentor_creation": {
                "name": "Dr. Test Mentor",
                "mentor_age": 35,
                "background": "Test AI researcher background",
                "recent_events": "Test recent events",
                "personality_style": "Test personality style",
                "greeting": "Hello! I'm your test mentor.",
                "sys_prompt_summary": "Test system prompt summary",
                "brief_background": "Test user background",
                "goal": "Test user goal",
            },
            "mentor_reply": "This is a test mentor response.",
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5] * 20,  # 100-dimensional vector
        }

    @staticmethod
    def patch_openai_services():
        """
        Create patches for OpenAI services.
        
        Returns:
            List of patch objects for OpenAI services
        """
        responses = MockAIServices.mock_openai_responses()
        
        patches = [
            patch('tgbot.services.temp_openai.openai_client.chat.completions.create', 
                  return_value=MagicMock(choices=[MagicMock(message=MagicMock(content=json.dumps(responses["mentor_creation"])))])),
            patch('tgbot.services.temp_openai.openai_client.embeddings.create', 
                  return_value=MagicMock(data=[MagicMock(embedding=responses["embedding"])])),
        ]
        
        return patches

    @staticmethod
    def patch_qdrant_services():
        """
        Create patches for Qdrant services.
        
        Returns:
            List of patch objects for Qdrant services
        """
        patches = [
            patch('tgbot.services.qdrantus.qdrant_client.upsert'),
            patch('tgbot.services.qdrantus.qdrant_client.search', return_value=[]),
        ]
        
        return patches


class TestDataFactory:
    """Factory for creating test data."""

    @staticmethod
    def create_user_registration_data() -> Dict[str, Any]:
        """
        Create user registration data for testing.
        
        Returns:
            Dict containing user registration data
        """
        return {
            "background_text": "I'm a software developer with 3 years of experience. I want to learn AI and machine learning to advance my career.",
            "expected_mentor_name": "Dr. Sarah Johnson",
            "expected_mentor_age": 42,
            "expected_greeting": "Hello! I'm Dr. Sarah Johnson, and I'm excited to be your AI mentor.",
        }

    @staticmethod
    def create_conversation_test_data() -> Dict[str, Any]:
        """
        Create conversation test data.
        
        Returns:
            Dict containing conversation test data
        """
        return {
            "user_messages": [
                "Hello! I want to learn about AI.",
                "What are the main types of machine learning?",
                "Can you explain supervised learning?",
            ],
            "mentor_responses": [
                "Great! I'd be happy to help you learn about AI.",
                "There are three main types: supervised, unsupervised, and reinforcement learning.",
                "Supervised learning uses labeled training data to learn patterns.",
            ],
            "conversation_history": [
                {"role": "user", "content": "Hello! I want to learn about AI."},
                {"role": "assistant", "content": "Great! I'd be happy to help you learn about AI."},
            ],
        }

    @staticmethod
    def create_subscription_test_data() -> Dict[str, Any]:
        """
        Create subscription test data.
        
        Returns:
            Dict containing subscription test data
        """
        from datetime import datetime, timedelta
        
        return {
            "active_subscription": {
                "is_sub": True,
                "sub_until": datetime.utcnow() + timedelta(days=30),
            },
            "expired_subscription": {
                "is_sub": True,
                "sub_until": datetime.utcnow() - timedelta(days=1),
            },
            "no_subscription": {
                "is_sub": False,
                "sub_until": None,
            },
            "subscription_price": 10000,  # 100 rubles in kopecks
            "mentor_price": 5000,  # 50 rubles in kopecks
        }


class AsyncTestHelpers:
    """Helper functions for async testing."""

    @staticmethod
    async def run_async_test(test_func, *args, **kwargs):
        """
        Run an async test function.
        
        Args:
            test_func: Async test function to run
            *args: Positional arguments for the test function
            **kwargs: Keyword arguments for the test function
            
        Returns:
            Result of the test function
        """
        return await test_func(*args, **kwargs)

    @staticmethod
    def create_async_mock(*args, **kwargs):
        """
        Create an async mock object.
        
        Args:
            *args: Positional arguments for AsyncMock
            **kwargs: Keyword arguments for AsyncMock
            
        Returns:
            AsyncMock: Async mock object
        """
        return AsyncMock(*args, **kwargs)


def assert_user_created(user: DBUser, expected_data: Dict[str, Any]):
    """
    Assert that a user was created with expected data.
    
    Args:
        user: Created user instance
        expected_data: Expected user data
    """
    assert user.id is not None
    assert user.name == expected_data["name"]
    assert user.telegram_id == expected_data["telegram_id"]
    if "username" in expected_data:
        assert user.username == expected_data["username"]


def assert_mentor_created(mentor: DBMentor, expected_data: Dict[str, Any]):
    """
    Assert that a mentor was created with expected data.
    
    Args:
        mentor: Created mentor instance
        expected_data: Expected mentor data
    """
    assert mentor.id is not None
    assert mentor.name == expected_data["name"]
    assert mentor.mentor_age == expected_data["mentor_age"]
    assert mentor.user_id == expected_data["user_id"]


def assert_conversation_created(messages: List[DBConversationMessage], expected_count: int):
    """
    Assert that conversation messages were created.
    
    Args:
        messages: List of created conversation messages
        expected_count: Expected number of messages
    """
    assert len(messages) == expected_count
    for message in messages:
        assert message.id is not None
        assert message.content is not None
        assert message.role in ["user", "assistant"]