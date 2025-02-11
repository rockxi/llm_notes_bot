from ._imports import * 

async def paginate_tasks(state: FSMContext, tasks_text: str = '', page: int = 1) -> tuple[str, Union[InlineKeyboardMarkup, None]]:    

    if tasks_text == '':
        tasks_text = str(await state.get_value('tasks_text'))

    await state.set_data({'tasks_text': tasks_text})

    active_tasks = []
    completed_tasks = []
    current_section = None
    current_date = None
    
    for line in tasks_text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if '🗓 Ваши задачи:' in line:
            current_section = 'active'
        elif '📝 Выполненые задачи:' in line:
            current_section = 'completed'
        elif line.startswith('📅'):
            current_date = '\n' + line

        elif line.startswith('⏰') or line.startswith('<s>'):
            if current_section == 'active':
                active_tasks.append((current_date, line))
            else:
                completed_tasks.append((current_date, line))
    
    all_tasks = active_tasks + completed_tasks
    
    total_pages = (len(all_tasks) + items_per_page - 1) // items_per_page
    
    page = max(1, min(page, total_pages))

    
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    current_page_tasks = all_tasks[start_idx:end_idx]
    
    text = "🗓 Ваши задачи:\n"
    
    current_date_active = None
    for date, task in current_page_tasks:
        if task in [t[1] for t in active_tasks]:
            if date != current_date_active:
                text += f"{date}\n"
                current_date_active = date
            text += f"{task}\n"
    
    if any(task[1] in [t[1] for t in completed_tasks] for task in current_page_tasks):
        text += "\n📝 Выполненые задачи:\n"
        current_date_completed = None
        for date, task in current_page_tasks:
            if task in [t[1] for t in completed_tasks]:
                if date != current_date_completed:
                    text += f"{date}\n"
                    current_date_completed = date
                text += f"{task}\n"
    
    buttons = []
    
    if page > 1:
        buttons.append(InlineKeyboardButton(text="←", callback_data=f"page_t_{page-1}"))
    
    buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="current_page"))
    
    if page < total_pages:
        buttons.append(InlineKeyboardButton(text="→", callback_data=f"page_t_{page+1}"))
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    
    if total_pages == 0:
        return tasks_text, None

    return text, keyboard
