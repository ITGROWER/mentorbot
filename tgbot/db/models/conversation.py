from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from tgbot.db.models import Base
from tgbot.db.models.mixins import TimestampMixin
from tgbot.db.models.mixins.int_id_pk import IntIdPk
from sqlalchemy.orm import relationship


class DBConversationMessage(IntIdPk, TimestampMixin, Base):
    __tablename__ = "conversation_messages"

    role: Mapped[str] = mapped_column(String(16))  # "user" или "assistant"
    content: Mapped[str] = mapped_column(String(4096))
    is_summary: Mapped[bool] = mapped_column(unique=False, default=False)

    # Отношения
    user_id = mapped_column(ForeignKey("users.id"))
    user = relationship("DBUser", back_populates="conversation_messages")
    mentor_id = mapped_column(ForeignKey("mentors.id"))
    mentor = relationship("DBMentor", back_populates="conversation_messages")
