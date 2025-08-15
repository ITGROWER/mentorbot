# db/repositories/conversation.py
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.db.models.conversation import DBConversationMessage
from tgbot.db.repositories.base import SQLAlchemyRepository
from tgbot.services import encryption


class ConversationRepository(SQLAlchemyRepository[DBConversationMessage]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DBConversationMessage)
        self.session = session

    async def create_message(
        self, message: DBConversationMessage
    ) -> DBConversationMessage:
        message.content = encryption.encrypt(message.content)
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        message.content = encryption.decrypt(message.content)
        return message

    async def get_recent_messages(
        self, user_id: int, mentor_id: int, limit: int = 10
    ) -> list[DBConversationMessage]:
        result = await self.session.execute(
            select(DBConversationMessage)
            .where(
                DBConversationMessage.user_id == user_id,
                DBConversationMessage.mentor_id == mentor_id,
            )
            .order_by(DBConversationMessage.created_at.desc())
            .limit(limit)
        )
        messages = result.scalars().all()
        for msg in messages:
            msg.content = encryption.decrypt(msg.content)
        # Возвращаем в порядке возрастания времени (старые первыми)
        return sorted(messages, key=lambda m: m.created_at)

    # Можно добавить методы для получения сообщений по mentor_id и т.д.

    async def count(self, user_id: int) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(DBConversationMessage).where(
                DBConversationMessage.user_id == user_id,
            )
        )
        return result.scalar_one()
