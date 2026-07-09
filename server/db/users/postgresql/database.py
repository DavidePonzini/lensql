
from sqlscope.catalog import Catalog

from server.db.users.queries import BuiltinQueries, MetadataQueries

from .data_types import DATA_TYPES
from .connection import PostgresqlConnection
from .queries import PostgresqlBuiltinQueries, PostgresqlMetadataQueries
from ..database import Database

import dav_tools
import os
import docker
from docker.models.containers import Container
from sqlscope import Catalog, load_catalog
from pathlib import Path

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
    
    def get_search_path(self) -> str:
        result = super().get_search_path()

        # Additional logic to handle PostgreSQL-specific search path behavior

        # remove $user from the search path (default value, not used by lensql)
        # using ', ' prevents removing $user if it's the only value in the search path
        result = result.replace('"$user", ', '')

        # postgres automatically adds double quotes around the search path if it special characters or spaces, so we need to remove them to get the actual search path
        if result.startswith('"') and result.endswith('"'):
            result = result[1:-1]

        # actual double quotes in the search path are escaped with double quotes, so we need to replace them with single quotes to get the actual search path
        result = result.replace('""', '"')

        return result

    def get_system_catalog(self) -> Catalog:
        dir = Path(__file__).parent

        return load_catalog(f'{dir}/system_catalog.json')
