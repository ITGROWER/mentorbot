from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.db.models.mentor import DBMentor
from tgbot.db.repositories.base import SQLAlchemyRepository


class MentorRepository(SQLAlchemyRepository[DBMentor]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DBMentor)

    # async def get(self, telegram_id: int) -> DBMentor | None:
    #     return await super().get_one(telegram_id=str(telegram_id))

    async def get_by_user_id(self, user_id) -> DBMentor | None:
        return await super().get_one(user_id=user_id)