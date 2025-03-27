from dav_tools import chatgpt
import prompts

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
