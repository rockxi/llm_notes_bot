from .system.db import get_db_async, get_db, Note, User, Task, Thought, Message, Goal
from sqlalchemy.exc import IntegrityError
import msg_tmp
from datetime import datetime, timedelta
from sqlalchemy.future import select
from log import p, pa
from itertools import groupby
from termcolor import cprint 


# db = next(get_db())
async def get_user_by_tg_id(tg_id : str):
    async with get_db_async() as db:
        result = await db.execute(
            select(User).filter(User.tg_id == tg_id)
        )
        user = result.scalars().first()
        return user
async def get_user_by_id(user_id: int):
    async with get_db_async() as db:
        result = await db.execute(
            select(User).filter(User.id == user_id)
        )
        user = result.scalars().first()
        return user

def text_to_int_args(number):
    try:
        if isinstance(number, str):
            number = number.split(' ') #pyright: ignore 

        number = list(map(int, number))
        return number
    except Exception as e: 
        return [f'{e}, {e.__class__}']

def text_to_time(time_text):  
    if '::' in time_text:
        hours, mins = time_text.split('::')
        try:
            time = (datetime.now() + timedelta(hours = 3)) + timedelta(minutes=int(mins), hours=int(hours))
            return time

        except Exception as e:
            return f'{e}, {e.__class__}'
    
    if 'days:' in time_text:
        time_text = time_text.replace('days:', '')
        time_text = time_text.split(' ')
        days, time = time_text
        try:
            hours, mins = time.split(':')
            time = (datetime.now() + timedelta(hours = 3)) + timedelta(days = int(days))
            time = time.replace(hour=int(hours), minute=int(mins))
            return time
        except Exception as e: 
            return f'{e}, {e.__class__}'

    try:
        time = datetime.strptime(time_text, '%Y-%m-%d %H:%M')
        return time
    except Exception as e: 
        return f'{e}, {e.__class__}'

def format_tasks(tasks):
    current_time = datetime.now() + timedelta(hours=3)
    # Разделяем задачи на актуальные и просроченные
    actual_tasks = []
    expired_tasks = []
    for task in tasks:
        if task.time > current_time:
            actual_tasks.append(task)
        else:
            expired_tasks.append(task)
    def get_date_str(task):
        return task.time.strftime('%d.%m.%Y')
    def format_task_group(tasks, is_expired=False):
        if not tasks:
            return ""
        result = ""

        sorted_tasks = sorted(tasks, key=lambda x: x.time)
        for date_str, day_tasks in groupby(sorted_tasks, key=get_date_str):
            result += f"📅 {date_str}:\n"
            
            for task in day_tasks:
                time_str = task.time.strftime('%H:%M')
                task_text = f"⏰ {time_str} | #{task.number}: {task.text}"
                # Зачёркиваем если задача выполнена или просрочена
                if task.done or is_expired:
                    task_text = f"<s>{task_text}</s>"
                result += f"{task_text}\n"
            
            result += "\n"
        
        return result
    task_string = "🗓 Ваши задачи:\n\n"
    # Сначала добавляем актуальные задачи
    task_string += format_task_group(actual_tasks)
    # Затем добавляем просроченные задачи
    if expired_tasks:
        task_string += "📝 Выполненые задачи:\n\n"
        task_string += format_task_group(expired_tasks, is_expired=True)
    
    return task_string.rstrip()
def format_notes(notes):
    cprint([note.text for note in notes], 'yellow')
    if not notes:
        return "📝 У вас пока нет заметок"
    
    # Сортируем заметки по номеру в порядке убывания
    sorted_notes = sorted(notes, key=lambda x: x.number, reverse=True)
    
    # Формируем заголовок с количеством заметок
    total_notes = len(sorted_notes)
    note_string = f"📝 Ваши заметки (всего: {total_notes})\n\n"
    
    # Добавляем заметки с группировкой по 5
    for i, note in enumerate(sorted_notes, 1):
        note_string += f"📌 #{note.number}: {note.text}\n"
    
    return note_string
def format_response(message):
    for m in msg_tmp.stop_list:
        if m in message: 
            return msg_tmp.instrument_error
    return message
def format_notification(number, text, time):
    time_str = time.strftime('%H:%M')
    return f'🔔 Напоминаю!\n\n📌 {time_str} | #{number}: {text}'



    


async def add_user(state): # создать нового пользователя
    username = await state.get_value('username')
    tg_id = await state.get_value('tg_id')
    role = await state.get_value('role')

    if role is None:
        role = 'user'

    db_user = User(username=username, tg_id=tg_id, role=role)

    if username == 'rockxi':
        role = 'admin'

    try:
        async with get_db_async() as db:
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)

    except IntegrityError:
        await db.rollback() #pyright: ignore
        await pa(f'Попытка повторной регистрации {username}')
        db_user = await get_user_by_tg_id(tg_id)

    return msg_tmp.start_message

async def add_note(state, text: str): # добавить заметку
    tg_id = await state.get_value('tg_id')
    await state.update_data({'command': '/add_note'})
    user = await get_user_by_tg_id(tg_id)

    if not user:
        print(tg_id)
        return msg_tmp.user_not_found

    user_id = user.id

    db_note = Note(user_id=user_id, text=text)
    async with get_db_async() as db:
        db.add(db_note)
        await db.commit()
        await db.refresh(db_note)

    return msg_tmp.note_added

async def notes(state): # получить заметки
    tg_id = await state.get_value('tg_id')
    await state.update_data({'command': '/n'})
    user = await get_user_by_tg_id(tg_id)
    if not user:
        return msg_tmp.user_not_found
    user_id = user.id

    async with get_db_async() as db:
        result = await db.execute(
            select(Note).filter(Note.user_id == user_id)
        )
        notes = result.scalars().all()

    if not notes:
        return msg_tmp.note_empty

    return format_notes(notes)

async def delete_notes(state, number: list): # удалить заметку
    number = text_to_int_args(number)
    await state.update_data({'command': '/delete_notes'})

    tg_id = await state.get_value('tg_id')
    user = await get_user_by_tg_id(tg_id)
    if not user:
        return msg_tmp.user_not_found
    user_id = user.id

    async with get_db_async() as db:
        result = await db.execute(
            select(Note).filter(Note.user_id == user_id)
        )
        notes = result.scalars().all()

        for note in notes:
            if note.number in number:
                await db.delete(note)

        await db.commit()

    return msg_tmp.note_deleted

async def add_task(state, text): 
    from komand import parse_task_and_time as ptat

    d = ptat(text)
    text, time_text = d['text'], d['time_text']

    if time_text == '':
        return msg_tmp.time_parse_error

    tg_id = await state.get_value('tg_id')
    user = await get_user_by_tg_id(tg_id)
    await state.update_data({'command': '/add_task'})
    

    if not user:
        return msg_tmp.user_not_found

    user_id = user.id

    time = text_to_time(time_text)

    db_task = Task(user_id=user_id, text=text, time=time)
    async with get_db_async() as db:
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)

    if isinstance(time, datetime):
        time_text = datetime.strftime(time, '%H:%M %d.%m.%y')

    return msg_tmp.task_added(time_text)

async def tasks(state):
    tg_id = await state.get_value('tg_id')
    await state.update_data({'command': '/t'})
    user = await get_user_by_tg_id(tg_id)

    if not user:
        return msg_tmp.user_not_found
    user_id = user.id

    async with get_db_async() as db:
        result = await db.execute(
            select(Task).filter(Task.user_id == user_id)
        )
        tasks = result.scalars().all()

    if not tasks:
        return msg_tmp.task_empty
    return format_tasks(tasks)

async def delete_tasks(state, number: list):
    number = text_to_int_args(number)

    tg_id = await state.get_value('tg_id')
    await state.update_data({'command': '/delete_tasks'})
    user = await get_user_by_tg_id(tg_id)
    if not user:
        return msg_tmp.user_not_found

    user_id = user.id

    async with get_db_async() as db:
        result = await db.execute(
            select(Task).filter(Task.user_id == user_id)
        )
        tasks = result.scalars().all()

        for task in tasks:
            if task.number in number:
                await db.delete(task)

        await db.commit()

    return msg_tmp.task_deleted

async def set_task_status(state, number: list):
    number = text_to_int_args(number)

    tg_id = await state.get_value('tg_id')
    await state.update_data({'command': '/done'})
    user = await get_user_by_tg_id(tg_id)
    if not user:
        return msg_tmp.user_not_found

    user_id = user.id

    async with get_db_async() as db:
        result = await db.execute(
            select(Task).filter(Task.user_id == user_id)
        )
        tasks = result.scalars().all()

        for task in tasks:
            if task.number in number:
                if task.done:          #pyright: ignore
                    task.done = False  #pyright: ignore
                else:
                    task.done = True   #pyright: ignore

        await db.commit()

    return msg_tmp.task_done

async def clear_context(state):
    tg_id = await state.get_value('tg_id')
    await state.update_data({'command': '/clear'})
    async with get_db_async() as db:
        result = await db.execute(
            select(User).filter(User.tg_id == tg_id)
        )
        user = result.scalars().first()
        if not user:
            return 404

        user.context = 0 #pyright: ignore
        await db.commit()

    return msg_tmp.context_cleared

async def help(state):
    await state.update_data({'command': '/help'})
    return msg_tmp.help_message

async def change_timezone(state, time_now: str):
    tg_id = await state.get_value('tg_id')
    await state.update_data({'command': '/change_timezone'})
    async with get_db_async() as db:
        result = await db.execute(
            select(User).filter(User.tg_id == tg_id)
        )
        user = result.scalars().first()
        if not user:
            return 404

        if time_now == 't':
            user_time = datetime.now() + user.timezone #pyright: ignore
            return msg_tmp.chose_timezone(user_time.strftime('%H:%M'))

        from komand import parse_time as pt
        user_time = text_to_time(pt(time_now))
        if not isinstance(user_time, datetime):
            return msg_tmp.timezone_error

        time_delta = user_time.hour - datetime.now().hour

        if time_delta < 0:
            time_delta += 24

        time_delta = timedelta(hours=time_delta)
        try:
            user.timezone = time_delta #pyright: ignore
            now = datetime.now()
            now += time_delta
        except Exception as e:
            await pa(f'Exception in timezone {e}, {e.__class__}\n time_delta {time_delta}, user_time {user_time}')
            return msg_tmp.timezone_error

        await db.commit()

    return msg_tmp.timezone_changed(now.strftime('%H:%M'))

async def summary_notes(state):

    note_string = await notes(state)
    await state.update_data({'command': '/summary_notes'})
    from komand import summary_notes as sn
    await pa(sn(str(note_string)))

    return sn(str(note_string))
 

