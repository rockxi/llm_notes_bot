import logging
from log import pa
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from params import token
from router import router, callback_router
from notificator import periodic_schedule_notifications


async def main():
    await pa('Подключаемся...')
    bot = Bot(token=token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    dp.include_router(callback_router)
    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(periodic_schedule_notifications(bot))

    await pa('Подключeно.')
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
