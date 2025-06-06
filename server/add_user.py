from server.db import register_user

from dav_tools import argument_parser, messages


if __name__ == '__main__':
    argument_parser.set_description('Add a new user to the database')
    argument_parser.add_argument('username', type=str, help='Username of the user to add')
    argument_parser.add_argument('password', type=str, help='Password of the user to add')

    username = argument_parser.args.username
    password = argument_parser.args.password

    if register_user(username, password):
        messages.success(f'User {username} added successfully.')
    else:
        messages.error(f'Failed to add user {username}.')
        