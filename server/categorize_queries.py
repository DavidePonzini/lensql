import pandas as pd
from server.sql import SQLCode
from tqdm import tqdm

def categorize_queries(filename_in: str, filename_out: str):
    '''Categorize SQL queries in a CSV file by their type. The results are saved to a new CSV file.'''

    df = pd.read_csv(filename_in)

    for idx, row in tqdm(df.iterrows(), total=len(df)):
        if pd.isna(row['query_type']):
            df.at[idx, 'query_type'] = SQLCode(row['query']).query_type

    df.to_csv(filename_out, index=False)

if __name__ == '__main__':
    categorize_queries('q.csv', 'q_out.csv')
    