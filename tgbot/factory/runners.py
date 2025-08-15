from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from tgbot.misc.logger import logger
from tgbot.services import broadcaster
from tgbot.services.subscription import (
    notify_expired_subscriptions,
    notify_unpaid_registered_users,
)

if TYPE_CHECKING:
    from aiogram import Bot, Dispatcher
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from tgbot.config import Config


async def on_startup(
    bot: Bot,
    config: Config,
    session_pool: async_sessionmaker[AsyncSession],
) -> None:
    _tasks = [
        asyncio.create_task(notify_expired_subscriptions(bot, session_pool)),
        asyncio.create_task(notify_unpaid_registered_users(bot, session_pool)),
    ]
    await broadcaster.broadcast(bot, config.common.admins, "Бот запущен!")


async def on_shutdown() -> None:
    logger.info("Shutting down...")


async def run_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    dispatcher.startup.register(on_startup)
    dispatcher.shutdown.register(on_shutdown)
    await bot.delete_webhook(drop_pending_updates=True)
    return await dispatcher.start_polling(bot)
