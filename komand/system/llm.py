from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from params import model, api_key, base_url, verbose, max_len
from komand.komand_list import komand_list
from .prompt import prompt_template, convert_template, summary_template
from langchain.output_parsers import ResponseSchema
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser
from termcolor import cprint
from log import p
import msg_tmp
from datetime import datetime, timedelta

class LLM:
    def __init__(self): pass 
    async def inv(self, input_text, chat_history, state):
        """
        input_text: string - user's message
        chat_history: list of strings - chat history 
        state: FSMContext - state from aiogram
        """ 

        self.llm = ChatOpenAI(model=model, api_key=api_key, base_url=base_url)
        self.tools = [k.get_tool(state) for k in komand_list if not k.tg_only]
        self.prompt_template = prompt_template
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt_template) #pyright: ignore
        self.executor = AgentExecutor(agent = self.agent, tools = self.tools, verbose = verbose, handle_parsing_errors = True) #pyright: ignore

        if len(chat_history) > max_len: chat_history = chat_history[-max_len:]
        if not chat_history: chat_history = []
        
        response = await self.executor.ainvoke({
            'input': input_text,
            'chat_history': chat_history, 
        })

        response_text = self._stringify(response['output'])
        
        return response_text

    def _stringify(self, text):
        if 'Ответ: ' in text : text = text.split('Ответ: ')[1]
        return text

    def get_commands_list(self): 
        return [cmd for k in komand_list \
            for cmd in (k.command if isinstance(k.command, list) else [k.command])]

    def get_command(self, text: str):
        if not text in self.get_commands_list():
            raise Exception('Command not found')

        for k in komand_list:
            if text in k.command or text == k.command:
                return k.func
        
    # def get_commands_dict(self):
    #     return {k.command: k.func for k in komand_list}
    
    async def __call__(self, input_text, chat_history, state):
         return await self.inv(input_text, chat_history, state)

def parse_task_and_time(input_text: str) -> dict:
    response_schemas = [
        ResponseSchema(name="text", description="Основаная информация о задаче без временной информации"),
        ResponseSchema(name="time_text", description=f"Время в формате: \"%Y-%m-%d %H:%M\". Если указано время в формате 'через 5 минут, через час' и так далее (относительное время)\
                       , Подай на вход время в формате HH::MM. То есть, если скажут 'через 5 минут', то подай на вход '00::05', если скажут через час подай на вход '01::00' и так далее\
                       Если не будет указания даты передай формат 'days:0 HH:MM'. Следуй системному промпту."),
    ] 

    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    prompt = ChatPromptTemplate.from_template(convert_template)

    model_ = ChatOpenAI(model = model, api_key = api_key, base_url=base_url, verbose = verbose)

    chain = prompt | model_ | output_parser

    try:
        result = chain.invoke({
            "input_text": input_text,
            "format_instructions": format_instructions
        }) 
        return result
    except Exception as e:
        return {
            "text": input_text,
            "time_text": ""
        }

def parse_time(input_text: str) -> str:
    response_schemas = [
        ResponseSchema(name="time_text", description=f"Time in format \"%Y-%m-%d %H:%M\".")
    ] 

    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    prompt = ChatPromptTemplate.from_template(convert_template)

    model_ = ChatOpenAI(model=model, api_key=api_key, base_url=base_url, verbose=verbose)

    chain = prompt | model_ | output_parser

    try:
        result = chain.invoke({
            "input_text": input_text,
            "format_instructions": format_instructions
        }) 
        return result["time_text"]

    except Exception as e:
        return ""

def summary_notes(notes: str) -> str:

    response_schemas = [
        ResponseSchema(name="summary_notes", description='''Сделай краткое описание заметок переданных тебе
        и помни, что ты - личная секретарша пользователя. Выведи ответ для и рекомендации в одну переменную. Обращайся к нему на ты''')
    ] 
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    prompt = ChatPromptTemplate.from_template(summary_template)

    model_ = ChatOpenAI(model=model, api_key=api_key, base_url=base_url, verbose=verbose)

    chain = prompt | model_ | output_parser

    try:
        result = chain.invoke({
            "notes": notes,
            "format_instructions": format_instructions
        }) 

        cprint(result, color = 'yellow')
        return result["summary_notes"]

    except Exception as e:
        p(e.__class__)
        return msg_tmp.output_parse_error

