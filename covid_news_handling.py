import json
import logging
import sched
import time

import requests

import api_keys
import sv

# Initialise the scheduler
scheduler = sched.scheduler(time.time,
                            time.sleep)

removed_articles = []


def news_API_request(covid_terms: str = json.loads(open("config.json", encoding="utf8").read())['news_terms'],
                     increment: bool = True, test:bool=False):
    """Makes request to news API

    Args:
        covid_terms (str, optional): Takes in the articles as a string
        Defaults to 'Covid COVID-19 coronavirus'.
        
    Returns:
        list: Returns a list of dictionary items of articles
    """
    # Add one to the sv.page variable so that when an API call is made
    # different results are returned
    url = ('https://newsapi.org/v2/everything?'
           f'q={covid_terms}&'
           'sortBy=popularity&'
           f'page={sv.page}&'
           f'apiKey={api_keys.NEWS_API_KEY}')
    sv.page += 1 if increment else 0

    # Make API request
    logging.info("Attemping to make News API call.")
    response = requests.get(url)
    if test:
        return response.status_code
    # Return list of dictionary items which are the articles
    logging.info("Successful News API call.")
    # Return a list of the articles
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
    """Returns a list without the articles that are passed through the current articles variable

    Args:
        article_title (str): The article to be removed
        current_articles (list, optional): The current news articles. Defaults to [].

    Returns:
        list: The current articles without the removed one
    """
    if len(current_articles) == 0:
        # If there are no articles in the list then just return an empty list
        return []

    removed_articles.append(article_title)
    # Add the articles to be removed to the removed article list
    # This will ensure that the article stays removed when new things are loaded into the list
    logging.info("Removed article(s).")
    return [x for x in current_articles if x['title'] != article_title]


def get_updated_news_data(name):
    """Updates the sv.news_articles variable

    Args:
        name (str): The name of the update
    """
    # If the name is  in the cancelled threads list then don't do the update
    if (name, "news") in sv.cancelled_threads:
        # Remove the name from the cancelled threads list
        sv.cancelled_threads.remove((name, "news"))
        logging.info("Cancelled thread executed.")
        return

    # Update the sv.news_articles variable using the update_news() function
    sv.news_articles += update_news()
    # Reverse the news articles so that new articles are showed when the page is updated
    sv.news_articles = sv.news_articles[::-1]
    logging.info("COVID-19 data updated.")
    return


def schedule_news_updates(update_interval, update_name):
    """Schedules news updates

    Args:
        update_interval (float): The seconds until the update
        update_name (str): The name of the update
    """
    # Add the update to the scheduler
    scheduler.enter(update_interval, 1, get_updated_news_data, (update_name,))
    # Run the scheduler
    scheduler.run()

# Initialise the news articles
logging.info("News articles initialised.")
sv.news_articles = update_news()
