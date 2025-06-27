from . import chatgpt, tools
from . import prompts, format

def explain_error_message(code: str, exception: str) -> str:
    message = chatgpt.Message()
    
    message.add_message_system(prompts.SYSTEM_INSTRUCTIONS)
    message.add_message_user(prompts.explain_error(code, exception))
    answer = chatgpt.generate_answer(message, json_format=format.MessageFormat, tools=[
        tools.get_search_path,
        tools.get_tables,
    ])

    return format.format_response(answer)

def locate_error_cause(code: str, exception: str) -> str:
    message = chatgpt.Message()
    
    message.add_message_system(prompts.SYSTEM_INSTRUCTIONS)
    message.add_message_user(prompts.locate_error_cause(code, exception))
    answer = message.generate_answer(json_format=format.MessageFormat)

    return format.format_response(answer)

def provide_error_example(code: str, exception: str) -> str:
    message = chatgpt.Message()

    message.add_message_system(prompts.SYSTEM_INSTRUCTIONS)
    message.add_message_user(prompts.provide_error_example(code, exception))
    answer = message.generate_answer(json_format=format.MessageFormat)

    return format.format_response(answer)

def fix_query(code: str, exception: str) -> str:
    message = chatgpt.Message()

    message.add_message_system(prompts.SYSTEM_INSTRUCTIONS)
    message.add_message_user(prompts.fix_query(code, exception))
    answer = message.generate_answer(json_format=format.MessageFormat)

    return format.format_response(answer)

def describe_my_query(code: str) -> str:
    message = chatgpt.Message()
    
    message.add_message_system(prompts.SYSTEM_INSTRUCTIONS)
    message.add_message_user(prompts.describe_my_query(code))
    answer = message.generate_answer(json_format=format.MessageFormat)

    return format.format_response(answer)

def explain_my_query(code: str) -> str:
    message = chatgpt.Message()
    
    message.add_message_system(prompts.SYSTEM_INSTRUCTIONS)
    message.add_message_user(prompts.explain_my_query(code))
    answer = message.generate_answer(json_format=format.MessageFormat)

    return format.format_response(answer)
