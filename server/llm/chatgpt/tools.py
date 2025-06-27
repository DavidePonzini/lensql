from typing import Any, Callable, Dict, List
import inspect
import typing

# ---------- helpers ---------------------------------------------------------

def _pytype_to_jsontype(py_type: type) -> str:
    '''Very small mapper from Python types → JSON Schema type strings.'''
    return {
        str:    'string',
        int:    'integer',
        float:  'number',
        bool:   'boolean',
        list:   'array',
        dict:   'object'
    }.get(py_type, 'string')   # sensible fallback


def _infer_properties(fn: Callable) -> tuple[Dict[str, Dict[str, Any]], List[str]]:
    '''
    Build JSON-Schema properties + required from a function signature.
    Anything without a default value is considered *required*.
    '''
    sig        = inspect.signature(fn)
    type_hints = typing.get_type_hints(fn)

    props: Dict[str, Dict[str, Any]] = {}
    required: List[str] = []

    for name, param in sig.parameters.items():
        py_t        = type_hints.get(name, str)
        json_t      = _pytype_to_jsontype(py_t)
        props[name] = {'type': json_t}

        if param.default is not inspect._empty:
            props[name]['default'] = param.default
        else:
            required.append(name)

    return props, required


# ---------- the Tool object -------------------------------------------------

class Tool:
    '''
    A thin wrapper that stores the Python callable and generates the
    OpenAI JSON-schema entry when asked.
    '''
    def __init__(self, function: Callable, description: str):
        self.function = function
        self.description = description
        self.name = function.__name__

        self.parameters, self.required = _infer_properties(function)

    @property
    def schema(self) -> Dict[str, Any]:
        '''Return exactly the dict you drop into tools=[…].'''
        return {
            'type': 'function',
            'function': {
                'name':        self.name,
                'description': self.description,
                'parameters': {
                    'type':       'object',
                    'properties': self.parameters,
                    'required':   self.required,
                    'additionalProperties': False,  # strict validation
                }
            }
        }

    def __call__(self, **kwargs):
        '''Just lets you do tool(**json_args) later on.'''
        return self.function(**kwargs)

def llm_tool(description: str):
    '''
    Decorator to turn a function into a Tool object.
    The function must have type hints for its parameters.
    '''
    def decorator(fn: Callable) -> Tool:
        return Tool(fn, description)
    return decorator
