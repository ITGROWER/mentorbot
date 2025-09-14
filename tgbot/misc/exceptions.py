"""
Custom exceptions for MentorBot.

This module defines custom exception classes for different types of errors
that can occur in the bot application, providing better error handling
and debugging capabilities.
"""

from typing import Optional, Dict, Any


class MentorBotError(Exception):
    """Base exception class for all MentorBot errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        Initialize MentorBot error.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class DatabaseError(MentorBotError):
    """Database-related errors."""
    pass


class UserNotFoundError(DatabaseError):
    """Raised when a user is not found in the database."""
    
    def __init__(self, telegram_id: Optional[str] = None, user_id: Optional[int] = None):
        """
        Initialize user not found error.
        
        Args:
            telegram_id: Telegram ID that was not found
            user_id: Database user ID that was not found
        """
        if telegram_id:
            message = f"User with Telegram ID {telegram_id} not found"
            details = {"telegram_id": telegram_id}
        elif user_id:
            message = f"User with ID {user_id} not found"
            details = {"user_id": user_id}
        else:
            message = "User not found"
            details = {}
            
        super().__init__(message, "USER_NOT_FOUND", details)


class MentorNotFoundError(DatabaseError):
    """Raised when a mentor is not found in the database."""
    
    def __init__(self, user_id: Optional[int] = None, mentor_id: Optional[int] = None):
        """
        Initialize mentor not found error.
        
        Args:
            user_id: User ID for which mentor was not found
            mentor_id: Mentor ID that was not found
        """
        if user_id:
            message = f"Mentor for user {user_id} not found"
            details = {"user_id": user_id}
        elif mentor_id:
            message = f"Mentor with ID {mentor_id} not found"
            details = {"mentor_id": mentor_id}
        else:
            message = "Mentor not found"
            details = {}
            
        super().__init__(message, "MENTOR_NOT_FOUND", details)


class SubscriptionError(MentorBotError):
    """Subscription-related errors."""
    pass


class SubscriptionExpiredError(SubscriptionError):
    """Raised when user's subscription has expired."""
    
    def __init__(self, user_id: int, expired_at: str):
        """
        Initialize subscription expired error.
        
        Args:
            user_id: ID of the user with expired subscription
            expired_at: When the subscription expired
        """
        message = f"Subscription for user {user_id} expired at {expired_at}"
        super().__init__(message, "SUBSCRIPTION_EXPIRED", {
            "user_id": user_id,
            "expired_at": expired_at
        })


class SubscriptionLimitReachedError(SubscriptionError):
    """Raised when user has reached their message limit."""
    
    def __init__(self, user_id: int, message_count: int, limit: int):
        """
        Initialize subscription limit reached error.
        
        Args:
            user_id: ID of the user who reached the limit
            message_count: Current message count
            limit: Message limit
        """
        message = f"User {user_id} has reached message limit ({message_count}/{limit})"
        super().__init__(message, "SUBSCRIPTION_LIMIT_REACHED", {
            "user_id": user_id,
            "message_count": message_count,
            "limit": limit
        })


class AIServiceError(MentorBotError):
    """AI service-related errors."""
    pass


class OpenAIError(AIServiceError):
    """OpenAI API errors."""
    
    def __init__(self, message: str, api_error: Optional[str] = None):
        """
        Initialize OpenAI error.
        
        Args:
            message: Error message
            api_error: Original API error message
        """
        super().__init__(message, "OPENAI_ERROR", {"api_error": api_error})


class EmbeddingError(AIServiceError):
    """Embedding generation errors."""
    
    def __init__(self, message: str, text: Optional[str] = None):
        """
        Initialize embedding error.
        
        Args:
            message: Error message
            text: Text that failed to embed
        """
        super().__init__(message, "EMBEDDING_ERROR", {"text": text})


class VectorDatabaseError(MentorBotError):
    """Vector database (Qdrant) errors."""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        """
        Initialize vector database error.
        
        Args:
            message: Error message
            operation: Operation that failed
        """
        super().__init__(message, "VECTOR_DB_ERROR", {"operation": operation})


class ConfigurationError(MentorBotError):
    """Configuration-related errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the error
        """
        super().__init__(message, "CONFIGURATION_ERROR", {"config_key": config_key})


class ValidationError(MentorBotError):
    """Data validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            field: Field that failed validation
            value: Value that failed validation
        """
        super().__init__(message, "VALIDATION_ERROR", {"field": field, "value": value})


class EncryptionError(MentorBotError):
    """Encryption/decryption errors."""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        """
        Initialize encryption error.
        
        Args:
            message: Error message
            operation: Encryption operation that failed
        """
        super().__init__(message, "ENCRYPTION_ERROR", {"operation": operation})


class PaymentError(MentorBotError):
    """Payment processing errors."""
    
    def __init__(self, message: str, payment_id: Optional[str] = None):
        """
        Initialize payment error.
        
        Args:
            message: Error message
            payment_id: Payment ID that failed
        """
        super().__init__(message, "PAYMENT_ERROR", {"payment_id": payment_id})


class RateLimitError(MentorBotError):
    """Rate limiting errors."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        """
        Initialize rate limit error.
        
        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
        """
        super().__init__(message, "RATE_LIMIT_ERROR", {"retry_after": retry_after})


class UserBannedError(MentorBotError):
    """Raised when a banned user tries to use the bot."""
    
    def __init__(self, user_id: int, telegram_id: str):
        """
        Initialize user banned error.
        
        Args:
            user_id: Database user ID
            telegram_id: Telegram user ID
        """
        message = f"User {telegram_id} (ID: {user_id}) is banned"
        super().__init__(message, "USER_BANNED", {
            "user_id": user_id,
            "telegram_id": telegram_id
        })