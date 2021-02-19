import pandas as pd
from scipy.sparse.linalg import svds
import numpy as np
import json
from data_linter.lint import Linter
from data_linter.impose_data_types import impose_metadata_types_on_pd_df
from IPython.display import Markdown

try:
    ratings = pd.read_csv(
        '/home/teamtitanic/new_datasets/kafka_raw_ratings_new.csv').drop_duplicates()
    ratings.reset_index(drop=True, inplace=True)

    # Data quality check on clean data
    with open("raw_ratings_schema.json") as schema_definition:
        schema = json.load(schema_definition)
        linter = Linter(ratings, schema)
        linter.check_all()
        print(linter.markdown_report())
        impose_metadata_types_on_pd_df(
            df=ratings, meta_data=schema, errors='raise')
    schema_definition.close()

except FileNotFoundError:
    print("File does not exist")
