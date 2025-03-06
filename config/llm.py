from dav_tools import chatgpt
import prompts

def explain_error(code, exception) -> str:
    message = chatgpt.Message()
    
    message.add_message(chatgpt.MessageRole.USER, prompts.explain_error(code, exception))
    answer = message.generate_answer()

    return answer
