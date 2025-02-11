import logging
from aiogram import Bot
from telebot import TeleBot
from params import logs_token, admin_id

bot      = Bot(token=logs_token)
sync_bot = TeleBot(logs_token)


def p(t): 
    t = str(t)
    logging.info(t)     
    sync_bot.send_message(admin_id, t, parse_mode='HTML')


async def pa(t, from_bot = None):
    t = str(t)
    logging.info(t)

    if not from_bot:
        msg = await bot.send_message(admin_id, t)
        return msg
    else:
        await bot.send_message(admin_id, t, reply_to_message_id=from_bot, parse_mode='HTML')
