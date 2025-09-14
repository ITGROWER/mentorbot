"""
User model for storing Telegram user information and mentoring data.

This module defines the DBUser model which represents a user in the system,
including their personal information, subscription status, and relationships
with mentors and conversation messages.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from tgbot.db.models import Base
from tgbot.db.models.conversation import DBConversationMessage
from tgbot.db.models.mentor import DBMentor
from tgbot.db.models.mixins import TimestampMixin
from tgbot.db.models.mixins.int_id_pk import IntIdPk
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from aiogram.types import User


class DBUser(IntIdPk, TimestampMixin, Base):
    """
    User model representing a Telegram user in the mentoring system.
    
    Stores user profile information, subscription status, and maintains
    relationships with mentors and conversation history. Users can have
    multiple mentors and conversation messages associated with them.
    
    Attributes:
        name: User's full name from Telegram
        username: Telegram username (optional)
        brief_background: User's background information for AI mentor creation
        goal: User's goals and objectives for mentoring
        telegram_id: Unique Telegram user ID
        sub_until: Subscription expiration date (None if no active subscription)
        is_sub: Whether user has an active subscription
        is_reg: Whether user has completed initial registration
        is_ban: Whether user is banned from using the bot
        mentors: List of mentors associated with this user
        conversation_messages: List of conversation messages with mentors
    """
    __tablename__ = "users"

    # Basic user information
    name: Mapped[str]  # User's full name from Telegram
    username: Mapped[str | None] = mapped_column(String(64))  # Telegram username (optional)
    brief_background: Mapped[str | None] = mapped_column(String(512))  # User background for AI
    goal: Mapped[str | None] = mapped_column(String(512))  # User's goals and objectives
    telegram_id: Mapped[str | None] = mapped_column(String(32), unique=True)  # Unique Telegram ID

    # Subscription and status information
    sub_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)  # Subscription expiry
    is_sub: Mapped[bool] = mapped_column(unique=False, default=False)  # Active subscription status
    is_reg: Mapped[bool] = mapped_column(unique=False, default=False)  # Registration completion
    is_ban: Mapped[bool] = mapped_column(Boolean, default=False)  # Ban status
    
    # Relationships
    mentors: Mapped[List["DBMentor"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan"  # Delete mentors when user is deleted
    )
    conversation_messages: Mapped[List["DBConversationMessage"]] = relationship(
        "DBConversationMessage", 
        back_populates="user", 
        cascade="all, delete-orphan"  # Delete messages when user is deleted
    )

    @classmethod
    def from_aiogram(cls, user: User) -> DBUser:
        """
        Create a DBUser instance from an aiogram User object.
        
        This factory method extracts relevant information from the Telegram
        user object and creates a new database user record.
        
        Args:
            user: aiogram User object from Telegram API
            
        Returns:
            DBUser: New user instance with data from Telegram user
        """
        return cls(
            name=user.full_name, 
            username=user.username, 
            telegram_id=str(user.id)
        )
