import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties

from app.database import init_db
from app.handlers import router
from app.openai_client import initialize_documents
from config import TOKEN

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await init_db()
    await initialize_documents()
    await dp.start_polling(bot)


if __name__ == '__main__':
    # на проде закомментировать, т.к. вывод в терминал занимает много времени
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
