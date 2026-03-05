from .data_types import DATA_TYPES
from .connection import MySQLConnection
from .queries import MySQLBuiltinQueries, MySQLMetadataQueries
from ..database import Database

import dav_tools
import os
import docker
from docker.models.containers import Container

NETWORK_NAME = os.getenv('DB_USERS_NETWORK', 'db_users')


class MySQLDatabase(Database):
    def __init__(self, dbname: str):
        super().__init__(
            dbname=dbname,
            port=3306,
            dbms_name='mysql',
            admin_username='root',
            builtin_queries=MySQLBuiltinQueries,
            metadata_queries=MySQLMetadataQueries,
            data_types=DATA_TYPES,
        )

    def create_container(self) -> Container:
        client = docker.from_env()

        container = client.containers.run(
            image='mysql:latest',
            name=self.hostname,
            environment={
                'MYSQL_ALLOW_EMPTY_PASSWORD': 'yes',
                'MYSQL_DATABASE': 'default',
            },
            detach=True,
            network=NETWORK_NAME,
            volumes={
                # Mount a volume for MySQL data persistence
                f'{self.hostname}_data': {
                    'bind': '/var/lib/mysql',
                    'mode': 'rw',
                }
            },
            labels=self.container_labels,
            mem_limit='512m',
            nano_cpus=1_000_000_000,  # Limit to 1 CPU
        )

        # Wait for the container to be ready
        container.reload()
        while container.status != 'running':
            dav_tools.messages.info(f'Waiting for container {self.hostname} to be running...')
            container.reload()

        return container

    def _get_connection(self, autocommit: bool = True) -> MySQLConnection:
        return MySQLConnection(host=self.hostname, port=self.port, autocommit=autocommit)