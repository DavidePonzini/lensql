
from .data_types import DATA_TYPES
from .connection import PostgresqlConnection
from .queries import PostgresqlBuiltinQueries, PostgresqlMetadataQueries
from ..database import Database

from psycopg2 import sql
import dav_tools
import os
import docker
from docker.models.containers import Container

NETWORK_NAME = os.getenv('DB_USERS_NETWORK', 'db_users')


class PostgresqlDatabase(Database):
    Database.admin_username = 'postgres'

    Database.builtin_queries = PostgresqlBuiltinQueries
    Database.metadata_queries = PostgresqlMetadataQueries

    Database.data_types = DATA_TYPES

    @property
    def db_type(self) -> str:
        return 'postgresql'
    
    @property
    def port(self) -> int:
        return 5432
    
    def create_container(self) -> Container:
        client = docker.from_env()

        container = client.containers.run(
            image='postgres:latest',
            name=self.hostname,
            environment={
                'POSTGRES_PASSWORD': 'password',
                'POSTGRES_HOST_AUTH_METHOD': 'trust',
            },
            ports={
                f'{self.port}/tcp': self.port,
            },
            detach=True,
            network=NETWORK_NAME,
            volumes={
                # Mount a volume for PostgreSQL data persistence
                f'{self.hostname}_data': {
                    'bind': '/var/lib/postgresql/data',
                    'mode': 'rw',
                }
            },
            mem_limit='512m',
            nano_cpus=1_000_000_000,  # Limit to 1 CPU,
        )

        # Wait for the container to be ready
        container.reload()
        while container.status != 'running':
            dav_tools.messages.info(f'Waiting for container {self.hostname} to be running...')
            container.reload()

        return container

    def _get_connection(self, autocommit: bool = True) -> PostgresqlConnection:
        self.start_container() # ensure container is running before connecting

        return PostgresqlConnection(host=self.hostname, port=self.port, autocommit=autocommit)

    def exists(self) -> bool:
        with PostgresqlDatabase('postgres').connect_as_admin() as admin_conn:
            assert isinstance(admin_conn, PostgresqlConnection)

            with admin_conn.cursor() as cur:
                cur.execute(sql.SQL('''
                    SELECT 1 FROM pg_database WHERE datname = {dbname}
                ''').format(
                    dbname=sql.Placeholder('dbname')
                ), {
                    'dbname': self.dbname
                })

                return cur.fetchone() is not None

    def init(self, password: str) -> bool:
        if self.dbname == self.admin_username:
            dav_tools.messages.error('Cannot initialize admin database.')
            return False

        if self.exists():
            dav_tools.messages.warning(f'Database for user {self.dbname} already exists.')
            return True

        # NOTE: CREATE DATABASE does not support transactions
        try:
            with PostgresqlDatabase('postgres').connect_as_admin() as admin_conn:
                assert isinstance(admin_conn, PostgresqlConnection)

                with admin_conn.cursor() as cur:
                    cur.execute(sql.SQL('''
                        CREATE DATABASE {username}
                    ''').format(
                        username=sql.Identifier(self.dbname)
                    ))
        except Exception as e:
            dav_tools.messages.error(f'CREATE DATABASE {self.dbname} failed: {e}')
            return False
        
        try:
            with PostgresqlDatabase('postgres').connect_as_admin(autocommit=False) as admin_conn:
                assert isinstance(admin_conn, PostgresqlConnection)

                with admin_conn.cursor() as cur:
                    cur.execute(sql.SQL('''
                        CREATE USER {username} WITH PASSWORD {password}
                    ''').format(
                        username=sql.Identifier(self.dbname),
                        password=sql.Placeholder('password')
                    ), {
                        'password': password
                    })

                    cur.execute(sql.SQL('''
                        ALTER USER {username} WITH CREATEROLE
                    ''').format(
                        username=sql.Identifier(self.dbname),
                    ))

                    cur.execute(sql.SQL('''
                        GRANT ALL PRIVILEGES ON DATABASE {username} TO {username}
                    ''').format(
                        username=sql.Identifier(self.dbname)
                    ))

                    for db in ['postgres', 'template1', 'template0']:
                        cur.execute(sql.SQL('''
                            REVOKE CONNECT ON DATABASE {db} FROM {username}
                        ''').format(
                            db=sql.Identifier(db),
                            username=sql.Identifier(self.dbname),
                        ))

            with self.connect_as_admin() as user_conn:
                assert isinstance(user_conn, PostgresqlConnection)

                with user_conn.cursor() as cur:
                    cur.execute(sql.SQL('''
                        ALTER SCHEMA public OWNER TO {username}
                    ''').format(
                        username=sql.Identifier(self.dbname)
                    ))

                user_conn.commit()

            return True
        except Exception as e:
            dav_tools.messages.error(f'Failed to initialize database for user {self.dbname}: {e}')
            return False

        
