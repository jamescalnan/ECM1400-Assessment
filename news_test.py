from covid_news_handling import *


def test_news_API_request():
    data = news_API_request(increment=False)
    covid_news_data = news_API_request("Covid COVID-19 coronavirus", increment=False)
    assert data