from params import token
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from komand.system.db import get_db, User

async def sm(chat_id, text):
    bot = Bot(token=token)
    try:
        await bot.send_message(chat_id=chat_id, text=text)
    except:
        pass
    return

if __name__ == "__main__":
    db = next(get_db())
    W = db.query(User).all()
    message = 'Привет! Давненько мы не общались...\n\nЯ немного обновилась, Тимоха (шиза) пофиксил баг с указанием времени (наверное).\n\nТеперь уведомления работают по-лучше.\n\nПоболтаем?'
    print([i.username + i.tg_id for i in W])
    # for i in W:
    #     asyncio.run(sm(i.tg_id, message))


