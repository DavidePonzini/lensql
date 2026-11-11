from . import admin, users

import dav_tools

def register_user(user: admin.User,
                  password: str,
                  *,
                  school: str,
                  is_teacher: bool = False,
                  is_admin: bool = False,
                  activities: list[admin.Activity] = []
    ) -> bool:
    '''
    Register a new user.

    Args:
        username (str): The username of the new user.
        password (str): The password for the new user.
        school (str): The school of the new user.
        is_teacher (bool): Whether the new user is a teacher.
        is_admin (bool): Whether the new user is an admin.
        activities (list[admin.Activity]): List of activities to add the user to.

    Returns:
        bool: True if registration is successful, False otherwise.
    '''

    # Register on admin DB
    if not user.register_account(password, school=school, is_teacher=is_teacher, is_admin=is_admin):
        dav_tools.messages.error(f'User "{user.username}" already exists.')
    
    for activity in activities:
        activity.add_participant(user)
    
    return True
