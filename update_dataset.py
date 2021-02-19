import pandas as pd

try:
    # Get old dataset
    old_ratings = pd.read_csv(
        '/home/teamtitanic/datasets/kafka_raw_ratings.csv').drop_duplicates()
    old_ratings.reset_index(drop=True, inplace=True)

    # Get new dataset
    new_ratings = pd.read_csv(
        '/home/teamtitanic/datasets/kafka_raw_ratings_new.csv').drop_duplicates()
    new_ratings.reset_index(drop=True, inplace=True)

    # Merge the datasets
    combined_ratings = pd.concat([old_ratings, new_ratings], ignore_index=True)

    # Store the merged dataset in the VM
    combined_ratings.to_csv(
        '/home/teamtitanic/datasets/kafka_raw_ratings.csv', index=False)
except FileNotFoundError:
    print("File does not exist")
