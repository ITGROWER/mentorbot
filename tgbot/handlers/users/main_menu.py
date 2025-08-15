from datetime import datetime
import logging

from aiogram import F, Router
from aiogram.enums import ChatType, ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.types.labeled_price import LabeledPrice

from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.config import Config, create_config
from tgbot.db.repositories.repository import Repository
from tgbot.keyboards.inline.inline import main_menu_keyboard
from tgbot.texts import (
    BILLING_MENU_TEMPLATE,
    BUY_SUB_BUTTON_TEXT,
    DELETE_ACCOUNT_BUTTON_TEXT,
    INVITE_TEXT,
    MENTORS_MENU_TEMPLATE,
    MENU_HTML,
    PROFILE_MENU_TEMPLATE,
    SETTINGS_MENU_TEMPLATE,
    UPGRADE_SUB_BUTTON_TEXT,
    NEW_MENTOR_BUTTON_TEXT,
    PAYMENTS_DISABLED_TEXT,
)
from tgbot.misc.states import BuyMentorState, StartForm

main_menu_router = Router()
main_menu_router.message.filter(F.chat.type == ChatType.PRIVATE)
main_menu_router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)


@main_menu_router.message(F.text == "В меню", StateFilter("*"))
@main_menu_router.message(Command(commands="menu"), StateFilter("*"))
async def main_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        MENU_HTML,
        reply_markup=main_menu_keyboard,
        parse_mode=ParseMode.HTML,
    )


@main_menu_router.callback_query(F.data == "profile")
async def profile_menu(
    callback_query: CallbackQuery,
    state: FSMContext,
    repo: Repository,
):
    await state.clear()
    user = await repo.users.get(telegram_id=callback_query.from_user.id)
    now = datetime.utcnow()
    active_sub = (
        user.is_sub and user.sub_until and user.sub_until > now
    )
    sub_status = (
        f"активна до {user.sub_until:%d.%m.%Y}" if active_sub else "не оформлена"
    )
    text = PROFILE_MENU_TEMPLATE.format(
        name=user.name,
        goal=user.goal or "не указана",
        sub_status=sub_status,
    )
    kb = None
    config = create_config()
    if not active_sub and config.provider_config.enabled:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=BUY_SUB_BUTTON_TEXT, callback_data="buy_sub")]
            ]
        )
    await callback_query.message.answer(
        text, reply_markup=kb, parse_mode=ParseMode.HTML
    )


@main_menu_router.callback_query(F.data == "invite_friend")
async def referral_system(
    callback_query: CallbackQuery,
    state: FSMContext,
):
    await state.clear()
    await callback_query.message.answer(INVITE_TEXT, parse_mode=ParseMode.HTML)


@main_menu_router.callback_query(F.data == "mentors")
async def mentors_menu(
    callback_query: CallbackQuery,
    state: FSMContext,
    repo: Repository,
):
    await state.clear()
    user = await repo.users.get(telegram_id=callback_query.from_user.id)
    mentors = await repo.mentors.get_all(user_id=user.id)
    if mentors:
        mentors_list = "\n".join(
            f"• {m.name}, {m.mentor_age}" for m in mentors
        )
    else:
        mentors_list = "Пока нет ни одного ментора"
    text = MENTORS_MENU_TEMPLATE.format(mentors_list=mentors_list)
    buttons = [
        [
            InlineKeyboardButton(
                text=f"Удалить {m.name}", callback_data=f"delete_mentor:{m.id}"
            )
        ]
        for m in mentors
    ]
    config = create_config()
    if config.provider_config.enabled:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=NEW_MENTOR_BUTTON_TEXT, callback_data="buy_mentor"
                )
            ]
        )
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback_query.message.answer(
        text, reply_markup=kb, parse_mode=ParseMode.HTML
    )


@main_menu_router.callback_query(F.data == "buy_mentor")
async def start_buy_mentor(callback_query: CallbackQuery, state: FSMContext):
    try:
        current_state = await state.get_state()
        if current_state is not None:
            await state.clear()
        config: Config = create_config()
        if not config.provider_config.enabled:
            await callback_query.message.answer(PAYMENTS_DISABLED_TEXT)
            return
        try:
            splitconfig = config.provider_config.token.split(":")[1]
        except Exception as e:
            logging.error(e)
            splitconfig = []
        if splitconfig == "TEST":
            await callback_query.message.reply(
                "Для оплаты используйте данные тестовой карты: 1111 1111 1111 1026, 12/22, CVC 000."
            )

        price = config.provider_config.mentor_price
        prices = [LabeledPrice(label="Новый ментор", amount=price)]
        await state.set_state(BuyMentorState.buying)
        await callback_query.bot.send_invoice(
            chat_id=callback_query.message.chat.id,
            title="Покупка ментора",
            description="Оплата нового ментора",
            payload="mentor_paid",
            provider_token=config.provider_config.token,
            currency=config.provider_config.currency,
            prices=prices,
            need_phone_number=True,
            send_phone_number_to_provider=True,
            provider_data=config.provider_config.provider_data(
                price, "Покупка ментора"
            ),
        )
    except Exception as e:
        logging.error(f"Ошибка при покупке ментора: {e}")
        await callback_query.message.answer("Произошла ошибка при покупке ментора!")
        current_state = await state.get_state()
        if current_state is not None:
            await state.clear()


@main_menu_router.message(BuyMentorState.buying, F.successful_payment)
async def mentor_payment_success(message: Message, state: FSMContext):
    await message.answer(
        "✅ Оплата прошла успешно. Расскажите немного о себе для создания нового ментора."
    )
    await state.set_state(StartForm.about_user)


@main_menu_router.callback_query(F.data == "settings")
async def settings_menu(
    callback_query: CallbackQuery,
    state: FSMContext,
    repo: Repository,
):
    await state.clear()
    user = await repo.users.get(telegram_id=callback_query.from_user.id)
    active_sub = (
        user.is_sub and user.sub_until and user.sub_until > datetime.utcnow()
    )
    buttons: list[list[InlineKeyboardButton]] = []
    config = create_config()
    if not active_sub and config.provider_config.enabled:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=UPGRADE_SUB_BUTTON_TEXT, callback_data="buy_sub"
                )
            ]
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text=DELETE_ACCOUNT_BUTTON_TEXT, callback_data="delete_account"
            )
        ]
    )
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback_query.message.answer(
        SETTINGS_MENU_TEMPLATE, reply_markup=kb, parse_mode=ParseMode.HTML
    )


@main_menu_router.callback_query(F.data == "delete_account")
async def delete_account(
    callback_query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    repo: Repository,
) -> None:
    await state.clear()
    user = await repo.users.get(telegram_id=callback_query.from_user.id)
    if user:
        await session.delete(user)
        await session.commit()
    await callback_query.message.answer(
        "Ваш аккаунт удалён вместе с переписками и менторами.",
        parse_mode=ParseMode.HTML,
    )


@main_menu_router.callback_query(F.data == "billing")
async def billing_menu(
    callback_query: CallbackQuery,
    state: FSMContext,
    repo: Repository,
):
    await state.clear()
    user = await repo.users.get(telegram_id=callback_query.from_user.id)
    now = datetime.utcnow()
    active_sub = (
        user.is_sub and user.sub_until and user.sub_until > now
    )
    if active_sub:
        remaining = user.sub_until - now
        days_left = remaining.days
        expires_line = (
            f"Осталось {days_left} дн." if days_left > 0 else "Меньше суток"
        )
        status_line = "✅ Подписка активна"
        kb = None
    else:
        status_line = "❌ Подписка не оформлена"
        expires_line = ""
        config = create_config()
        kb = None
        if config.provider_config.enabled:
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=BUY_SUB_BUTTON_TEXT, callback_data="buy_sub")]
                ]
            )
    text = BILLING_MENU_TEMPLATE.format(
        status_line=status_line, expires_line=expires_line
    )
    await callback_query.message.answer(
        text, reply_markup=kb, parse_mode=ParseMode.HTML
    )
