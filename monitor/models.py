from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.types import ARRAY
from sqlalchemy.sql import func

Base = declarative_base()


class Recommendation(Base):
    __tablename__ = 'recommendations'
    id = Column(Integer, primary_key=True)
    served_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(String)
    model = Column(String)
    model_num = Column(Integer)
    movie_ids = Column(ARRAY(String))

    def __repr__(self):
        return "<Recommendation(id='{}', served_at='{}', user_id={}, model={}, model_num={}, movie_ids={})>" \
            .format(self.id, self.served_at, self.user_id, self.model, self.model_num, self.movie_ids)


class RecommendationRating(Base):
    __tablename__ = 'recommendationratings'
    id = Column(Integer, primary_key=True)
    captured_at = Column(DateTime(timezone=True), server_default=func.now())
    rating = Column(Integer)

    def __repr__(self):
        return "<RecommendationRating(id='{}', captured_at='{}', rating={})>" \
            .format(self.id, self.captured_at, self.rating)


class CanaryRecommendation(Base):
    __tablename__ = 'canaryrecommendations'
    id = Column(Integer, primary_key=True)
    served_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(String)
    model = Column(String)
    model_num = Column(Integer)
    movie_ids = Column(ARRAY(String))

    def __repr__(self):
        return "<CanaryRecommendation(id='{}', served_at='{}', user_id={}, model={}, model_num={}, movie_ids={})>" \
            .format(self.id, self.served_at, self.user_id, self.model, self.model_num, self.movie_ids)


class CanaryRecommendationRating(Base):
    __tablename__ = 'canaryrecommendationratings'
    id = Column(Integer, primary_key=True)
    captured_at = Column(DateTime(timezone=True), server_default=func.now())
    rating = Column(Integer)

    def __repr__(self):
        return "<CanaryRecommendationRating(id='{}', captured_at='{}', rating={})>" \
            .format(self.id, self.captured_at, self.rating)
