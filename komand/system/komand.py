from pydantic import BaseModel, create_model
from inspect import signature, Parameter
import asyncio
from langchain.tools import StructuredTool
from typing import Optional, Any, Union

class Komand:
    def __init__(self,
                 command: Union[str, list],
                 func,
                 description : str = '',
                 return_direct : bool = True,
                 tg_only : bool = False,
                 llm_only : bool = False
                 ):

        self.command = command
        if isinstance(self.command, list):
            self.name = self.command[0].replace('/', '')
        else:
            self.name = self.command.replace('/', '')
        self.func = func
        self.description = description
        self.tg_only = tg_only
        self.return_direct = return_direct
        self.llm_only = llm_only

    def get_tool(self, state, llm_only = False):
        if self.tg_only: return None

        async def a_func(**kwargs): return await self.func(state, **kwargs)

        return StructuredTool(
            name = self.name,
            coroutine= a_func,
            # func = s_func, 
            description = self.description,
            args_schema = self._generate_args_schema(),
            return_direct = self.return_direct,
        )
    
    def _generate_args_schema(self):
        sig = signature(self.func)
        parameters = sig.parameters

        # Фильтруем параметр state
        parameters = {
            name: param for name, param in parameters.items()
            if name != 'state'
        }

        # Если параметров нет, создаем пустой класс
        if not parameters:
            return type(f"{self.name}Input", (BaseModel,), {})

        # Создаем поля для модели
        fields = {}
        for name, param in parameters.items():
            if param.kind not in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY):
                continue
            
            field_type = param.annotation if param.annotation != Parameter.empty else str
            
            # Создаем описание поля
            field_info = {
                "type": field_type,
                "required": param.default == Parameter.empty
            }
            
            if param.default != Parameter.empty:
                field_info["default"] = param.default

            fields[name] = field_info

        # Создаем и возвращаем класс модели
        return type(f"{self.name}Input", (BaseModel,), {
            "__annotations__": {name: field["type"] for name, field in fields.items()},
            "__module__": __name__,
            **{name: field.get("default", ...) for name, field in fields.items() if "default" in field}
        })
