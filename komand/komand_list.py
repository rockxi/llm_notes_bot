from .system.komand import Komand
import komand.func as func

komand_list = [
    Komand(['/start', ], func = func.add_user, tg_only = True),
    Komand('/clear', func = func.clear_context, tg_only = True),
    Komand(['/change_timezone', '/ct'], func = func.change_timezone, tg_only = True),
    Komand('/help', func = func.help, tg_only = True), 

    Komand( # Команда для добавления заметки
        command = ['/add_note', '/an'],
        func = func.add_note,
        description = '''Вызывается если пользователь подаёт запрос на добавление заметки,
        определи границы самой заметки и подай текст заметки на вход просто как строку. ''',
    ),
    Komand( # Команда для получения заметок
        command = ['/notes', '/n'],
        func = func.notes,
        description = '''Вызывается если пользователь подаёт запрос на получение своих заметок. Или скажет "заметки", "мои заметки"''',
    ),
    Komand( # Команда для удаления заметок
        command = ['/delete_notes', '/dn'],
        func = func.delete_notes,
        description = '''Вызывай если пользователь попросит удалить заметки. На вход подаются список из int значений - номеров заметок'''
    ),
    Komand( # Команда для анализа заметок
        command = ['/summary_notes', '/sn'],
        func = func.summary_notes,
        description = '''Вызывается если пользователь попросит вывести сводку по заметкам''',
    ),
    
    Komand( # Команда для добавления задачи
        command =['/add_task', '/at'],
        func = func.add_task,
        description = f'''Вызывается если пользователь подаёт запрос на добавление задачи. 
        определи границы задачи и подай на вход текст задачи в аргументе text
        Из text убери саму просьбу о добавлении задачи
        Пример
        входная строка: "Напомни мне сделать домашнюю работу в 6 вечера"
        text = "сделать домашнюю работу в 6 вечера"
        или например text = "18:30 позвонить маме

        обязательно оставь в сообщении указание на время
        Если пользователь скажет "напомни завтра сделать математику"
        то text = "сделать математику завтра" 
        или при запросе "напомни позвонить бабушке в 18:00" подай на вход text = 'позвонить бабушке в 18:00'
        ''',
        
    ),
    Komand( # Команда для получения задач
        command = ['/tasks', '/t'],
        func = func.tasks,
        description = '''Вызывается если пользователь подаёт запрос на получение своих задач.''',
    ),
    Komand( # Команда для удаления задач
        command = ['/delete_tasks', '/dt'],
        func = func.delete_tasks,
        description = '''Вызывай если пользователь попросит удалить задачи. На вход подаются список из int значений - номеров задач'''
    ),
    Komand( # Команда для отметки задач как выполненные
        command = ['/done_tasks', '/done'],
        func = func.set_task_status,
        description='''Вызывай если пользователь попросит отметить задачи как выполненные, "зачеркнуть" или наоборот, снять эту метку.
        На вход подаются список из int значений - номеров задач'''
    ),
]
