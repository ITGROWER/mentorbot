from __future__ import annotations

import asyncio
import secrets
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from tgbot.db.repositories.repository import Repository
from tgbot.texts import (
    SUBSCRIPTION_EXPIRED_MESSAGE,
    SUBSCRIPTION_INACTIVE_TEMPLATE,
)

if TYPE_CHECKING:
    from aiogram import Bot
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

PERIOD_NAMES = {
    3: "3 дня",
    14: "две недели",
    30: "месяц",
    182: "полгода",
    365: "год",
}

PROMO_TEXTS = [
    "Не пропустите! Оформите подписку и получите полный доступ уже сегодня.",
    "Ваши возможности ждут оплаты — подпишитесь сейчас!",
    "Активируйте подписку и откройте новые горизонты!",
    "Лучшее время купить подписку — прямо сейчас!",
    "Не оставляйте обучение на паузе — оформите подписку.",
    "Подписка — ключ к эксклюзивным материалам. Оплатите и начните!",
    "Доступ к премиум‑контенту всего в одном шаге — оплатите подписку.",
    "Ваша подписка неактивна. Активируйте её и пользуйтесь всеми функциями.",
    "Вернитесь в игру — оформите подписку и продолжайте.",
    "Продолжайте развитие без ограничений — оплатите подписку.",
]


async def _sleep_until_noon() -> None:
    now = datetime.utcnow()
    target = now.replace(hour=12, minute=0, second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)
    await asyncio.sleep((target - now).total_seconds())


async def notify_expired_subscriptions(
    bot: Bot,
    session_pool: async_sessionmaker[AsyncSession],
) -> None:
    while True:
        await _sleep_until_noon()
        async with session_pool() as session:
            repo = Repository(session)
            now = datetime.utcnow()
            users = await repo.users.get_expired(now)
            for user in users:
                if user.sub_until is None or user.telegram_id is None:
                    continue
                delta = (now - user.sub_until).days
                if delta == 0:
                    text = SUBSCRIPTION_EXPIRED_MESSAGE
                else:
                    period = PERIOD_NAMES.get(delta)
                    if not period:
                        continue
                    text = SUBSCRIPTION_INACTIVE_TEMPLATE.format(period=period)
                if user.is_sub:
                    user.is_sub = False
                    await repo.users.update(user)
                await bot.send_message(int(user.telegram_id), text)
            await session.commit()


async def notify_unpaid_registered_users(
    bot: Bot,
    session_pool: async_sessionmaker[AsyncSession],
) -> None:
    while True:
        await _sleep_until_noon()
        async with session_pool() as session:
            repo = Repository(session)
            users = await repo.users.get_unpaid_registered()
            for user in users:
                if user.telegram_id is None:
                    continue
                text = secrets.choice(PROMO_TEXTS)
                await bot.send_message(int(user.telegram_id), text)
            await session.commit()

