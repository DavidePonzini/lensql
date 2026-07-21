from server.db.users import get_database
from server.db.admin import User
from sqlscope import Dialect

from tqdm import tqdm

import dav_tools

if __name__ == '__main__':
    dav_tools.argument_parser.add_argument('dbms', help='DBMS to connect to (e.g. "postgres")', type=Dialect, choices=list(Dialect))
    dav_tools.argument_parser.parse_args()

    dbms = Dialect(dav_tools.argument_parser.args.dbms)

    for user in tqdm(User.list_all(), desc="Processing users"):
        db = get_database(user.username, dbms)
        db.start_container()
        print(db.hostname)