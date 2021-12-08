from rich.console import Console

import api_keys
import requests
import sched
import sv
import time
import logging
import json

c = Console()

scheduler = sched.scheduler(time.time,
                            time.sleep)

removed_articles = []


def news_API_request(covid_terms: str = json.loads(open("config.json", encoding="utf8").read())['news_terms'], increment:bool = True):
    """Makes request to news API

    Args:
        covid_terms (str, optional): Takes in the articles as a string
        Defaults to 'Covid COVID-19 coronavirus'.
        
    Returns:
        list: Returns a list of dictionary items of articles
    """
    sv.page += 1 if increment else 0
    url = ('https://newsapi.org/v2/everything?'
           f'q={covid_terms}&'
           'sortBy=popularity&'
           f'page={sv.page}&'
           f'apiKey={api_keys.NEWS_API_KEY}')

    # Make API request
    logging.info("Attemping to make News API call.")
    response = requests.get(url)
    # Return list of dictionary items which are the articles
    logging.info("Successful News API call.")
    return [story for story in response.json()["articles"]]


def get_current_article_titles(data: list = []):
    """Creates a list of article titles

    Args:
        data (list, optional): Takes in the articles as a. Defaults to [].

    Returns:
        list: Returns a list of article titles
    """
    return [] if len(data) == 0 else [x['title'] for x in data[0]]


def update_news(current_news: list = []):
    """Returns a list of articles that haven't been seen before

    Args:
        current_news (list, optional): The current articles. Defaults to [].

    Returns:
        list: Returns a list of the new articles
    """
    # Make news request
    logging.info("Updating news list.")
    news_request = news_API_request()

    # Get the titles for the current news articles in use
    if len(current_news) == 0:
        current_news_titles = []
    else:
        current_news_titles = get_current_article_titles(current_news)
    # Return a list of new articles where the title hasnt been seen before

    return [article for article in news_request if
            article['title'] not in current_news_titles and article['title'] not in removed_articles]


def remove_article(article_title: str, current_articles: list = []):
    if len(current_articles) == 0:
        return []

    removed_articles.append(article_title)
    return_list = [x for x in current_articles if x['title'] != article_title]
    logging.info("Removed article(s).")
    return return_list


def get_updated_news_data(name):
    if (name, "covid") in sv.cancelled_threads:
        sv.cancelled_threads.remove((name, "covid"))
        logging.info("Cancelled thread executed.")
        return

    sv.news_articles += update_news()
    sv.news_articles = sv.news_articles[::-1]
    logging.info("COVID-19 data updated.")


def schedule_news_updates(update_interval, update_name):
    scheduler.enter(update_interval, 1, get_updated_news_data, (update_name,))
    scheduler.run()

logging.info("News articles initialised.")
sv.news_articles = update_news()
