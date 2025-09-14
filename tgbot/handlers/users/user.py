"""
Core user interaction handlers for the MentorBot.

This module contains the main user-facing functionality including:
- User registration and onboarding
- Mentor creation and management
- Conversation handling with AI mentors
- Subscription and payment integration
- User state management

All handlers are filtered to work only in private chats.
"""

import json
from datetime import datetime
from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.enums.parse_mode import ParseMode

from tgbot.config import Config, create_config

from tgbot.db.models.conversation import DBConversationMessage
from tgbot.db.models.mentor import DBMentor
from tgbot.db.repositories.repository import Repository
from tgbot.misc.logger import logger
from tgbot.misc.states import DialogueWithMentor, StartForm
from tgbot.services.temp_openai import (
    init_mentor,
    reply_from_mentor,
    create_embeddings,
)
from tgbot.services.qdrantus import store_message, retrieve_history
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import ReplyKeyboardRemove

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from tgbot.texts import (
    WELCOME_BACK_MESSAGE,
    WELCOME_HTML,
    AGENT_CREATED_TEMPLATE,
    SUBSCRIPTION_LIMIT_MESSAGE,
    SUBSCRIPTION_EXPIRED_MESSAGE,
    USER_NOT_FOUND,
    MENTOR_NOT_FOUND,
    BUY_SUB_BUTTON_TEXT,
    NO_MENTORS_MESSAGE,
    PAYMENTS_DISABLED_TEXT,
    NEW_MENTOR_BUTTON_TEXT,
)
from tgbot.misc.exceptions import (
    UserNotFoundError,
    MentorNotFoundError,
    SubscriptionExpiredError,
    SubscriptionLimitReachedError,
    UserBannedError,
    AIServiceError,
)
from tgbot.misc.error_handler import error_handler_decorator

# Create router for user handlers
user_router = Router()

# Filter handlers to only work in private chats
user_router.message.filter(F.chat.type == ChatType.PRIVATE)
user_router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)


@user_router.message(CommandStart(), flags={"throttling_key": "default"})
async def user_start(
    message: Message,
    state: FSMContext,
    repo: Repository,
) -> None:
    """
    Handle the /start command for user onboarding and navigation.
    
    This is the main entry point for users interacting with the bot. It handles:
    - New user registration flow
    - Returning user navigation
    - Banned user handling
    - Mentor availability checks
    - Subscription status validation
    
    Args:
        message: The Telegram message object containing user information
        state: FSM context for managing user conversation state
        repo: Database repository for user and mentor data access
    """
    # Clear any existing state to start fresh
    await state.clear()
    logger.info(f"User {message.from_user.id} started the bot")

    # Get or create user record
    user = await repo.users.get(telegram_id=message.from_user.id)
    
    # Check if user is banned
    if user.is_ban:
        await message.answer("You are banned from using this bot")
        await state.clear()
        return
    
    # Handle returning registered users
    if user.is_reg:
        # Check if user has any mentors
        mentors = await repo.mentors.get_all(user_id=user.id)
        if mentors:
            # User has mentors, start conversation mode
            await message.answer(WELCOME_BACK_MESSAGE, reply_markup=ReplyKeyboardRemove())
            await state.set_state(DialogueWithMentor.process)
        else:
            # User is registered but has no mentors
            # Check if they have an active subscription
            active_sub = (
                user.is_sub and user.sub_until and user.sub_until > datetime.utcnow()
            )
            if active_sub:
                # User has active subscription, offer to create new mentor
                kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=f"{NEW_MENTOR_BUTTON_TEXT} (coming soon)",
                                callback_data="buy_mentor",
                            )
                        ]
                    ]
                )
                await message.answer(NO_MENTORS_MESSAGE, reply_markup=kb)
            else:
                # No active subscription, show welcome back message
                await message.answer(
                    WELCOME_BACK_MESSAGE, reply_markup=ReplyKeyboardRemove()
                )
        return
    
    # Handle new user registration
    await message.answer(
        WELCOME_HTML, parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(StartForm.about_user)


@user_router.message(F.text, StartForm.about_user)
async def get_about_user(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    repo: Repository,
) -> None:
    """
    Process user background information and create their first AI mentor.
    
    This handler is triggered when a new user provides their background information
    during the registration process. It:
    - Sends the user's background to AI service to generate mentor personality
    - Updates user profile with extracted information
    - Creates a new mentor record in the database
    - Initializes conversation state with the mentor's greeting
    
    Args:
        message: The Telegram message containing user's background text
        state: FSM context for managing conversation state
        session: Database session for transaction management
        repo: Database repository for data access
    """
    logger.info(f"Processing user background for user {message.from_user.id}")
    
    # Generate AI mentor based on user's background
    resp = await init_mentor(message.text)
    resp_json = json.loads(resp)

    # Get user record and update with extracted information
    user = await repo.users.get(telegram_id=message.from_user.id)
    user.brief_background = resp_json["brief_background"]
    user.goal = resp_json["goal"]
    user.is_reg = True  # Mark user as registered
    await repo.users.update(user)
    await session.commit()

    # Create new mentor record with AI-generated personality
    new_mentor = DBMentor(
        name=resp_json["name"],
        mentor_age=resp_json["mentor_age"],
        background=resp_json["background"],
        recent_events=resp_json["recent_events"],
        greeting=resp_json["greeting"],
        sys_prompt_summary=resp_json["sys_prompt_summary"],
        personality_style=resp_json["personality_style"],
        user=user,
    )
    await repo.mentors.create(new_mentor)
    await session.commit()

    # Send mentor introduction to user
    await message.answer(
        AGENT_CREATED_TEMPLATE.format(
            name=resp_json["name"],
            mentor_age=resp_json["mentor_age"],
            background=resp_json["background"],
            recent_events=resp_json["recent_events"],
            greeting=resp_json["greeting"],
        ),
        parse_mode=ParseMode.HTML,
    )
    
    # Switch to conversation mode
    await state.set_state(DialogueWithMentor.process)
    
    # Initialize conversation history with user's message and mentor's greeting
    conversation_history = [
        {"role": "user", "content": message.text},
        {"role": "assistant", "content": resp_json["greeting"]},
    ]
    await state.update_data(conversation_history=conversation_history)


@user_router.message(
    F.text,
    DialogueWithMentor.process,
    ~F.text.in_({"В меню"}),
    ~F.text.startswith("/menu"),
)
async def dialogue_process(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    repo: Repository,
):
    """
    Process user messages during mentor conversation.
    
    This is the main conversation handler that:
    - Validates user status and subscription
    - Retrieves relevant conversation history using vector search
    - Generates AI mentor responses
    - Stores conversation data for future reference
    - Manages conversation history length
    
    Args:
        message: The Telegram message from the user
        state: FSM context for conversation state management
        session: Database session for transaction management
        repo: Database repository for data access
    """
    user_id = message.from_user.id
    user = await repo.users.get(telegram_id=user_id)

    # Validate user exists
    if not user:
        raise UserNotFoundError(telegram_id=str(user_id))

    # Check if user is banned
    if user.is_ban:
        raise UserBannedError(user.id, str(user_id))

    # Check subscription status and handle expiration
    if user.is_sub and user.sub_until and user.sub_until < datetime.utcnow():
        # Subscription expired, update user status
        user.is_sub = False
        await repo.users.update(user)
        await session.commit()
        
        # Show subscription expired message with purchase option
        buy_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=BUY_SUB_BUTTON_TEXT, callback_data="buy_sub"
                    )
                ]
            ]
        )
        await message.answer(
            SUBSCRIPTION_EXPIRED_MESSAGE,
            reply_markup=buy_kb,
            parse_mode=ParseMode.HTML,
        )
        await state.clear()
        return

    # Check free tier message limit for non-subscribers
    if not user.is_sub:
        message_quantity = await repo.conversations.count(user_id=user.id)
        if message_quantity > 10:  # Free tier limit
            config: Config = create_config()
            if config.provider_config.enabled:
                # Show subscription purchase option
                buy_kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=BUY_SUB_BUTTON_TEXT, callback_data="buy_sub"
                            )
                        ]
                    ],
                )
                price_rub = config.provider_config.price // 100
                await message.answer(
                    SUBSCRIPTION_LIMIT_MESSAGE.format(price=price_rub),
                    reply_markup=buy_kb,
                    parse_mode=ParseMode.HTML,
                )
            else:
                # Payments disabled, show limit message
                await message.answer(PAYMENTS_DISABLED_TEXT)
            await state.clear()
            return

    # Get user's mentor
    mentor = await repo.mentors.get_by_user_id(user.id)
    if not mentor:
        raise MentorNotFoundError(user_id=user.id)

    # Prepare mentor data for AI processing
    mentor_json = dict(
        name=mentor.name,
        mentor_age=mentor.mentor_age,
        background=mentor.background,
        recent_events=mentor.recent_events,
        greeting=mentor.greeting,
        sys_prompt_summary=mentor.sys_prompt_summary,
        personality_style=mentor.personality_style,
        brief_background=user.brief_background,
        goal=user.goal,
    )

    # Get current conversation history from state
    user_data = await state.get_data()
    conversation_history = user_data.get("conversation_history", [])
    
    # Create embeddings for vector search and store user message
    embedding = await create_embeddings(message.text)
    similar_messages = retrieve_history(user_id, embedding, top_k=5)
    store_message(user_id, "user", message.text, embedding)
    
    # Build context from similar past messages
    context_history = (
        [{"role": "system", "content": "\n".join(similar_messages)}]
        if similar_messages
        else []
    )
    
    # Create dialogue keyboard with menu option
    dialogue_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="В меню")]], resize_keyboard=True
    )
    
    # Generate mentor response using AI
    resp = await reply_from_mentor(
        user_msg=message.text,
        conversation_history=context_history + conversation_history,
        mentor_json=json.dumps(mentor_json),
    )
    
    # Send mentor response to user
    await message.answer(resp, reply_markup=dialogue_kb)
    
    # Store assistant response in vector database
    resp_embedding = await create_embeddings(resp)
    store_message(user_id, "assistant", resp, resp_embedding)

    # Update conversation history
    conversation_history.extend(
        [
            {"role": "user", "content": message.text},
            {"role": "assistant", "content": resp},
        ]
    )

    # Store conversation in database
    await repo.conversations.create_message(
        DBConversationMessage(user_id=user.id, role="user", content=message.text)
    )
    await repo.conversations.create_message(
        DBConversationMessage(user_id=user.id, role="assistant", content=resp)
    )

    # Limit conversation history to prevent context overflow
    if len(conversation_history) > 20:
        conversation_history = conversation_history[2:]  # Remove oldest messages

    # Update state with new conversation history
    await state.update_data(conversation_history=conversation_history)
