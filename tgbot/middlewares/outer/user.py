from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, cast

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update, User

from tgbot.db.models import DBUser

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from tgbot.db.repositories.repository import Repository


class DBUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        event = cast(Update, event)
        aiogram_user: User = data["event_from_user"]
        session: AsyncSession = data["session"]
        repo: Repository = data["repo"]
        user = await repo.users.get(telegram_id=aiogram_user.id)

        if user is None:
            try:
                user = DBUser.from_aiogram(aiogram_user)
                await repo.users.create(user)
                await session.commit()
            except Exception as e:
                # Handle race condition: user might have been created by another request
                await session.rollback()
                user = await repo.users.get(telegram_id=aiogram_user.id)
                if user is None:
                    # If still None after rollback, re-raise the exception
                    raise e
        if user.is_ban:
            if event.message:
                await event.message.answer("Вы заблокированы")
            elif event.callback_query and event.callback_query.message:
                await event.callback_query.message.answer("Вы заблокированы")
            return

        data["db_user"] = user
        return await handler(event, data)

