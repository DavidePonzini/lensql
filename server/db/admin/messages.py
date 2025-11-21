from dav_tools import database
from .connection import db, SCHEMA

from .queries import Query
from .users import User

class Message:
    def __init__(self, message_id: int, *,
                 query: Query | None = None
                ) -> None:
        self.message_id = message_id

        # Lazy properties
        self._query = query

    @property
    def query(self) -> Query:
        '''Get the query associated with this message'''
        if self._query is None:
            q = database.sql.SQL(
            '''
                SELECT
                    m.query_id
                FROM {schema}.messages AS m
                WHERE m.id = {message_id}
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                message_id=database.sql.Placeholder('message_id')
            )

            result = db.execute_and_fetch(q, {
                'message_id': self.message_id
            })

            assert result is not None and len(result) == 1 and len(result[0]) == 1, 'Failed to fetch message query.'

            query_id = result[0][0]
            self._query = Query(query_id)

        return self._query

    @staticmethod
    def log(answer: str, button: str, query: Query, msg_idx: int) -> 'Message':
        '''Log a new message'''

        result = db.insert(SCHEMA, 'messages', {
            'query_id': query.query_id,
            'answer': answer,
            'button': button,
            'msg_idx': msg_idx,
        }, ['id'])

        assert result is not None and len(result) == 1 and len(result[0]) == 1, 'Failed to log message.'

        message_id = result[0][0]

        return Message(message_id, query=query)
    
    def log_feedback(self, feedback: bool, user: User) -> None:
        '''Log feedback for a message'''

        query = database.sql.SQL(
        '''
            UPDATE {schema}.messages AS m
            SET
                feedback = {feedback},
                feedback_ts = NOW()
            FROM {schema}.queries AS q
            JOIN {schema}.query_batches AS qb ON q.batch_id = qb.id
            WHERE m.id = {message_id}
            AND m.query_id = q.id
            AND qb.username = {username}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            feedback=database.sql.Placeholder('feedback'),
            message_id=database.sql.Placeholder('message_id'),
            username=database.sql.Placeholder('username')
        )

        db.execute(query, {
            'feedback': feedback,
            'message_id': self.message_id,
            'username': user.username
        })
