from . import admin, users

from dav_tools import messages


def register_user(user: admin.User,
                  password: str,
                  *,
                  school: str,
                  is_teacher: bool = False,
                  is_admin: bool = False,
                  datasets: list[admin.Dataset] = []
    ) -> bool:
    '''
    Register a new user.

    Args:
        username (str): The username of the new user.
        password (str): The password for the new user.
        school (str): The school of the new user.
        is_teacher (bool): Whether the new user is a teacher.
        is_admin (bool): Whether the new user is an admin.
        datasets (list[admin.Dataset]): List of datasets to add the user to.

    Returns:
        bool: True if registration is successful, False otherwise.
    '''

    if not user.register_account(password, school=school, is_teacher=is_teacher, is_admin=is_admin):
        messages.debug(f'Failed to register user {user.username}. User already exists or database error.')
        return False
    
    if not users.auth.init_database(user.username, password):
        messages.debug(f'Failed to initialize database for user {user.username}. Deleting user.')
        user.delete_account()
        return False
    
    for dataset in datasets:
        dataset.add_participant(user)
    
    return True
