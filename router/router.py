from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from inspect import signature
from termcolor import cprint
 
import router.voice as voice
import msg_tmp
from komand import LLM
from komand import sync_func
from log import pa
from keyboards import keyboardable
from random import random



router = Router()
llm = LLM()


def format_response(message):
    for m in msg_tmp.stop_list:
        if m in message: 
            return msg_tmp.instrument_error
    return message




async def answer(response, msg, reply_markup = None):
    sync_func.add_message(str(msg.from_user.id), response, 'assistant', msg.message_id) 

    if random() <= 0.001:
        sync_func.add_message(str(msg.from_user.id), msg_tmp.liza_message, 'assistant', msg.message_id) 
        await msg.answer(msg_tmp.liza_message, parse_mode = 'HTML')
        await msg.answer_sticker(msg_tmp.liza_sticker)

    if reply_markup:
        return await msg.answer(response, parse_mode = 'HTML', reply_markup = reply_markup)

    return await msg.answer(response, parse_mode = 'HTML')




@router.message()
async def _(msg: Message, state: FSMContext):
    if not msg.from_user: return 
    if msg.sticker: cprint(f'{msg.sticker.file_id}', 'green')
    reply_markup = None
    
    id       =  str(msg.from_user.id)
    username =  str(msg.from_user.username)
    text     =  str(msg.text)

    if msg.voice: 
        text = await voice.recognize(msg, answer)
    if text == 400: return
    if username != 'rockxi':
        msg_to_user = await pa(f'[{username} : {id}{" voice" if msg.voice else ""}] : {text}') 
    await state.update_data(data = {'tg_id': id, 'username': username, 'role': 'user'})

    messages = sync_func.get_messages_list(id)
    sync_func.add_message(id, text)
    if not msg.bot is None: await msg.bot.send_chat_action(id, 'typing')

    if messages == 404: text = '/start' 
   
    potential_command = text.split()[0]
    
    if '/' == potential_command[0]:
        if potential_command not in llm.get_commands_list():  
            return await answer(msg_tmp.command_not_found, msg)
            
        function = llm.get_command(potential_command)
        if function == None: return await answer(msg_tmp.command_not_found, msg)
          
        if len(signature(function).parameters) > 1:
            com_text = text.replace(potential_command, '')
            if com_text    ==  '': return await answer(msg_tmp.no_arguments, msg)
            if com_text[0] == ' ': com_text = com_text[1:]
            response = await function(state, com_text)
        else:
            response = await function(state)


    else:
        response = await llm.inv(text, messages, state) 


    response = format_response(response) 

    potential_command = await state.get_value('command')
    kfunc = keyboardable(potential_command)
    
    if kfunc:
        response, reply_markup = await kfunc(state, response)

    if username != 'rockxi':
        await pa(f'[assistant] : {response}', from_bot = msg_to_user.message_id) #pyright: ignore    

    await answer(response, msg, reply_markup)



