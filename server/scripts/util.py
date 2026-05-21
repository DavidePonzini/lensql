from sqlerrors import SqlErrors, SqlErrorCategory
from sqlexercise import DifficultyLevel

import dav_tools

def print_taxonomy() -> None:
    '''Print the SQL error taxonomy with color coding based on error categories'''
    for e in SqlErrors:
        if e.definition.category is SqlErrorCategory.SYNTAX:
            color = dav_tools.messages.TextFormat.Color.RED
        elif e.definition.category is SqlErrorCategory.SEMANTIC:
            color = dav_tools.messages.TextFormat.Color.YELLOW
        elif e.definition.category is SqlErrorCategory.LOGICAL:
            color = dav_tools.messages.TextFormat.Color.CYAN
        elif e.definition.category is SqlErrorCategory.COMPLICATION:
            color = dav_tools.messages.TextFormat.Color.GREEN
        else:
            color = dav_tools.messages.TextFormat.Color.PURPLE

        if e.definition.is_deprecated:
            default_text_options = [dav_tools.messages.TextFormat.Style.DIM]
        else:
            default_text_options = [color]


        dav_tools.messages.message(
            e.value, e.definition.category, e.definition.name,
            text_min_len=[5, 5],
            default_text_options=default_text_options,
            additional_text_options=[
                [dav_tools.messages.TextFormat.Style.BOLD],
                [dav_tools.messages.TextFormat.Style.BOLD],
            ])

def select_target_errors() -> list[tuple[SqlErrors, DifficultyLevel]]:
    '''Prompt user to select which errors to target from the error stats.'''
    selection: list[tuple[int, str]] = []
    while True:
        selection_input = dav_tools.messages.ask('Enter space-separated error numbers and difficulties to target (e.g. "1a 3b 5c")')
        try:
            selection = [(int(i[:-1]), i[-1]) for i in selection_input.split()]
            if all(1 <= i <= len(SqlErrors) and d in ['a', 'b', 'c'] for i, d in selection):
                break
            else:
                dav_tools.messages.error('Invalid input. Please enter valid error numbers and difficulties from the list.')
        except ValueError:
            dav_tools.messages.error('Invalid input. Please enter space-separated error numbers and difficulties.')

    
    result: list[tuple[SqlErrors, DifficultyLevel]] = []

    for e, d in selection:
        difficulty = DifficultyLevel(ord(d) - ord('a') + 1)
        result.append((SqlErrors(e), difficulty))
    
    return result
