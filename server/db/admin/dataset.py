from dav_tools import database
from .connection import db, SCHEMA

def get(dataset_name: str | None) -> str:
    '''Get the dataset for a given dataset ID'''

    if dataset_name is None:
        return '-- No dataset provided'

    query = database.sql.SQL(
        '''
        SELECT dataset
        FROM {schema}.datasets
        WHERE name = {dataset_name}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        dataset_name=database.sql.Placeholder('dataset_name')
    )

    result = db.execute_and_fetch(query, {
        'dataset_name': dataset_name
    })

    if len(result) == 0:
        return '-- No dataset provided'

    return result[0][0]

def list_all(username: str) -> list[dict]:
    '''Get all datasets visible to the user'''

    query = database.sql.SQL(
    '''
        SELECT
            dataset_name
        FROM
            {schema}.has_dataset
        WHERE
            username = {username}
        ORDER BY
            dataset_name
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )
    result = db.execute_and_fetch(query, {
        'username': username
    })
    return [ row[0] for row in result ]

def add(name: str, dataset: str) -> None:
    '''Add a dataset to the database'''

    query = database.sql.SQL(
    '''
        INSERT INTO {schema}.datasets(name, dataset)
        VALUES ({name}, {dataset})
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        name=database.sql.Placeholder('name'),
        dataset=database.sql.Placeholder('dataset')
    )

    db.execute(query, {
        'name': name,
        'dataset': dataset
    })