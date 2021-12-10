from covid_news_handling import *


def test_news_API_request():
    data = news_API_request(increment=False)
    covid_news_data = news_API_request("Covid COVID-19 coronavirus", increment=False)
    assert data == covid_news_data


def test_news_API_response():
    assert news_API_request(test=True) == 200


def test_update_news():
    update_news()


def test_news_API_data():
    data = news_API_request()
    assert isinstance(data, list)
    assert len(data) > 0
