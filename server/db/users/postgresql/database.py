
from server.db.users.queries import BuiltinQueries, MetadataQueries

from .data_types import DATA_TYPES
from .connection import PostgresqlConnection
from .queries import PostgresqlBuiltinQueries, PostgresqlMetadataQueries
from ..database import Database

import dav_tools
import os
import docker
from docker.models.containers import Container

NETWORK_NAME = os.getenv('DB_USERS_NETWORK', 'db_users')

class PostgresqlDatabase(Database):
    def __init__(self, dbname: str,):
        super().__init__(
            dbname=dbname,
            port=5432,
            dbms_name='postgresql',
            admin_username='postgres',
            builtin_queries=PostgresqlBuiltinQueries,
            metadata_queries=PostgresqlMetadataQueries,
            data_types=DATA_TYPES,
        )

    def create_container(self) -> Container:
        client = docker.from_env()

        container = client.containers.run(
            image='postgres:latest',
            name=self.hostname,
            environment={
                'POSTGRES_PASSWORD': 'password',
                'POSTGRES_HOST_AUTH_METHOD': 'trust',
            },
            detach=True,
            network=NETWORK_NAME,
            volumes={
                # Mount a volume for PostgreSQL data persistence
                f'{self.hostname}_data': {
                    'bind': '/var/lib/postgresql',
                    'mode': 'rw',
                }
            },
            labels=self.container_labels,
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
        return PostgresqlConnection(host=self.hostname, port=self.port, autocommit=autocommit)


        
