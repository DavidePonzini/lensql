from server.db.users import get_database
from server.db.admin import User

import dav_tools

if __name__ == '__main__':
    dav_tools.argument_parser.add_argument('dbms', help='DBMS to connect to (e.g. "postgres")')
    dav_tools.argument_parser.parse_args()

    dbms = dav_tools.argument_parser.args.dbms

    for user in User.list_all():
        db = get_database(user.username, dbms)
        db.start_container()
        print(db.hostname)