from typing import Any, Callable#, Dict, List
# import inspect
# import typing

# ---------- helpers ---------------------------------------------------------

# def _pytype_to_jsontype(py_type: type) -> str:
#     '''Very small mapper from Python types → JSON Schema type strings.'''
#     return {
#         str:    'string',
#         int:    'integer',
#         float:  'number',
#         bool:   'boolean',
#         list:   'array',
#         dict:   'object'
#     }.get(py_type, 'string')   # sensible fallback


# def _infer_properties(fn: Callable) -> tuple[Dict[str, Dict[str, Any]], List[str]]:
#     '''
#     Build JSON-Schema properties + required from a function signature.
#     Anything without a default value is considered *required*.
#     '''
#     sig        = inspect.signature(fn)
#     type_hints = typing.get_type_hints(fn)

#     props: Dict[str, Dict[str, Any]] = {}
#     required: List[str] = []

#     for name, param in sig.parameters.items():
#         py_t        = type_hints.get(name, str)
#         json_t      = _pytype_to_jsontype(py_t)
#         props[name] = {'type': json_t}

#         if param.default is not inspect._empty:
#             props[name]['default'] = param.default
#         else:
#             required.append(name)

#     return props, required


# ---------- the Tool object -------------------------------------------------

class ToolParameter():
    '''
    A simple class to represent a parameter in a Tool.
    It is used to generate the JSON schema for the tool.
    '''
    def __init__(self, name: str, *, type: str, description: str, values: list[str] = []):
        self.name = name
        self.description = description
        self.type = type
        self.values = values  # optional, for enum-like parameters

    def to_dict(self) -> dict[str, Any]:
        '''Convert the ToolParameter to a dictionary for JSON schema.'''

        result = {
            'type':        self.type,
            'description': self.description,
        }

        if self.values:
            result['enum'] = self.values

        return result


class Tool:
    '''
    A thin wrapper that stores the Python callable and generates the
    OpenAI JSON-schema entry when asked.
    '''
    def __init__(self, function: Callable, description: str, *, parameters: list[ToolParameter] = [], required: list[str] = []):
        self.function = function
        self.description = description
        self.name = function.__name__
        self.parameters = parameters
        self.required = required

    @property
    def schema(self) -> dict[str, Any]:
        '''Return exactly the dict you drop into tools=[…].'''
        return {
            'type': 'function',
            'function': {
                'name':        self.name,
                'description': self.description,
                'parameters': {
                    'type': 'object',
                    'properties': {
                        param.name: param.to_dict() for param in self.parameters
                    },
                    'required': self.required,
                    'additionalProperties': False,  # strict validation
                }
            }
        }

    def __call__(self, username: str, **kwargs):
        '''Just lets you do tool(**json_args) later on.'''
        return self.function(username=username, **kwargs)

def llm_tool(description: str, *, parameters: list[ToolParameter] = [], required: list[str] = []) -> Callable[[Callable], Tool]:
    '''
    Decorator to turn a function into a Tool object.
    The function must have type hints for its parameters.
    '''
    def decorator(fn: Callable) -> Tool:
        return Tool(fn, description=description, parameters=parameters, required=required)
    
    return decorator
