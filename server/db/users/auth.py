from . import connection

from dav_tools.database import sql

def init_database(username: str, password: str = 'password') -> bool:
    # Note: CREATE DATABASE does not support transactions
    try:
        with connection.get_admin_connection(autocommit=True) as admin_conn:
            with admin_conn.cursor() as cur:
                cur.execute(sql.SQL('''
                    CREATE DATABASE {username}
                ''').format(
                    username=sql.Identifier(username)
                ))
    except Exception as e:
        from dav_tools import messages
        messages.debug(f'Failed to create database for user {username}: {e}')
        return False
    
    try:
        with connection.get_admin_connection(autocommit=False) as admin_conn:
            with admin_conn.cursor() as cur:
                cur.execute(sql.SQL('''
                    CREATE USER {username} WITH PASSWORD {password}
                ''').format(
                    username=sql.Identifier(username),
                    password=sql.Placeholder('password')
                ), {
                    'password': password
                })

                cur.execute(sql.SQL('''
                    ALTER USER {username} WITH CREATEROLE
                ''').format(
                    username=sql.Identifier(username),
                ))

                cur.execute(sql.SQL('''
                    GRANT ALL PRIVILEGES ON DATABASE {username} TO {username}
                ''').format(
                    username=sql.Identifier(username)
                ))

                for db in ['postgres', 'template1', 'template0']:
                    cur.execute(sql.SQL('''
                        REVOKE CONNECT ON DATABASE {db} FROM {username}
                    ''').format(
                        db=sql.Identifier(db),
                        username=sql.Identifier(username),
                    ))

        with connection.get_admin_connection(dbname=username) as user_conn:
            with user_conn.cursor() as cur:
                cur.execute(sql.SQL('''
                    ALTER SCHEMA public OWNER TO {username}
                ''').format(
                    username=sql.Identifier(username)
                ))

            user_conn.commit()

        return True
    except Exception as e:
        from dav_tools import messages
        messages.debug(f'Failed to initialize database for user {username}: {e}')
        return False
