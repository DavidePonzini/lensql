from server import db

from dav_tools import messages

if __name__ == '__main__':
    for user, password, is_admin, school in [
        ('lens', 'l', True, 'DIBRIS'),
        ('dav', 'd', True, 'DIBRIS'),
        ('giovanna', 'g', False, 'DIBRIS'),
        ('barbara', 'b', False, 'DIBRIS'),
        ('student', 's', False, 'DIBRIS'),
    ]:
        if db.register_user(user, password, is_admin=is_admin, school=school):
            messages.info(f'User {user} registered successfully')
