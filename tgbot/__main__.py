"""
Main entry point for MentorBot Telegram bot.

This module initializes and starts the Telegram bot with all necessary components:
- Configuration loading and validation
- Database and Redis connections
- AI services (Qdrant vector database, encryption)
- Bot and dispatcher setup
- Polling loop execution

The bot provides AI-powered personal mentoring through Telegram interface.
"""

import asyncio
from typing import TYPE_CHECKING

from tgbot.config import Config, create_config
from tgbot.factory.bot import create_bot
from tgbot.factory.dispatcher import create_dispatcher
from tgbot.factory.runners import run_polling
from tgbot.misc.logger import logger, setup_logger
from tgbot.services.qdrantus import init_qdrant
from tgbot.services import encryption

if TYPE_CHECKING:
    from aiogram import Bot, Dispatcher


async def main() -> None:
    """
    Main application entry point.
    
    Initializes all bot components in the correct order:
    1. Sets up logging system
    2. Initializes Qdrant vector database for AI embeddings
    3. Loads and validates configuration
    4. Sets up encryption service for sensitive data
    5. Creates dispatcher with all handlers and middlewares
    6. Creates bot instance with proper settings
    7. Starts the polling loop
    
    Raises:
        Exception: Any initialization or runtime errors will be propagated
    """
    # Initialize logging system first
    setup_logger()
    
    # Initialize Qdrant vector database for AI embeddings storage
    init_qdrant()
    
    # Load and validate configuration from environment variables
    config: Config = create_config()
    
    # Setup encryption service for protecting sensitive user data
    encryption.setup(
        config.common.encryption_key.get_secret_value(),
        enabled=config.common.encryption_on,
    )
    
    # Create dispatcher with all handlers, middlewares, and database connections
    dispatcher: Dispatcher = await create_dispatcher(config)
    
    # Create bot instance with proper configuration
    bot: Bot = await create_bot(config)

    # Start the main polling loop
    return await run_polling(dispatcher=dispatcher, bot=bot)


if __name__ == "__main__":
    """
    Application entry point when run directly.
    
    Handles graceful shutdown on KeyboardInterrupt (Ctrl+C) or SystemExit.
    """
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user or system")
