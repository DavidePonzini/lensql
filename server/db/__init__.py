from . import admin, users

import dav_tools

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

    # Register on admin DB
    if not user.register_account(password, school=school, is_teacher=is_teacher, is_admin=is_admin):
        dav_tools.messages.error(f'User "{user.username}" already exists.')
    
    # Register on user DB (PostgreSQL)
    if not users.PostgresqlDatabase(user.username).init(password):
        dav_tools.messages.error(f'Failed to initialize database for user {user.username}. Deleting user.')
    
    # Register on user DB (MySQL)
    # TODO
    
    for dataset in datasets:
        dataset.add_participant(user)
    
    return True
