from server.db.admin import User
import dav_tools

if __name__ == '__main__':
    dav_tools.argument_parser.add_argument('username', type=str, help='Username of the user to set the password for')
    dav_tools.argument_parser.add_argument('password', type=str, help='New password for the user')
    dav_tools.argument_parser.parse_args()

    user = User(dav_tools.argument_parser.args.username)
    user.change_password(dav_tools.argument_parser.args.password)

    dav_tools.messages.success(f"Password for user '{user.username}' has been updated successfully.")