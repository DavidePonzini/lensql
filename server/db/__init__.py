from . import admin, users

from dav_tools import messages

def register_user(username: str, password: str, *, is_teacher: bool = False, is_admin: bool = False) -> bool:
    '''
    Register a new user.

    Args:
        username (str): The username of the new user.
        password (str): The password for the new user.

    Returns:
        bool: True if registration is successful, False otherwise.
    '''

    if not admin.auth.register_user(username, password, is_teacher=is_teacher, is_admin=is_admin):
        messages.debug(f'Failed to register user {username}. User already exists or database error.')
        return False
    
    if not users.auth.init_database(username, password):
        messages.debug(f'Failed to initialize database for user {username}. Deleting user.')
        admin.auth.delete_user(username)
        return False
    
    return True