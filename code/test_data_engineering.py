from data_engineering import create_ratings_table, create_viewed_table
import pandas as pd
import numpy as np


def create_ratings_table_test():
    data = {'time': ['2020-04-07T09:09:17', '2020-04-07T09:11:42', '2020-04-07T09:15:22'],
            'userid': ['241832', '393843', '434614'],
            'movieid': ['pearl+harbor+2001', 'escape+to+witch+mountain+1975', 'batman+1989'],
            'rating': [4, 2, 3]}

    df = pd.DataFrame(data, columns=['time', 'userid', 'movieid', 'rating'])
    parameters = dict({'random_state': 42, 'min_movies': 0, 'min_reviews': 0})

    # Check for NaN values, rating is within [0, 5] range, userid is the index value, column names are movie values

    table, test = create_ratings_table(df, df, parameters)

    assert table['pearl+harbor+2001'].between(0, 5, inclusive=True).all()
    assert table['escape+to+witch+mountain+1975'].between(0, 5, inclusive=True).all()
    assert table['batman+1989'].between(0, 5, inclusive=True).all()

    for index, row in table.iterrows():
        assert index in set(['241832', '393843', '434614'])

    for column in table.columns:
        assert column in set(['pearl+harbor+2001', 'escape+to+witch+mountain+1975', 'batman+1989'])
    return None


def create_viewed_table_test():
    data = {'pearl+harbor+2001': [1.0, 3.0, 4.0],
            'escape+to+witch+mountain+1975': [3.0, 0.0, 1.0],
            'batman+1989': [0.0, 5.0, 0.0]}
    df = pd.DataFrame(data, columns=['pearl+harbor+2001', 'escape+to+witch+mountain+1975', 'batman+1989'], index=[434614, 43656, 207438])

    table = create_viewed_table(df)

    # confirm unviewed films are 0 and viewed are 1
    assert table['pearl+harbor+2001'].between(0, 1, inclusive=True).all()
    assert table['escape+to+witch+mountain+1975'].between(0, 1, inclusive=True).all()
    assert table['batman+1989'].between(0, 1, inclusive=True).all()

    assert (np.multiply(table.to_numpy(), df.to_numpy()) == df.to_numpy()).all()
    assert (np.multiply(table.to_numpy(), table.to_numpy()) == table.to_numpy()).all()

    return None



