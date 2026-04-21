import json
from openai import OpenAI
from pydantic import BaseModel
import os
from dav_tools import messages
from openai.types.responses import Response

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    messages.critical_error('OPENAI_API_KEY is not set. Please set it in your environment variables.')

client = OpenAI(api_key=api_key)

def generate_answer(
        system_prompt: str,
        user_prompt: str,
        *,
        previous_response_id: str | None = None,
        json_format: type[BaseModel],
        **kwargs) -> tuple[BaseModel, str]:
    '''
    Generate an answer from the LLM using the provided message and tools.

    Args:
        system_prompt: The system prompt to guide the LLM's behavior.
        user_prompt: The user's message or query.
        previous_response_id: The ID of the previous response in the conversation, if any.
        json_format: A Pydantic model class that defines the expected format of the LLM's response.
        **kwargs: Additional keyword arguments to pass to the OpenAI API.

    Returns:
        A tuple containing the generated answer (as a Pydantic model) and the response's ID.
    '''

    schema = json_format.model_json_schema()
    schema['additionalProperties'] = False      # Required for strict validation

    response = client.responses.create(
        model=os.getenv('LENSQL_OPENAI_MODEL', 'gpt-4o-mini'),
        instructions=system_prompt,
        input=user_prompt,
        previous_response_id=previous_response_id,
        text={
            'format': {
                'type': 'json_schema',
                'name': 'Response',
                'strict': True,
                'schema': schema,
                },
        },
        **kwargs
    )

    assert isinstance(response, Response)

    return json_format.model_validate_json(response.output_text), response.id
        