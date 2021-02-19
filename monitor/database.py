from crud import session_scope
from sqlalchemy.sql import func
from models import Recommendation, CanaryRecommendation
from models import RecommendationRating, CanaryRecommendationRating
from datetime import datetime, timedelta


def createRecommendation(reco: Recommendation):
    with session_scope() as s:
        s.add(reco)


def createCanaryRecommendation(reco: CanaryRecommendation):
    with session_scope() as s:
        s.add(reco)


def readRecommendations(userid):
    with session_scope() as s:
        since = datetime.now() - timedelta(hours=0.3)
        # create query to get all recommendations served to user in the last 3 hours
        q = s.query(Recommendation).filter(Recommendation.served_at >
                                           since).filter(Recommendation.user_id == userid)
        recommendedMovies = []
        # get a list of all movies recommended to the user and return
        for row in q.all():
            recommendedMovies += row.movie_ids
        return recommendedMovies


def readCanaryRecommendations(userid):
    with session_scope() as s:
        since = datetime.now() - timedelta(hours=0.3)
        # create query to get all recommendations served to user in the last 3 hours
        q = s.query(CanaryRecommendation).filter(CanaryRecommendation.served_at >
                                                 since).filter(CanaryRecommendation.user_id == userid)
        recommendedMovies = []
        # get a list of all movies recommended to the user and return
        for row in q.all():
            recommendedMovies += row.movie_ids
        return recommendedMovies


def createRecommendationRating(rating: RecommendationRating):
    with session_scope() as s:
        s.add(rating)


def createCanaryRecommendationRating(rating: CanaryRecommendationRating):
    with session_scope() as s:
        s.add(rating)


def readRecommendationRatingAverage():
    with session_scope() as s:
        since = datetime.now() - timedelta(hours=0.3)
        return s.query(func.avg(RecommendationRating.rating)).filter(RecommendationRating.captured_at > since).scalar()


def readCanaryRecommendationRatingAverage():
    with session_scope() as s:
        since = datetime.now() - timedelta(hours=0.3)
        return s.query(func.avg(CanaryRecommendationRating.rating)).filter(CanaryRecommendationRating.captured_at > since).scalar()
