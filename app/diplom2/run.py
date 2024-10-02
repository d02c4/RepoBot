import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import TOKEN, DB_URL
from app.middlewares.user_middlewares import UserMiddleware
from app.handlers import handlers, callback_query, func
from app.callbacks import pagination
from app.FSM import FSM_states
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from tortoise import Tortoise


async def on_startup() -> None:
    await Tortoise.init(
        db_url=DB_URL,
        modules={"models": ["app.models.user"]}
    )


async def on_shutdown() -> None:
    await Tortoise.close_connections()


async def main():
    bot = Bot(token=TOKEN)
    await on_startup()
    dp = Dispatcher()
    await bot.delete_webhook(True)
    dp.include_routers(handlers.router)
    # dp.include_routers(callback_query.router)
    dp.include_routers(pagination.router)
    dp.include_routers(FSM_states.router)
    # dp.include_router(sender.router)
    # dp.message.middleware(UserMiddleware)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
