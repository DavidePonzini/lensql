import os

def load_file(filename: str) -> str:
    file_path = f'{os.path.dirname(os.path.abspath(__file__))}/{filename}'

    with open(file_path) as file_path:
        return file_path.read()
