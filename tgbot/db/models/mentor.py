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
    __tablename__ = "mentors"

    name: Mapped[str]
    mentor_age: Mapped[int]
    background: Mapped[str] = mapped_column(String(256))
    recent_events: Mapped[str] = mapped_column(String(1024))
    personality_style: Mapped[str] = mapped_column(String(256))
    greeting: Mapped[str] = mapped_column(String(256))
    sys_prompt_summary: Mapped[str] = mapped_column(String(1024))
    user_id = mapped_column(ForeignKey("users.id"))
    user = relationship("DBUser", back_populates="mentors")
    conversation_messages: Mapped[List["DBConversationMessage"]] = relationship(
        "DBConversationMessage", back_populates="mentor", cascade="all, delete-orphan"
    )
