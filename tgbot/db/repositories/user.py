from collections.abc import Sequence
from datetime import datetime
from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.db.models import DBUser
from tgbot.db.repositories.base import SQLAlchemyRepository
from tgbot.services import encryption


class UserRepository(SQLAlchemyRepository[DBUser]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DBUser)

    def _decrypt(self, user: DBUser) -> DBUser:
        if user.brief_background:
            user.brief_background = encryption.decrypt(user.brief_background)
        if user.goal:
            user.goal = encryption.decrypt(user.goal)
        return user

    async def get(self, telegram_id: int) -> DBUser | None:
        user = await super().get_one(telegram_id=str(telegram_id))
        if user:
            self._decrypt(user)
        return user

    async def get_by_username(self, username: str) -> DBUser | None:
        user = await super().get_one(username=username)
        if user:
            self._decrypt(user)
        return user

    async def create(self, instance: DBUser) -> DBUser:
        if instance.brief_background:
            instance.brief_background = encryption.encrypt(instance.brief_background)
        if instance.goal:
            instance.goal = encryption.encrypt(instance.goal)
        created = await super().create(instance)
        return self._decrypt(created)

    async def update(self, instance: DBUser) -> DBUser:
        if instance.brief_background:
            instance.brief_background = encryption.encrypt(instance.brief_background)
        if instance.goal:
            instance.goal = encryption.encrypt(instance.goal)
        updated = await super().update(instance)
        return self._decrypt(updated)

    async def get_expired(self, before: datetime) -> Sequence[DBUser]:
        stmt = select(DBUser).where(
            DBUser.sub_until.is_not(None),
            DBUser.sub_until < before,
        )
        result = await self._session.scalars(stmt)
        users = cast(Sequence[DBUser], result.all())
        for user in users:
            self._decrypt(user)
        return users

    async def get_unpaid_registered(self) -> Sequence[DBUser]:
        stmt = select(DBUser).where(
            DBUser.is_reg.is_(True),
            DBUser.is_sub.is_(False),
        )
        result = await self._session.scalars(stmt)
        users = cast(Sequence[DBUser], result.all())
        for user in users:
            self._decrypt(user)
        return users
