
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
    Database.admin_username = 'postgres'

    Database.builtin_queries = PostgresqlBuiltinQueries
    Database.metadata_queries = PostgresqlMetadataQueries

    Database.data_types = DATA_TYPES

    @property
    def dbms_name(self) -> str:
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
            detach=True,
            network=NETWORK_NAME,
            volumes={
                # Mount a volume for PostgreSQL data persistence
                f'{self.hostname}_data': {
                    'bind': '/var/lib/postgresql/data',
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


        
