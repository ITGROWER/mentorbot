import json
from datetime import datetime
from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.enums.parse_mode import ParseMode

from tgbot.config import Config, create_config

from tgbot.db.models.conversation import DBConversationMessage
from tgbot.db.models.mentor import DBMentor
from tgbot.db.repositories.repository import Repository
from tgbot.misc.logger import logger
from tgbot.misc.states import DialogueWithMentor, StartForm
from tgbot.services.temp_openai import (
    init_mentor,
    reply_from_mentor,
    create_embeddings,
)
from tgbot.services.qdrantus import store_message, retrieve_history
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import ReplyKeyboardRemove

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from tgbot.texts import (
    WELCOME_BACK_MESSAGE,
    WELCOME_HTML,
    AGENT_CREATED_TEMPLATE,
    SUBSCRIPTION_LIMIT_MESSAGE,
    SUBSCRIPTION_EXPIRED_MESSAGE,
    USER_NOT_FOUND,
    MENTOR_NOT_FOUND,
    BUY_SUB_BUTTON_TEXT,
    NO_MENTORS_MESSAGE,
    PAYMENTS_DISABLED_TEXT,
    NEW_MENTOR_BUTTON_TEXT,
)

user_router = Router()
user_router.message.filter(F.chat.type == ChatType.PRIVATE)
user_router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)


@user_router.message(CommandStart(), flags={"throttling_key": "default"})
async def user_start(
    message: Message,
    state: FSMContext,
    repo: Repository,
) -> None:
    await state.clear()
    logger.info(message)

    user = await repo.users.get(telegram_id=message.from_user.id)
    if user.is_ban:
        await message.answer("Вы заблокированы")
        await state.clear()
        return
    # TODO сделать инфо о последнем менторе
    if user.is_reg:
        mentors = await repo.mentors.get_all(user_id=user.id)
        if mentors:
            await message.answer(WELCOME_BACK_MESSAGE, reply_markup=ReplyKeyboardRemove())
            await state.set_state(DialogueWithMentor.process)
        else:
            active_sub = (
                user.is_sub and user.sub_until and user.sub_until > datetime.utcnow()
            )
            if active_sub:
                kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=f"{NEW_MENTOR_BUTTON_TEXT} (скоро)",
                                callback_data="buy_mentor",
                            )
                        ]
                    ]
                )
                await message.answer(NO_MENTORS_MESSAGE, reply_markup=kb)
            else:
                await message.answer(
                    WELCOME_BACK_MESSAGE, reply_markup=ReplyKeyboardRemove()
                )
        return
    await message.answer(
        WELCOME_HTML, parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(StartForm.about_user)


@user_router.message(F.text, StartForm.about_user)
async def get_about_user(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    repo: Repository,
) -> None:
    # TODO сделать установку is_reg = True в конце
    logger.info(message.text)
    resp = await init_mentor(message.text)
    resp_json = json.loads(resp)

    user = await repo.users.get(telegram_id=message.from_user.id)
    user.brief_background = resp_json["brief_background"]
    user.goal = resp_json["goal"]
    user.is_reg = True
    await repo.users.update(user)
    await session.commit()

    new_mentor = DBMentor(
        name=resp_json["name"],
        mentor_age=resp_json["mentor_age"],
        background=resp_json["background"],
        recent_events=resp_json["recent_events"],
        greeting=resp_json["greeting"],
        sys_prompt_summary=resp_json["sys_prompt_summary"],
        personality_style=resp_json["personality_style"],
        user=user,
    )
    await repo.mentors.create(new_mentor)
    await session.commit()

    await message.answer(
        AGENT_CREATED_TEMPLATE.format(
            name=resp_json["name"],
            mentor_age=resp_json["mentor_age"],
            background=resp_json["background"],
            recent_events=resp_json["recent_events"],
            greeting=resp_json["greeting"],
        ),
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(DialogueWithMentor.process)
    conversation_history = [
        {"role": "user", "content": message.text},
        {"role": "assistant", "content": resp_json["greeting"]},
    ]
    await state.update_data(conversation_history=conversation_history)


@user_router.message(
    F.text,
    DialogueWithMentor.process,
    ~F.text.in_({"В меню"}),
    ~F.text.startswith("/menu"),
)
async def dialogue_process(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    repo: Repository,
):
    user_id = message.from_user.id
    user = await repo.users.get(telegram_id=user_id)

    if not user:
        await message.answer(USER_NOT_FOUND)
        await state.clear()
        return

    if user.is_ban:
        await message.answer("Вы заблокированы")
        await state.clear()
        return

    if user.is_sub and user.sub_until and user.sub_until < datetime.utcnow():
        user.is_sub = False
        await repo.users.update(user)
        await session.commit()
        buy_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=BUY_SUB_BUTTON_TEXT, callback_data="buy_sub"
                    )
                ]
            ]
        )
        await message.answer(
            SUBSCRIPTION_EXPIRED_MESSAGE,
            reply_markup=buy_kb,
            parse_mode=ParseMode.HTML,
        )
        await state.clear()
        return

    if not user.is_sub:
        message_quantity = await repo.conversations.count(user_id=user.id)
        if message_quantity > 10:
            config: Config = create_config()
            if config.provider_config.enabled:
                buy_kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=BUY_SUB_BUTTON_TEXT, callback_data="buy_sub"
                            )
                        ]
                    ],
                )
                price_rub = config.provider_config.price // 100
                await message.answer(
                    SUBSCRIPTION_LIMIT_MESSAGE.format(price=price_rub),
                    reply_markup=buy_kb,
                    parse_mode=ParseMode.HTML,
                )
            else:
                await message.answer(PAYMENTS_DISABLED_TEXT)
            await state.clear()
            return

    mentor = await repo.mentors.get_by_user_id(user.id)
    if not mentor:
        await message.answer(MENTOR_NOT_FOUND)
        await state.clear()
        return

    mentor_json = dict(
        name=mentor.name,
        mentor_age=mentor.mentor_age,
        background=mentor.background,
        recent_events=mentor.recent_events,
        greeting=mentor.greeting,
        sys_prompt_summary=mentor.sys_prompt_summary,
        personality_style=mentor.personality_style,
        brief_background=user.brief_background,
        goal=user.goal,
    )

    user_data = await state.get_data()
    conversation_history = user_data.get("conversation_history", [])
    embedding = await create_embeddings(message.text)
    similar_messages = retrieve_history(user_id, embedding, top_k=5)
    store_message(user_id, "user", message.text, embedding)
    context_history = (
        [{"role": "system", "content": "\n".join(similar_messages)}]
        if similar_messages
        else []
    )
    dialogue_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="В меню")]], resize_keyboard=True
    )
    resp = await reply_from_mentor(
        user_msg=message.text,
        conversation_history=context_history + conversation_history,
        mentor_json=json.dumps(mentor_json),
    )
    await message.answer(resp, reply_markup=dialogue_kb)
    resp_embedding = await create_embeddings(resp)
    store_message(user_id, "assistant", resp, resp_embedding)

    conversation_history.extend(
        [
            {"role": "user", "content": message.text},
            {"role": "assistant", "content": resp},
        ]
    )

    await repo.conversations.create_message(
        DBConversationMessage(user_id=user.id, role="user", content=message.text)
    )
    await repo.conversations.create_message(
        DBConversationMessage(user_id=user.id, role="assistant", content=resp)
    )

    if len(conversation_history) > 20:
        conversation_history = conversation_history[2:]

    await state.update_data(conversation_history=conversation_history)
