'''
Code modified from:
https://github.com/LearnDataSci/article-resources/blob/master/Guide%20to%20Using%20Databases%20with%20Python%20Postgres%2C%20SQLAlchemy%2C%20and%20Alembic/project/crud.py
'''

from datetime import datetime

from sqlalchemy import create_engine
from models import Base, Recommendation
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True)

Session = sessionmaker(bind=engine)

@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def recreate_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)