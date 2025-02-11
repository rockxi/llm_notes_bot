from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from keyboards import keyboardable
from log import pa


callback_router = Router()

@callback_router.callback_query(lambda x : x.data.startswith('page_'))
async def _(callback_query: CallbackQuery, state: FSMContext):
    data = callback_query.data
    if not data: return
    command = '/' + str(data.split('_')[1]) 
    page    = int(data.split('_')[2])
    kfunc   = keyboardable(command)

    if not kfunc: return

    text, keyboard = await kfunc(state, page = page)
    if text != 'None':
        await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode = 'HTML')#pyright: ignore
        await pa('text is none')
    await callback_query.answer()

@callback_router.callback_query(lambda x : x.data.startswith('current_page'))
async def _(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer('😜😳😳😳😳😳')
