import pandas as pd
import os
import csv

from data_engineering import create_train_test_split, create_ratings_table, create_viewed_table
from data_science import train_model, evaluate_model
from test_data_engineering import create_ratings_table_test, create_viewed_table_test

"""
When running on Jenkins ensure raw_ratings.csv and 
model.pickle have the correct names for the pipeline
"""

# CSV file locations
model_file = '/home/teamtitanic/datasets/model_versions.csv'
raw_ratings = '/home/teamtitanic/datasets/kafka_raw_ratings.csv'

# unit test
create_ratings_table_test()
create_viewed_table_test()

# Model parameters
parameters = dict({'test_size': 10,  # train percentage
                   'kafka_offset': -1,  # Used to recreate the same train test split
                   'random_state': 42,  # Random State
                   'min_movies': 10,  # minimum number of ratings for a user to be considered by model
                   'min_reviews': 3000,  # minimum number of reviews
                   'max_rows': 5000000,  # number of most recent kafka ratings to consider
                   })


# regathering data
raw_training_ratings, raw_testing_ratings, kafka_offset = create_train_test_split(pd.read_csv(raw_ratings),
                                                                                  parameters)
train_table, test_table = create_ratings_table(
    raw_training_ratings, raw_testing_ratings, parameters)

# creating viewed table
train_viewed_table = create_viewed_table(train_table)
test_viewed_table = create_viewed_table(test_table)
viewed_table = test_viewed_table.add(train_viewed_table)

# training model
all_predictions_table, predictions_table = train_model(
    train_table, viewed_table)

# saving model
predictions_table.to_pickle('gt3000.pickle')

# evaluating model
offline_measures = evaluate_model(
    predictions_table, train_table, test_table, viewed_table, all_predictions_table)

rmse = {'RMSE': offline_measures['RMSE']}
mae = {'MAE': offline_measures['MAE']}
coverage = {'Coverage': offline_measures['Coverage']}

offline_measure_df = pd.DataFrame(data=rmse, index=[0])
offline_measure_df.to_csv('offline_RMSE.csv', index=False)

offline_measure_df = pd.DataFrame(data=mae, index=[0])
offline_measure_df.to_csv('offline_MAE.csv', index=False)

offline_measure_df = pd.DataFrame(data=coverage, index=[0])
offline_measure_df.to_csv('offline_Coverage.csv', index=False)


model_version = "GIT HASH UNAVAILABLE"
if "GIT_COMMIT_HASH" in os.environ:
    model_version = os.environ["GIT_COMMIT_HASH"]

if not os.path.exists(model_file):
    with open(model_file, 'w') as csvfile:
        fileWriter = csv.writer(csvfile)
        fileWriter.writerow((['model_GIT', 'kafka_offset', 'ratings_used']))
        fileWriter.writerow(
            ([model_version, kafka_offset, parameters['max_rows']]))
else:
    with open(model_file, 'a') as csvfile:
        fileWriter = csv.writer(csvfile)
        fileWriter.writerow(
            ([model_version, kafka_offset, parameters['max_rows']]))
