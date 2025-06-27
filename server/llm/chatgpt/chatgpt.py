import json
from openai import OpenAI
from pydantic import BaseModel
import os
from dav_tools import messages
from .message import Message
from .tools import Tool


api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    messages.critical_error('OPENAI_API_KEY is not set. Please set it in your environment variables.')

client = OpenAI(api_key=api_key)

def generate_answer(message: Message, *, json_format: BaseModel, tools: list[Tool] = [], **kwargs) -> BaseModel:
    '''
    Generate an answer from the LLM using the provided message and tools.
    '''

    schema = json_format.model_json_schema()
    schema['additionalProperties'] = False      # Required for strict validation

    available_tools = tools
    tool_map = {tool.name: tool for tool in tools}

    while True:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=message.messages,
            response_format={
                'type': 'json_schema',
                'json_schema': {
                    'name': 'Response',
                    'strict': True,
                    'schema': schema,
                },
            },
            tools=[tool.schema for tool in available_tools],
            tool_choice='auto',
            **kwargs
        )

        msg = response.choices[0].message
        message.append(msg)

        messages.debug(msg)

        # A. Did the model call a tool?
        if msg.tool_calls:
            for call in msg.tool_calls:
                fn   = tool_map[call.function.name]
                args = json.loads(call.function.arguments) or {}
                result = fn(**args)

                available_tools.remove(fn)

                message.add_message_tool(call.id, result)

            continue                         # loop back for the model to integrate

        # B. Final JSON answer — validate & break
        return json_format.model_validate_json(msg.content)
        