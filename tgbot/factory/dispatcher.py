"""
Dispatcher factory module for creating and configuring the aiogram Dispatcher.

This module handles the creation of the main Dispatcher instance with all necessary
components: storage configuration, middleware setup, router registration, and
database connection management.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from redis.asyncio import Redis

from tgbot.db.create_pool import create_pool
from tgbot.handlers.admins.admin import admin_router
from tgbot.handlers.users.user import user_router
from tgbot.handlers.users.buy_sub import buy_router
from tgbot.handlers.users.mentors import mentor_router
from tgbot.handlers.users.main_menu import main_menu_router
from tgbot.middlewares.inner import ThrottlingMiddleware
from tgbot.middlewares.outer import DBSessionMiddleware, DBUserMiddleware

if TYPE_CHECKING:
    from aiogram.fsm.storage.base import BaseStorage

    from tgbot.config import Config


def _setup_outer_middlewares(dispatcher: Dispatcher, config: Config) -> None:
    """
    Set up outer middlewares that run before request processing.
    
    Outer middlewares handle cross-cutting concerns like database session management
    and user authentication. They run before the main request processing pipeline.
    
    Args:
        dispatcher: The dispatcher instance to configure
        config: Application configuration for database connection
    """
    # Create database connection pool and store it in dispatcher context
    pool = dispatcher["session_pool"] = create_pool(
        dsn=config.postgres.build_dsn(),
        enable_logging=config.postgres.enable_logging,
    )
    
    # Add database session middleware for automatic session management
    dispatcher.update.outer_middleware(DBSessionMiddleware(session_pool=pool))
    
    # Add user middleware for automatic user creation and retrieval
    dispatcher.update.outer_middleware(DBUserMiddleware())


def _setup_inner_middlewares(dispatcher: Dispatcher) -> None:
    """
    Set up inner middlewares that run during request processing.
    
    Inner middlewares handle request-specific concerns like throttling and
    callback query responses. They run after outer middlewares but before handlers.
    
    Args:
        dispatcher: The dispatcher instance to configure
    """
    # Add throttling middleware to prevent spam and abuse
    dispatcher.message.middleware(ThrottlingMiddleware())
    
    # Add callback answer middleware for automatic callback query responses
    dispatcher.callback_query.middleware(CallbackAnswerMiddleware())


def _setup_routers(dispatcher: Dispatcher) -> None:
    """
    Register all router modules with the dispatcher.
    
    Routers contain the actual message and callback handlers for different
    parts of the bot functionality. The order of registration matters for
    handler precedence.
    
    Args:
        dispatcher: The dispatcher instance to configure
    """
    # Register all routers in order of precedence
    # Note: main_menu_router also handles mentor purchases
    dispatcher.include_routers(
        user_router,        # Core user interaction handlers
        main_menu_router,   # Main menu and navigation handlers
        buy_router,         # Subscription and payment handlers
        admin_router,       # Administrative functions
        mentor_router,      # Mentor-specific functionality
    )


async def create_dispatcher(config: Config) -> Dispatcher:
    """
    Create and configure a complete Dispatcher instance.
    
    Sets up storage (Redis or memory), configures all middlewares, registers
    routers, and returns a fully configured dispatcher ready for use.
    
    Args:
        config: Application configuration containing all necessary settings
        
    Returns:
        Dispatcher: Fully configured dispatcher instance
        
    Raises:
        Exception: If Redis connection fails or other configuration errors occur
    """
    # Configure FSM storage based on configuration
    storage: BaseStorage
    if config.redis.use_redis:
        # Use Redis for persistent FSM storage (recommended for production)
        storage = RedisStorage(
            Redis(
                host=config.redis.host,
                port=config.redis.port,
                password=config.redis.password,
            ),
        )
    else:
        # Use memory storage (suitable for development/testing)
        storage = MemoryStorage()

    # Create dispatcher with storage and configuration
    dispatcher: Dispatcher = Dispatcher(
        name="main_dispatcher",
        storage=storage,
        config=config,
    )
    
    # Set up all middlewares and routers
    _setup_outer_middlewares(dispatcher=dispatcher, config=config)
    _setup_inner_middlewares(dispatcher=dispatcher)
    _setup_routers(dispatcher=dispatcher)
    
    return dispatcher
