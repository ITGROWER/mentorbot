"""
Pytest configuration and shared fixtures for MentorBot tests.

This module provides common fixtures, test configuration, and setup
that can be used across all test modules.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import AsyncGenerator, Generator

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from tgbot.config import Config, CommonConfig, PostgresConfig, RedisConfig, ProviderConfig
from tgbot.db.models import Base
from tgbot.db.repositories.repository import Repository
from tgbot.factory.dispatcher import create_dispatcher
from tgbot.factory.bot import create_bot


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Create an instance of the default event loop for the test session.
    
    This fixture ensures that all async tests use the same event loop
    and properly handle cleanup.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config() -> Config:
    """
    Create a test configuration with mock values.
    
    Returns:
        Config: Test configuration with safe default values
    """
    return Config(
        common=CommonConfig(
            bot_token="test_token",
            admins=[123456789],
            encryption_key="test_encryption_key",
            encryption_on=False,  # Disable encryption for tests
        ),
        redis=RedisConfig(
            use_redis=False,  # Use memory storage for tests
            host="localhost",
            port=6379,
            password="",
        ),
        postgres=PostgresConfig(
            host="localhost",
            port=5432,
            user="test_user",
            password="test_password",
            db="test_db",
            enable_logging=False,
        ),
        provider_config=ProviderConfig(
            token="test_provider_token",
            currency="RUB",
            price=10000,  # 100 rubles in kopecks
            mentor_price=5000,  # 50 rubles in kopecks
            enabled=True,
        ),
    )


@pytest.fixture
async def test_engine():
    """
    Create an in-memory SQLite database for testing.
    
    Returns:
        AsyncEngine: SQLAlchemy async engine for testing
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session.
    
    Args:
        test_engine: The test database engine
        
    Yields:
        AsyncSession: Database session for testing
    """
    async_session = async_sessionmaker(test_engine, expire_on_commit=False)
    
    async with async_session() as session:
        yield session


@pytest.fixture
async def test_repository(test_session: AsyncSession) -> Repository:
    """
    Create a test repository with database session.
    
    Args:
        test_session: The test database session
        
    Returns:
        Repository: Repository instance for testing
    """
    return Repository(session=test_session)


@pytest.fixture
async def test_bot(test_config: Config) -> Bot:
    """
    Create a test bot instance.
    
    Args:
        test_config: Test configuration
        
    Returns:
        Bot: Test bot instance
    """
    return await create_bot(test_config)


@pytest.fixture
async def test_dispatcher(test_config: Config) -> Dispatcher:
    """
    Create a test dispatcher with memory storage.
    
    Args:
        test_config: Test configuration
        
    Returns:
        Dispatcher: Test dispatcher instance
    """
    return await create_dispatcher(test_config)


@pytest.fixture
def mock_openai_service():
    """
    Create mock OpenAI service for testing.
    
    Returns:
        dict: Mock service functions
    """
    return {
        "init_mentor": AsyncMock(return_value='{"name": "Test Mentor", "mentor_age": 35, "background": "Test background", "recent_events": "Test events", "greeting": "Hello! I am your test mentor.", "sys_prompt_summary": "Test prompt", "personality_style": "Friendly", "brief_background": "User background", "goal": "User goal"}'),
        "reply_from_mentor": AsyncMock(return_value="This is a test mentor response."),
        "create_embeddings": AsyncMock(return_value=[0.1, 0.2, 0.3, 0.4, 0.5]),
    }


@pytest.fixture
def mock_qdrant_service():
    """
    Create mock Qdrant service for testing.
    
    Returns:
        dict: Mock service functions
    """
    return {
        "store_message": MagicMock(),
        "retrieve_history": MagicMock(return_value=["Previous message 1", "Previous message 2"]),
    }


@pytest.fixture
def sample_user_data():
    """
    Create sample user data for testing.
    
    Returns:
        dict: Sample user data
    """
    return {
        "name": "Test User",
        "username": "testuser",
        "telegram_id": "123456789",
        "brief_background": "I am a software developer",
        "goal": "Learn AI and machine learning",
        "is_sub": False,
        "is_reg": False,
        "is_ban": False,
    }


@pytest.fixture
def sample_mentor_data():
    """
    Create sample mentor data for testing.
    
    Returns:
        dict: Sample mentor data
    """
    return {
        "name": "Test Mentor",
        "mentor_age": 35,
        "background": "Experienced software engineer with 10+ years in AI",
        "recent_events": "Recently completed a machine learning course",
        "personality_style": "Friendly and encouraging",
        "greeting": "Hello! I'm here to help you learn AI and machine learning.",
        "sys_prompt_summary": "You are a helpful AI mentor specializing in software development and AI.",
    }


@pytest.fixture
def sample_conversation_data():
    """
    Create sample conversation data for testing.
    
    Returns:
        list: Sample conversation messages
    """
    return [
        {"role": "user", "content": "Hello, I want to learn about AI"},
        {"role": "assistant", "content": "Great! I'd be happy to help you learn about AI. What specific area interests you most?"},
        {"role": "user", "content": "I'm interested in machine learning"},
        {"role": "assistant", "content": "Machine learning is a fascinating field! Let's start with the basics."},
    ]