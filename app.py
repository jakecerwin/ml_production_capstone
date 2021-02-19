from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
from models import Recommendation, CanaryRecommendation
from database import createRecommendation, createCanaryRecommendation
from crud import recreate_database
import logging
from elasticapm.contrib.flask import ElasticAPM
import os

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}
db = SQLAlchemy(app)

# Elastic APM Setup
app.config['ELASTIC_APM'] = {
    'SERVICE_NAME': 'Recommendation_Service',
    'SECRET_TOKEN': 'IQ85WNCvPFyPPoPsYD',
    'SERVER_URL': 'https://1223d14f8f12425fb2876dba0884a602.apm.us-east-1.aws.cloud.es.io:443',
}

apm = ElasticAPM(app, logging=logging.WARNING)

predictions = pd.read_pickle('./data/gt3000.pickle')
canary_predictions = pd.read_pickle('./data/canary.pickle')


# retrieve model information
model_info = pd.read_csv('./data/model_versions.csv')
df = pd.DataFrame(model_info.iloc[:, :].values)
recent = df.tail(2)

if 'model_GIT' in recent.tail(1).iloc[0]:
    last_model = recent.tail(1).iloc[0]['model_GIT']
    second_to_last = recent.head(1).iloc[0]['model_GIT']

model_version = "GIT Not Retrieved"
canary_version = "GIT Not Retrieved"
if 'Canary_Release' in os.environ:
    if os.environ["Canary_Release"] == 'Yes':
        canary_version = last_model
        model_version = second_to_last
    else:
        model_version = last_model
        canary_version = second_to_last


# route accepts positive integers as userid


@app.route('/recommend/<int:userid>/<int:model>')
def recommend(userid, model):
    global model_version
    global canary_version
    if model == 1:
        if userid in predictions.index:
            row = predictions.loc[userid]
            labels = row.nlargest(20).keys().tolist()
            result = ",".join(labels)
            app.logger.info(str(userid) + "->" + result)

            # Store the recommendation in database
            reco = Recommendation(
                user_id=userid,
                movie_ids=labels,
                model=model_version,
                model_num=1
            )
            createRecommendation(reco)

            return result
        else:
            app.logger.info("User not indexed. Returning defaults")

            # Store the recommendation in database
            reco = Recommendation(
                user_id=userid,
                movie_ids=getDefaults().split(','),
                model=model_version,
                model_num=1
            )
            createRecommendation(reco)

            # Return response
            return getDefaults()

    if model == 2:
        if userid in canary_predictions.index:
            row = predictions.loc[userid]
            labels = row.nlargest(20).keys().tolist()
            result = ",".join(labels)
            app.logger.info(str(userid) + "->" + result)

            # Store the recommendation in database
            reco = CanaryRecommendation(
                user_id=userid,
                movie_ids=labels,
                model=canary_version,
                model_num=2
            )
            createCanaryRecommendation(reco)

            return result
        else:
            app.logger.info("User not indexed. Returning defaults")

            # Store the recommendation in database
            reco = CanaryRecommendation(
                user_id=userid,
                movie_ids=getDefaults().split(','),
                model=canary_version,
                model_num=2

            )
            createCanaryRecommendation(reco)

            # Return response
            return getDefaults()


def getDefaults():
    # if user is not in dataframe they presumably don't have enough ratings. Instead suggest popular movies
    return "the+shawshank+redemption+1994,the+godfather+1972,the+usual+suspects+1995,schindlers+list+1993,raiders+of+the+lost+ark+1981,rear+window+1954,star+wars+1977,dr.+strangelove+or+how+i+learned+to+stop+worrying+and+love+the+bomb+1964,casablanca+1942,the+sixth+sense+1999,the+maltese+falcon+1941,one+flew+over+the+cuckoos+nest+1975,citizen+kane+1941,north+by+northwest+1959,the+godfather+part+ii+1974,the+silence+of+the+lambs+1991,chinatown+1974,saving+private+ryan+1998,monty+python+and+the+holy+grail+1975,life+is+beautiful+1997"


if __name__ == '__main__':
    # setup the tables in db
    recreate_database()
    # start the server
    app.run(host='0.0.0.0', port=8083)
