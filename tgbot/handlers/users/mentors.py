from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.db.repositories.repository import Repository

mentor_router = Router()


@mentor_router.message(F.text == "Список менторов")
async def list_mentors(message: Message, state: FSMContext, repo: Repository):
    user = await repo.users.get(telegram_id=message.from_user.id)
    mentors = await repo.mentors.get_all(user_id=user.id)
    kb = [
        [
            InlineKeyboardButton(
                text=f"Удалить {m.name}", callback_data=f"delete_mentor:{m.id}"
            )
        ]
        for m in mentors
    ]
    await message.answer(
        text="Ваши менторы: ", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )


@mentor_router.callback_query(F.data.startswith("delete_mentor:"))
async def delete_mentor(
    callback_query: CallbackQuery,
    session: AsyncSession,
    repo: Repository,
) -> None:
    mentor_id = int(callback_query.data.split(":", 1)[1])
    await repo.mentors.delete(mentor_id)
    await session.commit()
    await callback_query.message.answer("Ментор удалён")


@mentor_router.message(F.text == "Последний ментор")
async def last_mentor(message: Message): ...


# @mentor_router.message(F.text == )
