import pandas as pd
import random
from sklearn.model_selection import train_test_split
from typing import List


def create_train_test_split(ratings: pd.DataFrame, parameters) -> List:
    """ To ensure full reproducability train test/split is performed across all raw_kafka_ratings.
        Only uses the last parameters['training_rows'] number of ratings to avoid growing resource consumption.

        Args:
            ratings: Source data.
        Returns:
            raw_training_ratings, raw_testing_ratings, kafka_offset : split kafka ratings, number of rows considered

    """

    max_rows = parameters['max_rows']
    kafka_offset = parameters['kafka_offset']

    test_percentage = int(parameters["test_size"])

    ratings.drop_duplicates()

    if kafka_offset != -1:
        ratings = ratings[:kafka_offset:]
    else:
        kafka_offset = len(ratings.index)

    train, test = train_test_split(ratings, test_size=(test_percentage / 100), random_state=parameters["random_state"])

    raw_training_ratings = train.tail(max_rows)
    raw_testing_ratings = test.tail(int((max_rows / 100) * test_percentage))

    return [raw_training_ratings, raw_testing_ratings, kafka_offset]


def create_ratings_table(raw_training_ratings: pd.DataFrame, raw_testing_ratings: pd.DataFrame, parameters) -> List:
    """Preprocess the data for ratings.

        Args:
            ratings: Source data.
        Returns:
            ratings in a table with user rows and movie columns .

    """

    # ratings.drop(ratings.columns[0], axis=1)
    # ratings.drop_duplicates()
    #ratings = ratings.query('rating >=3')
    raw_training_ratings.reset_index(drop=True, inplace=True)
    raw_testing_ratings.reset_index(drop=True, inplace=True)

    #only consider movies with over n ratings
    n = int(parameters['min_reviews'])
    movies = raw_training_ratings.movieid.value_counts()
    movies = movies[movies>n].index.tolist()

    #only consider ratings from users who have rated over n movies
    n = int(parameters['min_movies'])
    users = raw_training_ratings.userid.value_counts()
    users = users[users > n].index.tolist()

    ratings = raw_training_ratings.query('userid in @users')

    ratings = ratings.query('movieid in @movies')
    ratings.reset_index(drop=True, inplace=True)

    #transform data into matrix
    movies = set()
    users = dict(dict())

    test_users = dict(dict())

    for i in range(len(ratings)):
        user = ratings.loc[i, 'userid']
        movie = ratings.loc[i, 'movieid']
        rating = ratings.loc[i, 'rating']

        movies.add(movie)
        if user in users:
            users[user].update({movie: rating})
            test_users[user].update({movie: 0.0})
        else:
            users.update({user: dict({movie: rating})})
            test_users.update({user: dict({movie: 0.0})})

    for i in range(len(raw_testing_ratings)):
        user = raw_testing_ratings.loc[i, 'userid']
        movie = raw_testing_ratings.loc[i, 'movieid']
        rating = raw_testing_ratings.loc[i, 'rating']

        if user in users:
            users[user].update({movie: 0.0})
            test_users[user].update({movie: rating})



    # construct data frame
    df = pd.DataFrame.from_dict(users, orient='index')
    test_df = pd.DataFrame.from_dict(test_users, orient='index')

    ratings_table = df.fillna(value=0.0)
    test_ratings_table = test_df.fillna(value=0.0)

    return [ratings_table, test_ratings_table]


def create_viewed_table(ratings_table: pd.DataFrame) -> pd.DataFrame:
    """ Creates True/false table representing whether a user has watched each movie
        with identical rows and columns to the ratings table.

        Args:
            ratings_table: Preprocessed data for ratings stored in a dataframe
        Returns:
            table of 1/0 viewership.

    """

    return ratings_table.apply(lambda x: x > 0.0).astype(int)
