from . import prompts, format, chatgpt
from sql_error_categorizer import DetectedError

def explain_error_message(code: str, exception: str) -> str:
    answer = chatgpt.generate_answer(
        system_prompt=prompts.get_system_instructions(),
        user_prompt=prompts.explain_error(code, exception),
        json_format=format.MessageFormat,
    )

    return str(answer[0])

def locate_error_cause(code: str, exception: str) -> str:
    answer = chatgpt.generate_answer(
        system_prompt=prompts.get_system_instructions(),
        user_prompt=prompts.locate_error_cause(code, exception),
        json_format=format.MessageFormat,
    )

    return str(answer[0])

def provide_error_example(code: str, exception: str) -> str:
    answer = chatgpt.generate_answer(
        system_prompt=prompts.get_system_instructions(),
        user_prompt=prompts.provide_error_example(code, exception),
        json_format=format.MessageFormatWithCode,
    )

    return str(answer[0])

def fix_query(code: str, exception: str, errors: list[DetectedError]) -> str:
    answer = chatgpt.generate_answer(
        system_prompt=prompts.get_system_instructions(),
        user_prompt=prompts.fix_query(code, exception, errors=errors),
        json_format=format.MessageFormatWithCode,
    )

    return str(answer[0])

def describe_my_query(code: str) -> str:
    answer = chatgpt.generate_answer(
        system_prompt=prompts.get_system_instructions(),
        user_prompt=prompts.describe_my_query(code),
        json_format=format.MessageFormat,
    )

    return str(answer[0])

def explain_my_query(code: str) -> str:
    answer = chatgpt.generate_answer(
        system_prompt=prompts.get_system_instructions(),
        user_prompt=prompts.explain_my_query(code),
        json_format=format.MessageFormat,
    )

    return str(answer[0])

def detect_errors(code: str, errors: list[DetectedError]) -> str:
    assert len(errors) > 0, "No errors to detect"

    answer = chatgpt.generate_answer(
        system_prompt=prompts.get_system_instructions(),
        user_prompt=prompts.detect_errors(code, errors=errors),
        json_format=format.MessageFormat,
    )

    return str(answer[0])
