from dav_tools import database
from .connection import db, SCHEMA

def get(dataset_id: int | None) -> str:
    '''Get the dataset for a given dataset ID'''

    if dataset_id is None:
        return '-- No dataset provided'

    query = database.sql.SQL(
        '''
        SELECT dataset
        FROM {schema}.datasets
        WHERE id = {dataset_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        dataset_id=database.sql.Placeholder('dataset_id')
    )

    result = db.execute_and_fetch(query, {
        'dataset_id': dataset_id
    })

    if len(result) == 0:
        return '-- No dataset provided'

    return result[0][0]

def list_all(username: str) -> list[dict]:
    '''Get all datasets visible to the user'''

    query = database.sql.SQL(
    '''
        SELECT
            d.id,
            d.name
        FROM
            {schema}.datasets d
            JOIN {schema}.has_dataset hd ON d.id = hd.dataset_id
        WHERE
            hd.username = {username}
        ORDER BY
            d.name
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )
    result = db.execute_and_fetch(query, {
        'username': username
    })
    return [
        {
            'id': row[0],
            'name': row[1]
        }
        for row in result
    ]

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