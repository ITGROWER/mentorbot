import logging
from aiogram import F, Router
from tgbot.config import Config, create_config
from tgbot.db.repositories.repository import Repository
from tgbot.factory import bot
from tgbot.misc.logger import logger
from tgbot.misc.states import BuyState
from tgbot.texts import PAYMENTS_DISABLED_TEXT
from aiogram.types import CallbackQuery, PreCheckoutQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatType
from aiogram.types.labeled_price import LabeledPrice
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

buy_router = Router()
buy_router.message.filter(F.chat.type == ChatType.PRIVATE)
buy_router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)


@buy_router.callback_query(F.data == "buy_sub")
async def start_buy_sub(callback_query: CallbackQuery, state: FSMContext):
    try:
        # Проверка состояния и его очистка
        current_state = await state.get_state()
        if current_state is not None:
            await state.clear()  # чтобы свободно перейти сюда из любого другого состояния

        config: Config = create_config()
        if not config.provider_config.enabled:
            await callback_query.message.answer(PAYMENTS_DISABLED_TEXT)
            return
        try:
            splitconfig = config.provider_config.token.split(":")[1]
        except (IndexError, AttributeError) as e:
            logger.error(f"Failed to parse provider token: {e}")
            splitconfig = ""
        if splitconfig == "TEST":
            await callback_query.message.reply(
                "Для оплаты используйте данные тестовой карты: 1111 1111 1111 1026, 12/22, CVC 000."
            )

        price = config.provider_config.price
        prices = [LabeledPrice(label="Оплата заказа", amount=price)]
        await state.set_state(BuyState.buying)
        await callback_query.bot.send_invoice(
            chat_id=callback_query.message.chat.id,
            title="Покупка",
            description="Оплата бота",
            payload="bot_paid",
            provider_token=config.provider_config.token,
            currency=config.provider_config.currency,
            prices=prices,
            need_phone_number=True,
            send_phone_number_to_provider=True,
            provider_data=config.provider_config.provider_data(
                price, "Подписка на месяц"
            ),
        )
    except Exception as e:
        logging.error(f"Ошибка при выполнении команды /buy: {e}")
        await callback_query.message.answer("Произошла ошибка при обработке команды!")
        current_state = await state.get_state()
        if current_state is not None:
            await state.clear()


@buy_router.pre_checkout_query(lambda q: True)
async def process_pre_checkout(pre_checkout: PreCheckoutQuery):
    await pre_checkout.bot.answer_pre_checkout_query(pre_checkout.id, ok=True)


@buy_router.message(BuyState.buying, F.successful_payment)
async def handle_successful_payment(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    repo: Repository,
):
    user_id = message.from_user.id
    user = await repo.users.get(telegram_id=user_id)
    user.is_sub = True
    user.sub_until = datetime.utcnow() + timedelta(days=30)
    await repo.users.update(user)
    await session.commit()
    await message.answer("✅ Оплата прошла успешно. Подписка активирована!")
    await state.clear()
