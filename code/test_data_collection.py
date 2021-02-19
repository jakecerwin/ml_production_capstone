from get_kafka_data import parse_message
from io import StringIO

import pytest


class MockMessage:
    def __init__(self, value):
        self.value = value


@pytest.fixture(scope='function')
def buffer():
    return StringIO()


def test_simple_rating(buffer):
    message = MockMessage("2020-04-07T09:43:58,341128,GET /rate/the+godfather+1972=5")
    expected = "2020-04-07T09:43:58,341128,the+godfather+1972,5"
    parse_message(message, buffer)
    assert buffer.getvalue().strip() == expected


def test_skip_view(buffer):
    message = MockMessage("2020-04-07T09:26,617950,GET /data/m/the+karate+kid+1984/0.mpg")
    expected = ""
    parse_message(message, buffer)
    assert buffer.getvalue().strip() == expected


def test_malformed_no_year(buffer):
    message = MockMessage("2020-04-07T09:43:58,341128,GET /rate/the+godfather=5")
    expected = ""
    parse_message(message, buffer)
    assert buffer.getvalue().strip() == expected


def test_malformed_no_user(buffer):
    message = MockMessage("2020-04-07T09:43:58,GET /rate/the+godfather+1972=5")
    expected = ""
    parse_message(message, buffer)
    assert buffer.getvalue().strip() == expected


def test_malformed_request_uri(buffer):
    message = MockMessage("2020-04-07T09:43:58,341128,GET /rating/the+godfather+1972=5")
    expected = ""
    parse_message(message, buffer)
    assert buffer.getvalue().strip() == expected
