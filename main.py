import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
from middlewares import ModerationMiddleware
from handlers import start_router, sender_router, receiver_router, chat_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN topilmadi! .env faylini tekshiring.")
        sys.exit(1)

    logger.info("DB ishga tushirilmoqda...")
    await init_db()
    logger.info("DB tayyor ✓")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher(storage=MemoryStorage())

    # Middlewares
    dp.message.middleware(ModerationMiddleware())
    dp.callback_query.middleware(ModerationMiddleware())

    # Routers — order matters!
    # sender_router first: handles deep_link=True before start_router's fallback
    dp.include_router(sender_router)
    dp.include_router(start_router)
    dp.include_router(receiver_router)
    dp.include_router(chat_router)

    logger.info("Bot ishga tushdi 🚀")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("Bot to'xtatildi.")


if __name__ == "__main__":
    asyncio.run(main())
