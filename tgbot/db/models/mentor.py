"""
Mentor model for storing AI-generated mentor personalities and characteristics.

This module defines the DBMentor model which represents an AI-generated mentor
personality created specifically for a user. Each mentor has unique characteristics,
personality traits, and conversation history.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from tgbot.db.models import Base
from tgbot.db.models.conversation import DBConversationMessage
from tgbot.db.models.mixins import TimestampMixin
from tgbot.db.models.mixins.int_id_pk import IntIdPk
from sqlalchemy.orm import relationship


class DBMentor(IntIdPk, TimestampMixin, Base):
    """
    Mentor model representing an AI-generated mentor personality.
    
    Each mentor is uniquely created for a specific user based on their background
    and goals. The mentor has distinct personality traits, background information,
    and maintains conversation history with the user.
    
    Attributes:
        name: Mentor's name
        mentor_age: Mentor's age (used for personality generation)
        background: Mentor's professional and personal background
        recent_events: Recent events in mentor's life (for context)
        personality_style: Mentor's communication and personality style
        greeting: Initial greeting message from the mentor
        sys_prompt_summary: System prompt summary for AI conversation
        user_id: Foreign key to the user who owns this mentor
        user: Relationship to the user who owns this mentor
        conversation_messages: List of conversation messages with this mentor
    """
    __tablename__ = "mentors"

    # Mentor personality and characteristics
    name: Mapped[str]  # Mentor's name
    mentor_age: Mapped[int]  # Mentor's age for personality generation
    background: Mapped[str] = mapped_column(String(256))  # Professional/personal background
    recent_events: Mapped[str] = mapped_column(String(1024))  # Recent life events for context
    personality_style: Mapped[str] = mapped_column(String(256))  # Communication style
    greeting: Mapped[str] = mapped_column(String(256))  # Initial greeting message
    sys_prompt_summary: Mapped[str] = mapped_column(String(1024))  # AI system prompt summary
    
    # Foreign key relationship to user
    user_id = mapped_column(ForeignKey("users.id"))  # Owner of this mentor
    user = relationship("DBUser", back_populates="mentors")  # User relationship
    
    # Conversation history
    conversation_messages: Mapped[List["DBConversationMessage"]] = relationship(
        "DBConversationMessage", 
        back_populates="mentor", 
        cascade="all, delete-orphan"  # Delete messages when mentor is deleted
    )
