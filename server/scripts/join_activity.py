from server.db.admin import User, Activity
import dav_tools

if __name__ == '__main__':
    dav_tools.argument_parser.add_argument('username', type=str, help='Username of the user to set the password for')
    dav_tools.argument_parser.add_argument('activity', type=str, help='Activity ID to join')
    dav_tools.argument_parser.add_argument('-o', '--owner', action='store_true', help='Flag to indicate if the user is joining as an owner')
    dav_tools.argument_parser.parse_args()

    user = User(dav_tools.argument_parser.args.username)
    activity = Activity(dav_tools.argument_parser.args.activity)
    
    activity.add_participant(user)
    activity.set_owner_status(user, dav_tools.argument_parser.args.owner)

    dav_tools.messages.success(f"User '{user.username}' has been added to activity '{activity.activity_id}' with owner status: {dav_tools.argument_parser.args.owner}.")