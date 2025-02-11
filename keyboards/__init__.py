from .paginate_notes import paginate_notes
from .paginate_tasks import paginate_tasks
from typing import Union

keys_tuple = [
    (['/notes', '/n'], paginate_notes),
    (['/tasks', '/t'], paginate_tasks),   
]

def keyboardable(command : Union[str, None]):
    for i in keys_tuple:
        if command in i[0]: return i[1]
