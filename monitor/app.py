from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import requests
import os
from apscheduler.schedulers.background import BackgroundScheduler
import metrics
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}
db = SQLAlchemy(app)

feature_mapping = dict([('123', 1)])
split = 4
split_count = 0
canary_release = True
model_production = 1


@app.route('/recommend/<int:userid>')
def recommend(userid):
    global canary_release
    global split_count
    global split
    global feature_mapping
    global model_production

    model = 1
    if canary_release == True:
        if str(userid) in feature_mapping:
            model = feature_mapping[str(userid)]
        else:
            if split_count < split:
                feature_mapping[str(userid)] = 2
                model = 2
            else:
                feature_mapping[str(userid)] = 1
                model = 1
            split_count += 1
            split_count %= 10
    else:
        model = model_production

    url = "http://recommendation-service:8083/recommend/" + \
        str(userid) + "/" + str(model)

    try:
        return requests.get(url).content
    except requests.exceptions.RequestException as err:
        return "the+shawshank+redemption+1994,the+godfather+1972,the+usual+suspects+1995,schindlers+list+1993,raiders+of+the+lost+ark+1981,rear+window+1954,star+wars+1977,dr.+strangelove+or+how+i+learned+to+stop+worrying+and+love+the+bomb+1964,casablanca+1942,the+sixth+sense+1999,the+maltese+falcon+1941,one+flew+over+the+cuckoos+nest+1975,citizen+kane+1941,north+by+northwest+1959,the+godfather+part+ii+1974,the+silence+of+the+lambs+1991,chinatown+1974,saving+private+ryan+1998,monty+python+and+the+holy+grail+1975,life+is+beautiful+1997"
    except requests.exceptions.HTTPError as errh:
        return "the+shawshank+redemption+1994,the+godfather+1972,the+usual+suspects+1995,schindlers+list+1993,raiders+of+the+lost+ark+1981,rear+window+1954,star+wars+1977,dr.+strangelove+or+how+i+learned+to+stop+worrying+and+love+the+bomb+1964,casablanca+1942,the+sixth+sense+1999,the+maltese+falcon+1941,one+flew+over+the+cuckoos+nest+1975,citizen+kane+1941,north+by+northwest+1959,the+godfather+part+ii+1974,the+silence+of+the+lambs+1991,chinatown+1974,saving+private+ryan+1998,monty+python+and+the+holy+grail+1975,life+is+beautiful+1997"
    except requests.exceptions.ConnectionError as errc:
        return "the+shawshank+redemption+1994,the+godfather+1972,the+usual+suspects+1995,schindlers+list+1993,raiders+of+the+lost+ark+1981,rear+window+1954,star+wars+1977,dr.+strangelove+or+how+i+learned+to+stop+worrying+and+love+the+bomb+1964,casablanca+1942,the+sixth+sense+1999,the+maltese+falcon+1941,one+flew+over+the+cuckoos+nest+1975,citizen+kane+1941,north+by+northwest+1959,the+godfather+part+ii+1974,the+silence+of+the+lambs+1991,chinatown+1974,saving+private+ryan+1998,monty+python+and+the+holy+grail+1975,life+is+beautiful+1997"
    except requests.exceptions.Timeout as errt:
        return "the+shawshank+redemption+1994,the+godfather+1972,the+usual+suspects+1995,schindlers+list+1993,raiders+of+the+lost+ark+1981,rear+window+1954,star+wars+1977,dr.+strangelove+or+how+i+learned+to+stop+worrying+and+love+the+bomb+1964,casablanca+1942,the+sixth+sense+1999,the+maltese+falcon+1941,one+flew+over+the+cuckoos+nest+1975,citizen+kane+1941,north+by+northwest+1959,the+godfather+part+ii+1974,the+silence+of+the+lambs+1991,chinatown+1974,saving+private+ryan+1998,monty+python+and+the+holy+grail+1975,life+is+beautiful+1997"


@app.route('/canary/start')
def canary():
    global feature_mapping
    global model_production
    global canary_release
    feature_mapping = {}
    canary_release = True
    model_production = 1
    return 'OK'


@app.route('/rollout')
def rollout():
    global model_production
    global feature_mapping
    global canary_release
    model_production = 2
    feature_mapping = {}
    canary_release = False
    return 'OK'


@app.route('/abort')
def abort():
    global model_production
    global feature_mapping
    global canary_release
    model_production = 1
    feature_mapping = {}
    canary_release = False
    return 'OK'

# return the percentage of movies that were recommended and watched by the user


@app.route('/metrics/avg-recommended-rating/<int:model>')
def avgRecommendedRating(model):
    if model == 1:
        val = metrics.getCurrentModelMetric()
        if val is None:
            logging.warning("METRIC_AVG_RECOMMENDED_RATING_NONE")
            return "0"
        else:
            return str(val)
    elif model == 2:
        val = metrics.getCanaryModelMetric()
        if val is None:
            logging.warning("METRIC_AVG_RECOMMENDED_RATING_NONE")
            return "0"
        else:
            return str(val)
    return "0"


# trigger the calculation of ratings posted on recommended movies


@app.route('/metrics/calculate/<int:model>')
def metricCalculate(model):
    if model == 1:
        metrics.calculateCurrentModelMetric()
    elif model == 2:
        metrics.calculateCanaryModelMetric()
    return 'OK'


if __name__ == '__main__':
    # setup the scheduler to calculate online evaluation metrics at periodic intervals
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(metrics.calculateCurrentModelMetric, 'interval', minutes=60)
    sched.add_job(metrics.calculateCanaryModelMetric, 'interval', minutes=60)
    sched.start()
    # start the server
    app.run(host='0.0.0.0', port=8082)
    # shut down the background scheduler without waiting for any running jobs to finish
    sched.shutdown(wait=False)
