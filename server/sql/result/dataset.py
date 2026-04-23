from .result import QueryResult
from .util import Column

from ..code import SQLCode

from typing import Self
import pandas as pd
from flask_babel import _


class QueryResultDataset(QueryResult):
    '''Represents the result of a SQL query that returned a dataset.'''
    def __init__(self, result: pd.DataFrame, *,
                  query: SQLCode,
                  columns: list[Column],
                  notices: list = []):
        super().__init__(
            query=query,
            success=True,
            notices=notices,
            data_type='dataset')
        self._result = result
        self.columns = columns

    @property
    def result_html(self) -> str:
        result = self._result.replace({None: 'NULL'})

        rows = len(result)
        cols = len(result.columns)

        result = result.to_html(
            classes='table table-bordered table-hover table-responsive',
            show_dimensions=False,
            border=0
        )
        
        # Styling options go here, otherwise HTML tags are converted to text and shown in the result table instead of being rendered as HTML. 
        result = result.replace(
            '<thead>',
            '<thead class="table-dark">'
        ).replace(
            '<tbody>',
            '<tbody class="table-group-divider">'
        ).replace(
            '__UNEXPECTED__',
            f'<b style="color: red;">{_("Unexpected")}:</b>'
        ).replace(
            '__MISSING__',
            f'<b style="color: blue;">{_("Missing")}:</b>'
        ).replace(
            '__CORRECT__',
            f'<b style="color: green;">{_("Correct")}:</b>'
        )

        row_str = _("row") if rows == 1 else _("rows")
        col_str = _("column") if cols == 1 else _("columns")
        dimensions = f'<p><i>{rows} {row_str} × {cols} {col_str}</i></p>'

        return f'{dimensions}\n{result}'
    
    @property
    def result_text(self) -> str:
        return self._result.replace({None: 'NULL'}).to_csv()

    def row_count(self) -> int:
        '''Returns the number of rows in the result.'''
        return len(self._result)

    def has_same_columns(self, other: Self) -> bool:
        '''Checks if the columns of this result are the same as those of another result.'''
        return self.columns == other.columns
    
    def compare_column_names(self, other: Self) -> bool:
        '''Compares the columns of this result with another result and returns lists of missing, redundant, and wrong type columns.'''
        if len(self.columns) != len(other.columns):
            return False

        # for col1, col2 in zip(self.columns, other.columns):
        #     if col1.name != col2.name:
        #         return False
        
        return True
    
    def compare_column_types(self, other: Self) -> list[Column]:
        '''Compares the data types of the columns in this result with another result and returns a list of columns with mismatched types.'''
        wrong_types = []
        for col1, col2 in zip(self.columns, other.columns):
            if col1.data_type != col2.data_type:
                wrong_types.append(col1)
        return wrong_types
    
    def compare_results(self, other: Self) -> tuple[bool, pd.DataFrame]:
        self_cp = self._result.copy()
        other_cp = other._result.copy()

        # NOTE: duplicate columns names are not supported, as they would cause issues with pd.merge
        column_names_no_duplicates: list[str] = []
        for col in self.columns:
            count = column_names_no_duplicates.count(col.name)
            if count == 0:
                column_names_no_duplicates.append(col.name)
            else:
                column_names_no_duplicates.append(f"{col.name}_{count}")

        self_cp.columns = column_names_no_duplicates
        other_cp.columns = column_names_no_duplicates

        # Count row occurrences
        vc_self = self_cp.value_counts().reset_index(name='__count_self__')
        vc_other = other_cp.value_counts().reset_index(name='__count_other__')

        # Outer join on all columns to align rows
        merged = pd.merge(
            vc_self, vc_other,
            on=column_names_no_duplicates,
            how='outer'
        ).fillna(0)

        merged['__diff__'] = merged['__count_self__'] - merged['__count_other__']

        # Helper to expand rows with origin label
        def expand_rows(df: pd.DataFrame, label: str) -> pd.DataFrame:
            repeat_counts = df['__diff__'].abs().where(
                df['__diff__'].ne(0),
                df['__count_self__'],
            ).astype(int)

            rows = df.loc[df.index.repeat(repeat_counts)]
            rows = rows[column_names_no_duplicates]
            rows['check_result'] = label
            return rows

        unexpected_rows = expand_rows(merged[merged['__diff__'] > 0], f'__UNEXPECTED__ {_("your query should not return this row")}')
        missing_rows = expand_rows(merged[merged['__diff__'] < 0], f'__MISSING__ {_("your query should return this row but it does not")}')
        correct_rows = expand_rows(merged[merged['__diff__'] == 0], '__CORRECT__')

        # for correct rows, print a single row with no values and the amount of correct rows in the check_result column
        if len(correct_rows) == 0:
            # Don't print the correct rows if there are none
            correct_rows = correct_rows[0:0]
        else:
            count = len(correct_rows)

            correct_rows = correct_rows.iloc[0:1]
            correct_rows[column_names_no_duplicates] = ''
            correct_rows['check_result'] = f'__CORRECT__ {_("{count} rows in your query are correct").format(count=count)}'

        diff_rows = pd.concat([unexpected_rows, missing_rows], ignore_index=True)
        are_equal = diff_rows.empty

        result = pd.concat([diff_rows, correct_rows], ignore_index=True)

        return are_equal, result
