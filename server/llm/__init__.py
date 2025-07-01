from . import tools, prompts, format, chatgpt

def explain_error_message(username: str, code: str, exception: str) -> str:
    message = chatgpt.Message()
    
    message.add_message_system(prompts.SYSTEM_INSTRUCTIONS)
    message.add_message_user(prompts.explain_error(code, exception))
    answer = chatgpt.generate_answer(message, json_format=format.MessageFormat,
        tools=[
            tools.get_search_path,
            tools.get_tables,
        ], username=username,
    )

    return str(answer)

def locate_error_cause(username: str, code: str, exception: str) -> str:
    message = chatgpt.Message()
    
    message.add_message_system(prompts.SYSTEM_INSTRUCTIONS)
    message.add_message_user(prompts.locate_error_cause(code, exception))
    answer = chatgpt.generate_answer(message, json_format=format.MessageFormat,
        tools=[
            tools.get_search_path,
            tools.get_tables,
        ], username=username,
    )

    return str(answer)

def provide_error_example(username: str, code: str, exception: str) -> str:
    message = chatgpt.Message()

    message.add_message_system(prompts.SYSTEM_INSTRUCTIONS)
    message.add_message_user(prompts.provide_error_example(code, exception))
    answer = chatgpt.generate_answer(message,
        json_format=format.MessageFormat,
        tools=[
            tools.get_search_path,
            tools.get_tables,
        ],
        username=username,
    )

    return str(answer)

def fix_query(username: str, code: str, exception: str) -> str:
    message = chatgpt.Message()

    message.add_message_system(prompts.SYSTEM_INSTRUCTIONS)
    message.add_message_user(prompts.fix_query(code, exception))
    answer = chatgpt.generate_answer(message,
        json_format=format.MessageFormat,
        tools=[
            tools.get_search_path,
            tools.get_tables,
        ],
        username=username,
    )

    return str(answer)

def describe_my_query(username: str, code: str) -> str:
    message = chatgpt.Message()
    
    message.add_message_system(prompts.SYSTEM_INSTRUCTIONS)
    message.add_message_user(prompts.describe_my_query(code))
    answer = chatgpt.generate_answer(message,
        json_format=format.MessageFormat,
        tools=[
            tools.get_search_path,
            tools.get_tables,
        ],
        username=username,
    )

    return str(answer)

def explain_my_query(username: str, code: str) -> str:
    message = chatgpt.Message()
    
    message.add_message_system(prompts.SYSTEM_INSTRUCTIONS)
    message.add_message_user(prompts.explain_my_query(code))
    answer = chatgpt.generate_answer(message,
        json_format=format.MessageFormat,
        tools=[
            tools.get_search_path,
            tools.get_tables,
        ],
        username=username,
    )

    return str(answer)
