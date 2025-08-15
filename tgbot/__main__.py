import asyncio
from typing import TYPE_CHECKING

from tgbot.config import Config, create_config
from tgbot.factory.bot import create_bot
from tgbot.factory.dispatcher import create_dispatcher
from tgbot.factory.runners import run_polling
from tgbot.misc.logger import logger, setup_logger
from tgbot.services.qdrantus import init_qdrant
from tgbot.services import encryption

if TYPE_CHECKING:
    from aiogram import Bot, Dispatcher


async def main() -> None:
    setup_logger()
    init_qdrant()
    config: Config = create_config()
    encryption.setup(
        config.common.encryption_key.get_secret_value(),
        enabled=config.common.encryption_on,
    )
    dispatcher: Dispatcher = await create_dispatcher(config)
    bot: Bot = await create_bot(config)

    return await run_polling(dispatcher=dispatcher, bot=bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping bot")
