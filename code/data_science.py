import numpy as np
import pandas as pd
from scipy.sparse.linalg import svds
from typing import Dict, List


def train_model(train_table: pd.DataFrame, viewed_table: pd.DataFrame) -> List:
    """train model generating data frame of predicted ratings on -1 to 1 scale.

            Args:
                train_table from data split, viewed_table

            Returns:
                A data frame of predicted ratings on -1 to 1 scale

    """

    """"""
    # construct numpy array
    #nan_data = train_table.replace(0.0, np.NaN).to_numpy()
    #user_ratings_mean = np.nanmean(nan_data, axis=1)
    unviewed_table = viewed_table.apply(lambda x: 1 - x)
    # unviewed = unviewed_table.to_numpy()

    # construct numpy array
    data = train_table.to_numpy()
    user_ratings_mean = np.mean(data, axis=1)
    # factors in individual interpretation of the scale
    data_demeaned = data - user_ratings_mean.reshape(-1, 1)

    # use scipy sparse's svd to avoid 'killed: 9' memory issues
    U, sigma, Vt = svds(data_demeaned, k=25)

    sigma = np.diag(sigma)

    all_predictions = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1, 1)
    all_predictions_table = pd.DataFrame(all_predictions).set_index(viewed_table.index)
    all_predictions_table.set_axis(viewed_table.columns, axis='columns', inplace=True)


    # given already viewed movies a rating of 0. Note these will still be taken ahead of adverse movies
    predictions_table = pd.DataFrame(np.multiply(all_predictions_table,
                                                 unviewed_table.to_numpy()).set_index(viewed_table.index))
    predictions_table.set_axis(viewed_table.columns, axis='columns', inplace=True)

    return [all_predictions_table, predictions_table]


def evaluate_model(predictions_table: pd.DataFrame, ratings_table: pd.DataFrame,
                   test_table: pd.DataFrame, viewed_table: pd.DataFrame,
                   all_predictions_table: pd.DataFrame) -> Dict:
    """evaluates model returning rmse and coverage number

                Args:
                    predictions_table, ratings_table, test_table, viewed_table, all_predictions_table

                Returns:
                    dictionary with RMSE and Coverage values

    """

    viewed = viewed_table.to_numpy()
    predictions = predictions_table.to_numpy()
    all_predictions = all_predictions_table.to_numpy()
    ratings = ratings_table.to_numpy()
    test = test_table.to_numpy(copy=True)
    test_demeaned = test - np.mean(test, axis=1).reshape(-1, 1)
    test_set = test_table.apply(lambda x: x != 0.0).astype(int).to_numpy()

    result = dict()

    # Test set evaluation
    test_predictions = np.multiply(all_predictions, test_set)
    diff = np.subtract(test_predictions, test_demeaned)
    rmse = np.sqrt(np.mean(np.square(diff)))
    result.update({"RMSE": rmse})
    mae = np.mean(np.absolute(diff))
    result.update({"MAE": mae})

    # overall evaluation
    movies_recommended = set()
    i = 0
    for index, row in predictions_table.iterrows():
        if i > 10000: break
        else: i += 1

        labels = row.nlargest(20).keys().tolist()
        for movie in labels:
            movies_recommended.update(movie)

    result.update({"Coverage": len(movies_recommended)})

    return result
