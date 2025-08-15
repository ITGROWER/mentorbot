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
    __tablename__ = "users"

    name: Mapped[str]
    username: Mapped[str | None] = mapped_column(String(64))
    brief_background: Mapped[str | None] = mapped_column(String(512))
    goal: Mapped[str | None] = mapped_column(String(512))
    telegram_id: Mapped[str | None] = mapped_column(String(32), unique=True)

    sub_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_sub: Mapped[bool] = mapped_column(unique=False, default=False)
    is_reg: Mapped[bool] = mapped_column(unique=False, default=False)
    is_ban: Mapped[bool] = mapped_column(Boolean, default=False)
    
    mentors: Mapped[List["DBMentor"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    conversation_messages: Mapped[List["DBConversationMessage"]] = relationship(
        "DBConversationMessage", back_populates="user", cascade="all, delete-orphan"
    )

    @classmethod
    def from_aiogram(cls, user: User) -> DBUser:
        return cls(name=user.full_name, username=user.username, telegram_id=str(user.id))
