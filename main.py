import asyncio
import logging
import os

from aiogram import Dispatcher, Bot, Router

from bot.callbacks_handlers import router as callbacks_router
from bot.commands_handlers import router as commands_router
from bot.states_handlers import router as states_router


async def main():
    dp = Dispatcher()

    telegram_token = os.environ.get('TELEGRAM_TOKEN')
    bot = Bot(token=telegram_token)

    logging.basicConfig(level=logging.INFO)

    router = Router()
    router.include_routers(states_router, commands_router, callbacks_router)

    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
