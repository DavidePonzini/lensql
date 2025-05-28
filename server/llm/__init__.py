from dav_tools import chatgpt

from . import _prompts


MessageRole = chatgpt.MessageRole


def explain_error_message(code: str, exception: str) -> str:
    message = chatgpt.Message()
    
    message.add_message(MessageRole.USER, _prompts.explain_error(code, exception))
    answer = message.generate_answer()

    return answer

def locate_error_cause(code: str, exception: str) -> str:
    message = chatgpt.Message()
    
    message.add_message(MessageRole.USER, _prompts.locate_error_cause(code, exception))
    answer = message.generate_answer()

    return answer

def provide_error_example(code: str, exception: str) -> str:
    message = chatgpt.Message()

    message.add_message(MessageRole.USER, _prompts.provide_error_example(code, exception))
    answer = message.generate_answer()

    return answer

def fix_query(code: str, exception: str) -> str:
    message = chatgpt.Message()

    message.add_message(MessageRole.USER, _prompts.fix_query(code, exception))
    answer = message.generate_answer()

    return answer

def describe_my_query(code: str) -> str:
    message = chatgpt.Message()
    
    message.add_message(MessageRole.USER, _prompts.describe_my_query(code))
    answer = message.generate_answer()

    return answer

def explain_my_query(code: str) -> str:
    message = chatgpt.Message()
    
    message.add_message(MessageRole.USER, _prompts.explain_my_query(code))
    answer = message.generate_answer()

    return answer
