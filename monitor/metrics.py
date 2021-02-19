"""
Calculate the online evaluation metric - average rating on recommended movies
"""

import pandas as pd
import elasticapm
from models import RecommendationRating, CanaryRecommendationRating
from database import readRecommendations, readCanaryRecommendations
from database import createRecommendationRating, createCanaryRecommendationRating
from database import readRecommendationRatingAverage, readCanaryRecommendationRatingAverage


def getCurrentModelMetric():
    return readRecommendationRatingAverage()


def getCanaryModelMetric():
    return readCanaryRecommendationRatingAverage()


@elasticapm.capture_span()
def calculateCurrentModelMetric():
    count = 0
    userRecoDict = {}
    ratings = pd.read_csv('./data/kafka_raw_ratings_new.csv')
    # for all rating entries
    for _, row in ratings.iterrows():
        userid = str(row['userid'])
        movieid = row['movieid']
        rating = row['rating']
        # get the list of recommended movies to the user
        recoMovies = []
        # first check in-memory dict
        if userid in userRecoDict:
            recoMovies = userRecoDict[userid]
        else:  # else fetch from db and also persist to in-memory dict
            recoMovies = readRecommendations(userid)
            userRecoDict[userid] = recoMovies
        # if movie was recommended to the user, capture rating in db
        if movieid in recoMovies:
            recoRating = RecommendationRating(rating=rating)
            createRecommendationRating(recoRating)


def calculateCanaryModelMetric():
    count = 0
    userRecoDict = {}
    ratings = pd.read_csv('./data/kafka_raw_ratings_new.csv')
    # for all rating entries
    for _, row in ratings.iterrows():
        userid = str(row['userid'])
        movieid = row['movieid']
        rating = row['rating']
        # get the list of recommended movies to the user
        recoMovies = []
        # first check in-memory dict
        if userid in userRecoDict:
            recoMovies = userRecoDict[userid]
        else:  # else fetch from db and also persist to in-memory dict
            recoMovies = readCanaryRecommendations(userid)
            userRecoDict[userid] = recoMovies
        # if movie was recommended to the user, capture rating in db
        if movieid in recoMovies:
            recoRating = CanaryRecommendationRating(rating=rating)
            createCanaryRecommendationRating(recoRating)
