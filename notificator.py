from komand import func
from komand import delete_tasks
import asyncio
from komand import fetch_tasks 
from datetime import datetime, timedelta
from log import pa
from params import max_days

scheduled_tasks = {}

async def send_notification(bot, id, user_id, text, number, task_time):
    user = await func.get_user_by_id(user_id)
    tg_id = user.tg_id # pyright: ignore
    username = user.username # pyright: ignore
    await pa(f'tg_id={tg_id}\nusername={username}\ntasks={len(scheduled_tasks)}')
    await bot.send_message(chat_id=tg_id, text=func.format_notification(number, text, task_time))

async def notification_task(bot, id, user_id, delay, text, number, task_time): 
    await asyncio.sleep(delay)
    await send_notification(bot, id, user_id, text, number, task_time)
    try:
        scheduled_tasks.pop(id)
    except Exception as e:
        await pa(f'{e.__class__}\n{e}')

async def schedule_notifications(bot):
    tasks = await fetch_tasks()
    for task in tasks:
        id, user_id, task_time, text, number = task
        user = await func.get_user_by_id(user_id)
        if not user: continue
        user_timezone = user.timezone

        now = datetime.now() + timedelta(hours = 3)
        now += user_timezone #pyright: ignore 

        delay = (task_time - now).total_seconds() 

        if delay < -86400 * max_days:

            await pa(f'task {number} deleted by time')
            delete_tasks(number)

        if delay >= 0:
            if id in scheduled_tasks:
                scheduled_tasks[id].cancel()

            scheduled_tasks[id] = asyncio.create_task(notification_task(bot, id, user_id, delay, text, number, task_time))

async def periodic_schedule_notifications(bot, interval=60):
    while True:
        await schedule_notifications(bot)
        await asyncio.sleep(interval)



# async def schedule_notifications_2(bot):
#     tasks = await fetch_tasks()
#     for task in tasks:
#         id, user_id, task_time, text, number = task
#         user = await func.get_user_by_id(user_id)
#         if not user: continue
#         user_timezone = user.timezone
#
#         now = datetime.now() + timedelta(hours=3)
#         now += user_timezone #pyright: ignore 
#
#         if now.minute == task_time.minute:
#
#             asyncio.create_task(send_notification(bot, id, user_id, text, number, task_time))
# async def minute_schedule_notification(bot):
#     while True:
#         await schedule_notifications_2(bot)
#         await asyncio.sleep(60)
#
