from dav_tools import chatgpt
from . import prompts


MessageRole = chatgpt.MessageRole


def explain_error_message(code: str, exception: str) -> str:
    message = chatgpt.Message()
    
    message.add_message(chatgpt.MessageRole.USER, prompts.explain_error(code, exception))
    answer = message.generate_answer()

    return answer

def identify_error_cause(code: str, exception: str) -> str:
    message = chatgpt.Message()
    
    message.add_message(chatgpt.MessageRole.USER, prompts.guide_user(code, exception))
    answer = message.generate_answer()

    return answer


def explain_my_query(code: str) -> str:
    message = chatgpt.Message()
    
    message.add_message(chatgpt.MessageRole.USER, prompts.explain_my_query(code))
    answer = message.generate_answer()

    return answer

def free_prompt(prompt: str, code: str, conversation: list[dict[str, str]]) -> str:
    message = chatgpt.Message()
    message.add_message(chatgpt.MessageRole.USER, code)

    for msg in conversation:
        message.add_message(msg['role'], msg['content'])
        
    message.add_message(MessageRole.USER, prompt)
    answer = message.generate_answer()
    
    return answer