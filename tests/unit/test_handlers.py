"""
Unit tests for bot handlers.

This module contains tests for all bot handlers including user interaction,
mentor creation, conversation handling, and admin functions.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, User, Chat, CallbackQuery

from tgbot.handlers.users.user import user_router
from tgbot.misc.states import StartForm, DialogueWithMentor


class TestUserHandlers:
    """Test cases for user handlers."""

    @pytest.fixture
    def mock_message(self):
        """Create a mock message for testing."""
        message = MagicMock(spec=Message)
        message.from_user = MagicMock(spec=User)
        message.from_user.id = 123456789
        message.from_user.full_name = "Test User"
        message.from_user.username = "testuser"
        message.text = "Hello, I want to learn about AI"
        message.answer = AsyncMock()
        message.chat = MagicMock(spec=Chat)
        message.chat.type = "private"
        return message

    @pytest.fixture
    def mock_callback_query(self):
        """Create a mock callback query for testing."""
        callback = MagicMock(spec=CallbackQuery)
        callback.from_user = MagicMock(spec=User)
        callback.from_user.id = 123456789
        callback.data = "test_callback"
        callback.message = MagicMock(spec=Message)
        callback.message.chat = MagicMock(spec=Chat)
        callback.message.chat.type = "private"
        callback.answer = AsyncMock()
        callback.message.answer = AsyncMock()
        return callback

    @pytest.fixture
    def mock_state(self):
        """Create a mock FSM context for testing."""
        state = MagicMock(spec=FSMContext)
        state.clear = AsyncMock()
        state.set_state = AsyncMock()
        state.get_data = AsyncMock(return_value={})
        state.update_data = AsyncMock()
        return state

    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository for testing."""
        repo = MagicMock()
        repo.users = MagicMock()
        repo.mentors = MagicMock()
        repo.conversations = MagicMock()
        return repo

    @pytest.mark.asyncio
    async def test_user_start_new_user(self, mock_message, mock_state, mock_repository):
        """Test /start command for new user."""
        # Mock user not found (new user)
        mock_repository.users.get.return_value = None
        
        # Mock user creation
        mock_user = MagicMock()
        mock_user.is_ban = False
        mock_user.is_reg = False
        mock_repository.users.get.return_value = mock_user
        
        # Import and test the handler
        from tgbot.handlers.users.user import user_start
        
        await user_start(mock_message, mock_state, mock_repository)
        
        # Verify state was cleared and set to about_user
        mock_state.clear.assert_called_once()
        mock_state.set_state.assert_called_once_with(StartForm.about_user)
        
        # Verify welcome message was sent
        mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_user_start_banned_user(self, mock_message, mock_state, mock_repository):
        """Test /start command for banned user."""
        # Mock banned user
        mock_user = MagicMock()
        mock_user.is_ban = True
        mock_repository.users.get.return_value = mock_user
        
        from tgbot.handlers.users.user import user_start
        
        await user_start(mock_message, mock_state, mock_repository)
        
        # Verify state was cleared
        mock_state.clear.assert_called()
        
        # Verify ban message was sent
        mock_message.answer.assert_called_with("You are banned from using this bot")

    @pytest.mark.asyncio
    async def test_user_start_registered_user_with_mentors(self, mock_message, mock_state, mock_repository):
        """Test /start command for registered user with mentors."""
        # Mock registered user with mentors
        mock_user = MagicMock()
        mock_user.is_ban = False
        mock_user.is_reg = True
        mock_repository.users.get.return_value = mock_user
        mock_repository.mentors.get_all.return_value = [MagicMock()]  # Has mentors
        
        from tgbot.handlers.users.user import user_start
        
        await user_start(mock_message, mock_state, mock_repository)
        
        # Verify state was set to dialogue process
        mock_state.set_state.assert_called_once_with(DialogueWithMentor.process)

    @pytest.mark.asyncio
    async def test_get_about_user(self, mock_message, mock_state, mock_repository):
        """Test processing user background information."""
        # Mock AI response
        ai_response = {
            "name": "Test Mentor",
            "mentor_age": 35,
            "background": "Experienced software engineer",
            "recent_events": "Completed AI course",
            "greeting": "Hello! I'm your test mentor.",
            "sys_prompt_summary": "You are a helpful AI mentor.",
            "personality_style": "Friendly and encouraging",
            "brief_background": "User background",
            "goal": "User goal",
        }
        
        # Mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_repository.users.get.return_value = mock_user
        
        # Mock session
        mock_session = MagicMock()
        mock_session.commit = AsyncMock()
        
        # Patch AI service
        with patch('tgbot.handlers.users.user.init_mentor', return_value=ai_response) as mock_init_mentor:
            from tgbot.handlers.users.user import get_about_user
            
            await get_about_user(mock_message, mock_state, mock_session, mock_repository)
            
            # Verify AI service was called
            mock_init_mentor.assert_called_once_with(mock_message.text)
            
            # Verify user was updated
            mock_repository.users.update.assert_called_once()
            
            # Verify mentor was created
            mock_repository.mentors.create.assert_called_once()
            
            # Verify state was updated
            mock_state.set_state.assert_called_once_with(DialogueWithMentor.process)
            mock_state.update_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_dialogue_process_subscription_check(self, mock_message, mock_state, mock_repository):
        """Test dialogue process with subscription validation."""
        # Mock user with expired subscription
        mock_user = MagicMock()
        mock_user.is_ban = False
        mock_user.is_sub = True
        mock_user.sub_until = None  # Expired subscription
        mock_repository.users.get.return_value = mock_user
        
        # Mock session
        mock_session = MagicMock()
        mock_session.commit = AsyncMock()
        
        with patch('tgbot.handlers.users.user.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = MagicMock()
            mock_datetime.utcnow.return_value.__lt__ = MagicMock(return_value=True)  # Expired
            
            from tgbot.handlers.users.user import dialogue_process
            
            await dialogue_process(mock_message, mock_state, mock_session, mock_repository)
            
            # Verify subscription was updated
            assert mock_user.is_sub is False
            mock_repository.users.update.assert_called_once()
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_dialogue_process_free_tier_limit(self, mock_message, mock_state, mock_repository):
        """Test dialogue process with free tier message limit."""
        # Mock user without subscription
        mock_user = MagicMock()
        mock_user.is_ban = False
        mock_user.is_sub = False
        mock_user.sub_until = None
        mock_repository.users.get.return_value = mock_user
        
        # Mock message count exceeding limit
        mock_repository.conversations.count.return_value = 15  # Exceeds limit of 10
        
        # Mock session
        mock_session = MagicMock()
        
        with patch('tgbot.handlers.users.user.create_config') as mock_config:
            mock_config.return_value.provider_config.enabled = True
            
            from tgbot.handlers.users.user import dialogue_process
            
            await dialogue_process(mock_message, mock_state, mock_session, mock_repository)
            
            # Verify state was cleared due to limit
            mock_state.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_dialogue_process_successful_conversation(self, mock_message, mock_state, mock_repository):
        """Test successful dialogue process."""
        # Mock user with subscription
        mock_user = MagicMock()
        mock_user.is_ban = False
        mock_user.is_sub = True
        mock_user.sub_until = None
        mock_user.id = 1
        mock_repository.users.get.return_value = mock_user
        
        # Mock mentor
        mock_mentor = MagicMock()
        mock_mentor.name = "Test Mentor"
        mock_mentor.mentor_age = 35
        mock_mentor.background = "Test background"
        mock_mentor.recent_events = "Test events"
        mock_mentor.greeting = "Test greeting"
        mock_mentor.sys_prompt_summary = "Test prompt"
        mock_mentor.personality_style = "Test style"
        mock_repository.mentors.get_by_user_id.return_value = mock_mentor
        
        # Mock session
        mock_session = MagicMock()
        
        # Mock AI services
        with patch('tgbot.handlers.users.user.create_embeddings', return_value=[0.1, 0.2, 0.3]) as mock_embeddings, \
             patch('tgbot.handlers.users.user.retrieve_history', return_value=[]) as mock_retrieve, \
             patch('tgbot.handlers.users.user.store_message') as mock_store, \
             patch('tgbot.handlers.users.user.reply_from_mentor', return_value="Test response") as mock_reply:
            
            from tgbot.handlers.users.user import dialogue_process
            
            await dialogue_process(mock_message, mock_state, mock_session, mock_repository)
            
            # Verify AI services were called
            mock_embeddings.assert_called()
            mock_retrieve.assert_called()
            mock_store.assert_called()
            mock_reply.assert_called()
            
            # Verify conversation was stored
            mock_repository.conversations.create_message.assert_called()
            
            # Verify state was updated
            mock_state.update_data.assert_called()


class TestHandlerIntegration:
    """Integration tests for handler workflows."""

    @pytest.mark.asyncio
    async def test_complete_user_registration_flow(self, test_repository: Repository):
        """Test complete user registration flow from start to mentor creation."""
        # This would be a more comprehensive integration test
        # that tests the entire flow from /start to mentor creation
        pass

    @pytest.mark.asyncio
    async def test_conversation_flow_with_subscription(self, test_repository: Repository):
        """Test conversation flow with active subscription."""
        # This would test the complete conversation flow
        # including subscription validation and message processing
        pass