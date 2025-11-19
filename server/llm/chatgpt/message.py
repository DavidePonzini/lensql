from dav_tools import messages

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


    def print_chat(self):
        for msg in self.messages:
            role = msg['role']
            content = msg['content']

            if role == MessageRole.TOOL:
                messages.message(content, icon='TOOL',
                                 icon_options=[
                                     messages.TextFormat.Style.BOLD,
                                     messages.TextFormat.Color.CYAN,
                                 ], default_text_options=[messages.TextFormat.Color.CYAN])
            elif role == MessageRole.USER:
                messages.message(content, icon='USER',
                                 icon_options=[
                                     messages.TextFormat.Style.BOLD,
                                     messages.TextFormat.Color.GREEN,
                                 ], default_text_options=[messages.TextFormat.Color.GREEN])
            elif role == MessageRole.ASSISTANT:
                messages.message(content, icon='ASSISTANT',
                                 icon_options=[
                                     messages.TextFormat.Style.BOLD,
                                     messages.TextFormat.Color.YELLOW,
                                 ], default_text_options=[messages.TextFormat.Color.YELLOW])
            elif role == MessageRole.SYSTEM:
                messages.message(content, icon='SYSTEM',
                                 icon_options=[
                                     messages.TextFormat.Style.BOLD,
                                     messages.TextFormat.Color.PURPLE,
                                 ], default_text_options=[messages.TextFormat.Color.PURPLE])