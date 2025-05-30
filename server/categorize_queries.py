import pandas as pd
from server.sql import SQLCode
from tqdm import tqdm
from dav_tools import argument_parser

def categorize_queries(filename_in: str, filename_out: str):
    '''Categorize SQL queries in a CSV file by their type. The results are saved to a new CSV file.'''

    df = pd.read_csv(filename_in)

    for idx, row in tqdm(df.iterrows(), total=len(df)):
        if pd.isna(row['query_type']):
            df.at[idx, 'query_type'] = SQLCode(row['query']).query_type

    df.to_csv(filename_out, index=False)

if __name__ == '__main__':
    argument_parser.add_argument('filename_in', type=str, help='Input CSV file with SQL queries')
    argument_parser.add_argument('filename_out', type=str, help='Output CSV file to save categorized queries')
    argument_parser.args

    categorize_queries(argument_parser.args.filename_in, argument_parser.args.filename_out)
    