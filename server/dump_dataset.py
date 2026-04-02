import json
import sys
from dataclasses import asdict, dataclass

import dav_tools
from dav_tools import database

from server.db.admin import Dataset, Exercise, User
from server.db.admin.connection import SCHEMA, db

ADMIN_USERNAME = 'lens'
ADMIN_USER = User(ADMIN_USERNAME)


@dataclass(frozen=True)
class ExerciseJSON:
    title: str
    request: str
    solutions: list[str]
    is_hidden: bool
    difficulty: int | None
    error: int | None
    learning_objectives: list[str]
    created_by: str | None


@dataclass(frozen=True)
class DatasetJSON:
    dataset_id: str
    title: str
    description: str
    dataset_str: str
    search_path: str | None
    dbms: str | None
    domain: str | None
    exercises: list[ExerciseJSON]


def dump_dataset(dataset_id: str) -> None:
    dataset_query = database.sql.SQL(
        '''
            SELECT
                id,
                name,
                description,
                dataset,
                search_path,
                dbms,
                domain
            FROM {schema}.datasets
            WHERE id = {dataset_id}
        '''
    ).format(
        schema=database.sql.Identifier(SCHEMA),
        dataset_id=database.sql.Placeholder('dataset_id'),
    )
    dataset_rows = db.execute_and_fetch(dataset_query, {'dataset_id': dataset_id})
    if not dataset_rows:
        raise ValueError(f'Dataset with ID {dataset_id} does not exist.')

    exercise_query = database.sql.SQL(
        '''
            SELECT
                e.title,
                e.request,
                e.solutions,
                e.is_hidden,
                e.generation_difficulty,
                e.generation_error,
                e.created_by,
                COALESCE(
                    ARRAY(
                        SELECT hlo.objective_id
                        FROM {schema}.has_learning_objective hlo
                        WHERE hlo.exercise_id = e.id
                        ORDER BY hlo.objective_id
                    ),
                    ARRAY[]::text[]
                ) AS learning_objectives
            FROM {schema}.exercises e
            WHERE e.dataset_id = {dataset_id}
            ORDER BY e.id
        '''
    ).format(
        schema=database.sql.Identifier(SCHEMA),
        dataset_id=database.sql.Placeholder('dataset_id'),
    )
    exercise_rows = db.execute_and_fetch(exercise_query, {'dataset_id': dataset_id})

    dataset_row = dataset_rows[0]
    dataset_json = DatasetJSON(
        dataset_id=dataset_row[0],
        title=dataset_row[1],
        description=dataset_row[2],
        dataset_str=dataset_row[3] or '',
        search_path=dataset_row[4],
        dbms=dataset_row[5],
        domain=dataset_row[6],
        exercises=[
            ExerciseJSON(
                title=row[0],
                request=row[1],
                solutions=json.loads(row[2]) if row[2] else [],
                is_hidden=row[3],
                difficulty=row[4],
                error=row[5],
                created_by=row[6],
                learning_objectives=list(row[7] or []),
            )
            for row in exercise_rows
        ],
    )

    print(json.dumps(asdict(dataset_json), indent=2, ensure_ascii=False))


def _insert_dataset(dataset: DatasetJSON) -> str:
    created_dataset = Dataset.create(
        title=dataset.title,
        description=dataset.description,
        dataset_str=dataset.dataset_str,
        domain=dataset.domain,
        search_path=dataset.search_path,
        dbms=dataset.dbms or 'postgresql',
    )
    created_dataset.add_participant(ADMIN_USER)
    created_dataset.set_owner_status(ADMIN_USER, True)
    return created_dataset.dataset_id


def _insert_exercise(dataset_id: str, exercise: ExerciseJSON) -> None:
    created_exercise = Exercise.create(
        title=exercise.title,
        user=User(exercise.created_by or ADMIN_USERNAME),
        dataset_id=dataset_id,
        request=exercise.request,
        solutions=exercise.solutions,
        difficulty=exercise.difficulty,
        error=exercise.error,
    )
    created_exercise.set_hidden(exercise.is_hidden)

    if exercise.learning_objectives:
        for objective_id in exercise.learning_objectives:
            created_exercise.set_learning_objective(objective_id)


def load_dataset() -> None:
    payload = json.load(sys.stdin)
    dataset = DatasetJSON(
        dataset_id=payload['dataset_id'],
        title=payload['title'],
        description=payload['description'],
        dataset_str=payload.get('dataset_str', ''),
        search_path=payload.get('search_path'),
        dbms=payload.get('dbms'),
        domain=payload.get('domain'),
        exercises=[
            ExerciseJSON(
                title=exercise['title'],
                request=exercise['request'],
                solutions=list(exercise.get('solutions', [])),
                is_hidden=bool(exercise.get('is_hidden', False)),
                difficulty=exercise.get('difficulty'),
                error=exercise.get('error'),
                learning_objectives=list(exercise.get('learning_objectives', [])),
                created_by=exercise.get('created_by'),
            )
            for exercise in payload.get('exercises', [])
        ],
    )

    dataset_id = _insert_dataset(dataset)
    for exercise in dataset.exercises:
        _insert_exercise(dataset_id, exercise)
    dav_tools.messages.info(f'Dataset loaded with ID: {dataset_id}')


if __name__ == '__main__':
    dav_tools.argument_parser.add_argument('action', help='Action to perform', choices=['dump', 'load'])
    dav_tools.argument_parser.add_argument('dataset', nargs='?', help='ID of the dataset to dump')
    dav_tools.argument_parser.parse_args()

    if dav_tools.argument_parser.args.action == 'dump':
        if not dav_tools.argument_parser.args.dataset:
            dav_tools.messages.critical_error('Dataset ID is required for dump.')
        dump_dataset(dav_tools.argument_parser.args.dataset)
    else:
        load_dataset()
