"""
Bot factory module for creating and configuring the Telegram bot instance.

This module handles the creation of the main Bot instance with proper configuration,
including default properties, command setup, and token management.
"""

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from tgbot.config import Config


async def _set_default_commands(bot: Bot) -> None:
    """
    Set up default bot commands for the Telegram interface.
    
    Configures the bot's command menu that users can access via the / command.
    Commands are displayed in the bot's interface and provide quick access
    to main functionality.
    
    Args:
        bot: The Telegram bot instance to configure commands for
    """
    user_commands = [
        BotCommand(command="start", description="Start the bot and begin mentoring"),
        BotCommand(command="menu", description="Open main menu")
    ]
    await bot.set_my_commands(user_commands)


async def create_bot(config: Config) -> Bot:
    """
    Create and configure a new Telegram bot instance.
    
    Initializes the bot with the provided configuration, sets up default properties
    for message parsing, and configures bot commands.
    
    Args:
        config: Application configuration containing bot token and settings
        
    Returns:
        Bot: Configured Telegram bot instance ready for use
        
    Raises:
        Exception: If bot token is invalid or bot creation fails
    """
    # Create bot instance with token and default properties
    bot = Bot(
        token=config.common.bot_token.get_secret_value(),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,  # Enable HTML parsing for rich text formatting
        ),
    )
    
    # Configure bot commands for user interface
    await _set_default_commands(bot)
    
    return bot
