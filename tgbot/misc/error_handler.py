"""
Error handling utilities for MentorBot.

This module provides centralized error handling, logging, and user-friendly
error responses for the bot application.
"""

import logging
from typing import Optional, Dict, Any, Callable, Awaitable
from functools import wraps

from aiogram import Bot
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramAPIError

from tgbot.misc.exceptions import (
    MentorBotError,
    UserNotFoundError,
    MentorNotFoundError,
    SubscriptionExpiredError,
    SubscriptionLimitReachedError,
    AIServiceError,
    OpenAIError,
    EmbeddingError,
    VectorDatabaseError,
    ConfigurationError,
    ValidationError,
    EncryptionError,
    PaymentError,
    RateLimitError,
    UserBannedError,
)
from tgbot.misc.logger import logger


class ErrorHandler:
    """Centralized error handler for the bot application."""
    
    def __init__(self, bot: Bot):
        """
        Initialize error handler.
        
        Args:
            bot: Telegram bot instance
        """
        self.bot = bot
        self.logger = logger
    
    async def handle_error(
        self,
        error: Exception,
        message: Optional[Message] = None,
        callback: Optional[CallbackQuery] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Handle an error and send appropriate response to user.
        
        Args:
            error: The exception that occurred
            message: Telegram message (if available)
            callback: Telegram callback query (if available)
            context: Additional context information
        """
        context = context or {}
        
        # Log the error
        self._log_error(error, context)
        
        # Get user-friendly error message
        user_message = self._get_user_message(error)
        
        # Send error message to user
        if message:
            await self._send_error_message(message, user_message)
        elif callback and callback.message:
            await self._send_error_message(callback.message, user_message)
    
    def _log_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """
        Log error with appropriate level and details.
        
        Args:
            error: The exception that occurred
            context: Additional context information
        """
        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
        }
        
        if isinstance(error, MentorBotError):
            error_details.update({
                "error_code": error.error_code,
                "details": error.details,
            })
        
        if isinstance(error, (UserBannedError, UserNotFoundError, MentorNotFoundError)):
            # These are expected errors, log as info
            self.logger.info(f"Expected error: {error.message}", extra=error_details)
        elif isinstance(error, (SubscriptionExpiredError, SubscriptionLimitReachedError)):
            # Business logic errors, log as warning
            self.logger.warning(f"Business logic error: {error.message}", extra=error_details)
        elif isinstance(error, (AIServiceError, VectorDatabaseError, ConfigurationError)):
            # Service errors, log as error
            self.logger.error(f"Service error: {error.message}", extra=error_details)
        else:
            # Unexpected errors, log as critical
            self.logger.critical(f"Unexpected error: {error.message}", extra=error_details)
    
    def _get_user_message(self, error: Exception) -> str:
        """
        Get user-friendly error message based on error type.
        
        Args:
            error: The exception that occurred
            
        Returns:
            str: User-friendly error message
        """
        if isinstance(error, UserBannedError):
            return "You are banned from using this bot. Please contact support if you believe this is an error."
        
        elif isinstance(error, UserNotFoundError):
            return "User not found. Please try starting the bot with /start command."
        
        elif isinstance(error, MentorNotFoundError):
            return "Mentor not found. Please try creating a new mentor or contact support."
        
        elif isinstance(error, SubscriptionExpiredError):
            return "Your subscription has expired. Please renew your subscription to continue using the bot."
        
        elif isinstance(error, SubscriptionLimitReachedError):
            return "You have reached your message limit. Please upgrade your subscription to continue chatting with your mentor."
        
        elif isinstance(error, (OpenAIError, EmbeddingError)):
            return "AI service is temporarily unavailable. Please try again later."
        
        elif isinstance(error, VectorDatabaseError):
            return "Memory service is temporarily unavailable. Please try again later."
        
        elif isinstance(error, ConfigurationError):
            return "Bot configuration error. Please contact support."
        
        elif isinstance(error, ValidationError):
            return "Invalid data provided. Please check your input and try again."
        
        elif isinstance(error, EncryptionError):
            return "Data encryption error. Please contact support."
        
        elif isinstance(error, PaymentError):
            return "Payment processing error. Please try again or contact support."
        
        elif isinstance(error, RateLimitError):
            return "Too many requests. Please wait a moment before trying again."
        
        elif isinstance(error, TelegramAPIError):
            return "Telegram service error. Please try again later."
        
        else:
            return "An unexpected error occurred. Please try again later or contact support if the problem persists."
    
    async def _send_error_message(self, message: Message, error_text: str) -> None:
        """
        Send error message to user.
        
        Args:
            message: Telegram message to reply to
            error_text: Error message to send
        """
        try:
            await message.answer(
                f"❌ {error_text}",
                parse_mode="HTML"
            )
        except Exception as e:
            self.logger.error(f"Failed to send error message: {e}")


def error_handler_decorator(error_handler: ErrorHandler):
    """
    Decorator for handling errors in handler functions.
    
    Args:
        error_handler: ErrorHandler instance
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., Awaitable[None]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as error:
                # Extract message and callback from args
                message = None
                callback = None
                
                for arg in args:
                    if isinstance(arg, Message):
                        message = arg
                    elif isinstance(arg, CallbackQuery):
                        callback = arg
                
                await error_handler.handle_error(error, message, callback)
        
        return wrapper
    return decorator


def safe_execute(
    func: Callable[..., Awaitable[Any]],
    *args,
    error_handler: Optional[ErrorHandler] = None,
    default_return: Any = None,
    **kwargs
) -> Any:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Positional arguments for the function
        error_handler: ErrorHandler instance (optional)
        default_return: Value to return if function fails
        **kwargs: Keyword arguments for the function
        
    Returns:
        Function result or default_return if error occurred
    """
    try:
        return func(*args, **kwargs)
    except Exception as error:
        if error_handler:
            # Log error but don't send user message for background functions
            error_handler._log_error(error, {"function": func.__name__})
        else:
            logger.error(f"Error in {func.__name__}: {error}")
        
        return default_return


async def safe_execute_async(
    func: Callable[..., Awaitable[Any]],
    *args,
    error_handler: Optional[ErrorHandler] = None,
    default_return: Any = None,
    **kwargs
) -> Any:
    """
    Safely execute an async function with error handling.
    
    Args:
        func: Async function to execute
        *args: Positional arguments for the function
        error_handler: ErrorHandler instance (optional)
        default_return: Value to return if function fails
        **kwargs: Keyword arguments for the function
        
    Returns:
        Function result or default_return if error occurred
    """
    try:
        return await func(*args, **kwargs)
    except Exception as error:
        if error_handler:
            error_handler._log_error(error, {"function": func.__name__})
        else:
            logger.error(f"Error in {func.__name__}: {error}")
        
        return default_return