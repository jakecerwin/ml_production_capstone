import os
import pytest
import requests


def test_prediction_status_code():
    userid = 184186
    response = requests.get(f"http://localhost:8082/recommend/{userid}")
    assert response.ok


def test_prediction_new_user():
    userid = 1000000000
    response = requests.get(f"http://localhost:8082/recommend/{userid}")
    expected = ("the+shawshank+redemption+1994,the+godfather+1972,the+usual+suspects+1995,schindlers+list+1993,"
                "raiders+of+the+lost+ark+1981,rear+window+1954,star+wars+1977,"
                "dr.+strangelove+or+how+i+learned+to+stop+worrying+and+love+the+bomb+1964,"
                "casablanca+1942,the+sixth+sense+1999,the+maltese+falcon+1941,one+flew+over+the+cuckoos+nest+1975,"
                "citizen+kane+1941,north+by+northwest+1959,the+godfather+part+ii+1974,the+silence+of+the+lambs+1991,"
                "chinatown+1974,saving+private+ryan+1998,monty+python+and+the+holy+grail+1975,life+is+beautiful+1997")
    assert response.text == expected
