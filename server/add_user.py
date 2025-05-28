import server.db_admin as db_admin
import server.db_users as db_users

from dav_tools import argument_parser, messages
from dav_tools.database import sql


def add_user(username: str, password: str):
    try:
        db_admin.register_user(username, password)
        messages.info(f'User credentials added: {username}')
    except Exception as e:
        messages.error(f"Error adding credentials for user {username}: {e}")

    try:
        with db_users.DBConnection(dbname='postgres', username='postgres') as admin_conn:
            with admin_conn.cursor() as cur:
                cur.execute(sql.SQL(
                    '''CREATE DATABASE {username}''').format(
                    username=sql.Identifier(username)
                ))

                cur.execute(sql.SQL(
                    '''CREATE USER {username} WITH PASSWORD {password}''').format(
                    username=sql.Identifier(username),
                    password=sql.Placeholder('password')
                ), {
                    'password': password
                })

                cur.execute(sql.SQL(
                    '''ALTER USER {username} WITH CREATEROLE''').format(
                    username=sql.Identifier(username),
                ))

                cur.execute(sql.SQL(
                    '''GRANT ALL PRIVILEGES ON DATABASE {username} TO {username}''').format(
                    username=sql.Identifier(username)
                ))

                for db in ['postgres', 'template1', 'template0']:
                    cur.execute(sql.SQL(
                        '''REVOKE CONNECT ON DATABASE {db} FROM {username}''').format(
                        db=sql.Identifier(db),
                        username=sql.Identifier(username),
                    ))

        with db_users.DBConnection(dbname=username, username='postgres') as user_conn:
            with user_conn.cursor() as cur:
                cur.execute(sql.SQL(
                    '''ALTER SCHEMA public OWNER TO {username}''').format(
                    username=sql.Identifier(username)
                ))

            user_conn.commit()

        messages.info(f'Database {username} created successfully.')

    except Exception as e:
        messages.error(f"Error creating database for user {username}: {e}")


if __name__ == '__main__':
    argument_parser.set_description('Add a new user to the database')
    argument_parser.add_argument('username', type=str, help='Username of the user to add')
    argument_parser.add_argument('password', type=str, help='Password of the user to add')

    username = argument_parser.args.username
    password = argument_parser.args.password

    add_user(username, password)