from .result import QueryResult
from .util import Column

from typing import Self
import pandas as pd


class QueryResultDataset(QueryResult):
    '''Represents the result of a SQL query that returned a dataset.'''
    def __init__(self, result: pd.DataFrame, *,
                  query: str,
                  columns: list[Column],
                  query_type: str, query_goal: str,
                  notices: list = []):
        super().__init__(
            query=query,
            success=True,
            query_type=query_type,
            query_goal=query_goal,
            notices=notices,
            data_type='dataset')
        self._result = result
        self.columns = columns

    @property
    def result_html(self) -> str:
        result = self._result.replace({None: 'NULL'})

        result = result.to_html(
            classes='table table-bordered table-hover table-responsive',
            show_dimensions=True,
            border=0
        )
        result = result.replace('<thead>', '<thead class="table-dark">').replace('<tbody>', '<tbody class="table-group-divider">')
        return result
    
    @property
    def result_text(self) -> str:
        return self._result.replace({None: 'NULL'}).to_csv()
    
    def has_same_columns(self, other: Self) -> bool:
        '''Checks if the columns of this result are the same as those of another result.'''
        return self.columns == other.columns
    
    def compare_column_names(self, other: Self) -> bool:
        '''Compares the columns of this result with another result and returns lists of missing, redundant, and wrong type columns.'''
        if len(self.columns) != len(other.columns):
            return False

        for col1, col2 in zip(self.columns, other.columns):
            if col1.name != col2.name:
                return False
        
        return True
    
    def compare_column_types(self, other: Self) -> list[Column]:
        '''Compares the data types of the columns in this result with another result and returns a list of columns with mismatched types.'''
        wrong_types = []
        for col1, col2 in zip(self.columns, other.columns):
            if col1.data_type != col2.data_type:
                wrong_types.append(col1)
        return wrong_types
    
    import pandas as pd

    def compare_results(self, other: Self) -> tuple[bool, pd.DataFrame]:
        # Count row occurrences
        vc_self = self._result.value_counts().reset_index(name='count_self')
        vc_other = other._result.value_counts().reset_index(name='count_other')

        # Outer join on all columns to align rows
        merged = pd.merge(
            vc_self, vc_other,
            on=self._result.columns.tolist(),
            how='outer'
        ).fillna(0)

        merged['diff'] = merged['count_self'] - merged['count_other']

        # Helper to expand rows with origin label
        def expand_rows(df, sign, origin):
            rows = df[df['diff'] * sign > 0]
            rows = rows.loc[rows.index.repeat(rows['diff'].abs())]
            rows = rows[self._result.columns.tolist()]
            rows['only_in'] = origin
            return rows

        only_in_self = expand_rows(merged, 1, 'Your query')
        only_in_other = expand_rows(merged, -1, 'Solution')

        diff_rows = pd.concat([only_in_self, only_in_other], ignore_index=True)

        are_equal = diff_rows.empty

        return are_equal, diff_rows

