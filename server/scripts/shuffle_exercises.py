'''Sfhuffle exercise order in a activity.'''

import dav_tools
from server.db.admin import Activity


if __name__ == '__main__':
    dav_tools.argument_parser.add_argument('activity', help='ID of the activity to shuffle exercises for')
    dav_tools.argument_parser.add_argument('prefix', nargs='?', default='Exercise ', help='Prefix for the shuffled exercise titles')
    dav_tools.argument_parser.parse_args()

    activity = Activity(dav_tools.argument_parser.args.activity)
    activity.shuffle(dav_tools.argument_parser.args.prefix)

    dav_tools.messages.success(f"Shuffled exercises in activity '{activity.activity_id}'")