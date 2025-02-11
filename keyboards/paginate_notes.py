from ._imports import * 

async def paginate_notes(state : FSMContext, notes_text : str = '', page: int = 1) -> tuple[str, Union[InlineKeyboardMarkup, None]]: 

    if notes_text == '':
        notes_text = str(await state.get_value('notes_text'))

    await state.set_data({'notes_text' : notes_text})
    
    lines = [line.strip() for line in notes_text.split('\n') if line.strip()]
    
    # Получаем заголовок (первая строка)
    header = lines[0]
    
    # Получаем только заметки (без заголовка)
    notes = [line for line in lines[1:] if line.startswith('📌')]
    
    # Вычисляем общее количество страниц
    total_pages = (len(notes) + items_per_page - 1) // items_per_page
    
    # Проверяем валидность номера страницы
    page = max(1, min(page, total_pages))
    
    # Получаем заметки для текущей страницы
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    current_page_notes = notes[start_idx:end_idx]
    
    text = f"{header}\n\n" + "\n".join(current_page_notes)
    
    buttons = []
    
    if page > 1:
        buttons.append(InlineKeyboardButton(text = "←", callback_data=f"page_n_{page-1}"))
    buttons.append(InlineKeyboardButton(text = f"{page}/{total_pages}", callback_data="current_page"))    
    if page < total_pages:
        buttons.append(InlineKeyboardButton(text = "→", callback_data=f"page_n_{page+1}"))
    
    
    keyboard = InlineKeyboardMarkup(inline_keyboard= [buttons])
    if total_pages == 0:
        return notes_text, None


    return text, keyboard

 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
