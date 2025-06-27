class MessageRole:
    USER = 'user'
    ASSISTANT = 'assistant'
    SYSTEM = 'system'
    TOOL = 'tool'

class Message:
    def __init__(self) -> None:
        self.messages = []

    def add_message_user(self, message: str):
        self.messages.append({
            'role': MessageRole.USER,
            'content': message
        })

    def add_message_assistant(self, message: str):
        self.messages.append({
            'role': MessageRole.ASSISTANT,
            'content': message
        })

    def add_message_system(self, message: str):
        self.messages.append({
            'role': MessageRole.SYSTEM,
            'content': message
        })

    def add_message_tool(self, call_id: int, message: str):
        self.messages.append({
            'role': MessageRole.TOOL,
            'tool_call_id': call_id,
            'content': message
        })

    def append(self, message: dict):
        self.messages.append(message)

