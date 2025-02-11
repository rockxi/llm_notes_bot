
from .db import get_db, Note, User, Task, Thought, Message, Goal
from termcolor import cprint
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import PendingRollbackError
import msg_tmp
from params import max_len

db = next(get_db())
# добавить сообщение
def get_user_by_tg_id(tg_id : str):
    user = db.query(User).filter(User.tg_id == tg_id).first()
    return user
def get_user_by_id(user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    return user

def add_message(tg_id : str, text : str, role : str = 'user', to_message = None):
    user_id = get_user_by_tg_id(tg_id)
    if not user_id: return msg_tmp.user_not_found

    user_id = user_id.id
    if to_message: to_message = str(to_message)

    db_message = Message(user_id = user_id, text = text, role = role, to_message = to_message)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    return 'Сообщение добавлено'

# словарь сообщений
def get_messages_list(tg_id : str):
    user_id = get_user_by_tg_id(tg_id)
    if not user_id: return 404

    user_id = user_id.id
    messages = db.query(Message).filter(Message.user_id == user_id).all()

    messages_list = []

    for msg in messages:
        messages_list.append({'role': msg.role, 'content': msg.text})  
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user: return 404

    context = user.context
    max_len_2 = context if max_len > context else max_len #pyright: ignore

    if len(messages_list) > max_len_2: #pyright: ignore
        messages_list = messages_list[-max_len_2:] 
        
    return messages_list

# удалить задачу
def delete_tasks(number):
    task = db.query(Task).filter(Task.number == number).first()
    if not task: return 404

    db.delete(task)
    db.commit()
    return 'Задача удалена'




 

