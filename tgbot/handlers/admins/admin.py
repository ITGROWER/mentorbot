from datetime import datetime, timedelta
import csv
import io

from aiogram import F, Router
from aiogram.enums import ChatType, ParseMode
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    BufferedInputFile,
)
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.db.repositories.repository import Repository
from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.inline.admin import admin_main_keyboard
from tgbot.misc.logger import logger
from tgbot.misc.states import AdminPanel

admin_router = Router()
admin_router.message.filter(AdminFilter(), F.chat.type == ChatType.PRIVATE)
admin_router.callback_query.filter(
    AdminFilter(),
    F.message.chat.type == ChatType.PRIVATE,
)


@admin_router.message(Command(commands="admin"))
async def admin_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Админ панель", reply_markup=admin_main_keyboard)


# Gift subscription
@admin_router.callback_query(F.data == "admin_gift_sub")
async def gift_sub_start(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(
        "Введите username пользователя для подарка подписки:"
    )
    await state.set_state(AdminPanel.gift_sub_username)


@admin_router.message(AdminPanel.gift_sub_username)
async def gift_sub_finish(
    message: Message,
    state: FSMContext,
    repo: Repository,
    session: AsyncSession,
) -> None:
    username = message.text.strip().lstrip("@")
    user = await repo.users.get_by_username(username=username)
    if not user:
        await message.answer("Пользователь не найден")
    else:
        user.is_sub = True
        user.sub_until = datetime.utcnow() + timedelta(days=30)
        await repo.users.update(user)
        await session.commit()
        await message.answer("Подписка активирована")
        try:
            await message.bot.send_message(
                int(user.telegram_id),
                "🎉 Ваша подписка активирована! Добро пожаловать в премиум.",
            )
        except TelegramAPIError as e:
            logger.error(e)
    await state.clear()


# Ban user
@admin_router.callback_query(F.data == "admin_ban_user")
async def ban_user_start(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer("Введите Telegram ID пользователя для блокировки:")
    await state.set_state(AdminPanel.ban_user_id)


@admin_router.message(AdminPanel.ban_user_id)
async def ban_user_finish(
    message: Message,
    state: FSMContext,
    repo: Repository,
    session: AsyncSession,
) -> None:
    try:
        user_id = int(message.text)
    except ValueError:
        await message.answer("Некорректный ID")
        await state.clear()
        return
    user = await repo.users.get(telegram_id=user_id)
    if not user:
        await message.answer("Пользователь не найден")
    else:
        user.is_ban = True
        await repo.users.update(user)
        await session.commit()
        await message.answer("Пользователь заблокирован")
    await state.clear()


# Direct message
@admin_router.callback_query(F.data == "admin_direct_message")
async def direct_message_start(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer("Введите Telegram ID пользователя:")
    await state.set_state(AdminPanel.direct_user_id)


@admin_router.message(AdminPanel.direct_user_id)
async def direct_message_get_text(message: Message, state: FSMContext) -> None:
    try:
        user_id = int(message.text)
    except ValueError:
        await message.answer("Некорректный ID")
        await state.clear()
        return
    await state.update_data(dm_user_id=user_id)
    await message.answer("Введите сообщение (HTML):")
    await state.set_state(AdminPanel.direct_message)


@admin_router.message(AdminPanel.direct_message)
async def direct_message_send(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    user_id = data.get("dm_user_id")
    try:
        await message.bot.send_message(
            user_id, message.html_text or message.text, parse_mode=ParseMode.HTML
        )
        await message.answer("Сообщение отправлено")
    except TelegramAPIError as e:
        logger.error(e)
        await message.answer("Не удалось отправить сообщение")
    await state.clear()


# Broadcast
@admin_router.callback_query(F.data == "admin_broadcast")
async def broadcast_start(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer("Отправьте сообщение или фото для рассылки:")
    await state.set_state(AdminPanel.broadcast_message)


@admin_router.message(F.photo, AdminPanel.broadcast_message)
async def broadcast_photo(message: Message, state: FSMContext) -> None:
    file_id = message.photo[-1].file_id
    await state.update_data(
        broadcast_type="photo",
        file_id=file_id,
        caption=message.caption or "",
    )
    await message.answer("Если нужна кнопка, отправьте 'Текст - URL', иначе '-' :")
    await state.set_state(AdminPanel.broadcast_button)


@admin_router.message(AdminPanel.broadcast_message)
async def broadcast_text(message: Message, state: FSMContext) -> None:
    await state.update_data(broadcast_type="text", text=message.text)
    await message.answer("Если нужна кнопка, отправьте 'Текст - URL', иначе '-' :")
    await state.set_state(AdminPanel.broadcast_button)


@admin_router.message(AdminPanel.broadcast_button)
async def broadcast_finish(
    message: Message,
    state: FSMContext,
    repo: Repository,
) -> None:
    data = await state.get_data()
    button_input = message.text
    kb: InlineKeyboardMarkup | None = None
    if button_input and button_input != "-":
        try:
            btn_text, btn_url = map(str.strip, button_input.split("-", 1))
            kb = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text=btn_text, url=btn_url)]]
            )
        except (ValueError, TypeError) as e:
            logger.error(e)
            kb = None
    users = await repo.users.get_all(is_ban=False)
    sent = 0
    blocked = 0
    failed = 0
    for user in users:
        try:
            chat_id = int(user.telegram_id)
            if data.get("broadcast_type") == "photo":
                await message.bot.send_photo(
                    chat_id,
                    data.get("file_id"),
                    caption=data.get("caption"),
                    parse_mode=ParseMode.HTML,
                    reply_markup=kb,
                )
            else:
                await message.bot.send_message(
                    chat_id,
                    data.get("text"),
                    parse_mode=ParseMode.HTML,
                    reply_markup=kb,
                )
            sent += 1
        except TelegramForbiddenError as e:
            blocked += 1
            logger.error(e)
        except TelegramAPIError as e:
            failed += 1
            logger.error(e)
            continue
    total = len(users)
    await message.answer(
        "Рассылка завершена.\n"
        f"Всего пользователей: {total}\n"
        f"Отправлено: {sent}\n"
        f"Не отправлено: {failed + blocked}\n"
        f"Заблокировали бота: {blocked}"
    )
    await state.clear()


# Statistics
@admin_router.callback_query(F.data == "admin_stats")
async def show_stats(callback: CallbackQuery, repo: Repository) -> None:
    users = await repo.users.get_all()
    messages = await repo.conversations.get_all()
    total_users = len(users)
    subs = len([u for u in users if u.is_sub])
    banned = len([u for u in users if u.is_ban])
    total_messages = len(messages)
    await callback.message.answer(
        "Статистика:\n"
        f"Всего пользователей: {total_users}\n"
        f"Активных подписок: {subs}\n"
        f"Заблокированных: {banned}\n"
        f"Сообщений в переписках: {total_messages}",
    )
    await callback.answer()


# Export users
@admin_router.callback_query(F.data == "admin_export_users")
async def export_users(callback: CallbackQuery, repo: Repository) -> None:
    users = await repo.users.get_all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "id",
            "name",
            "username",
            "telegram_id",
            "is_sub",
            "is_reg",
            "is_ban",
            "sub_until",
            "created_at",
        ]
    )
    for u in users:
        writer.writerow(
            [
                u.id,
                u.name,
                u.username,
                u.telegram_id,
                u.is_sub,
                u.is_reg,
                u.is_ban,
                u.sub_until,
                u.created_at,
            ]
        )
    file_bytes = output.getvalue().encode()
    await callback.message.answer_document(
        BufferedInputFile(file_bytes, filename="users.csv")
    )
    await callback.answer()


# Export conversations
@admin_router.callback_query(F.data == "admin_export_conversations")
async def export_conversations(callback: CallbackQuery, repo: Repository) -> None:
    messages = await repo.conversations.get_all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "id",
            "user_id",
            "mentor_id",
            "role",
            "content",
            "is_summary",
            "created_at",
        ]
    )
    for m in messages:
        writer.writerow(
            [
                m.id,
                m.user_id,
                m.mentor_id,
                m.role,
                m.content,
                m.is_summary,
                m.created_at,
            ]
        )
    file_bytes = output.getvalue().encode()
    await callback.message.answer_document(
        BufferedInputFile(file_bytes, filename="conversations.csv")
    )
    await callback.answer()

