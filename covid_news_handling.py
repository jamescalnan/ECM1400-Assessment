from rich.console import Console
c = Console()
import api_keys, requests


def news_API_request(covid_terms: str="Covid COVID-19 coronavirus"):
    """Makes request to news API

    Args:
        covid_terms (str, optional): Takes in the articles as a. Defaults to 'Covid COVID-19 coronavirus'.

    Returns:
        list: Returns a list of dictionary items of articles
    """
    url = ('https://newsapi.org/v2/everything?'
       f'q={covid_terms}&'
       'from=2021-11-10&'
       'sortBy=popularity&'
       f'apiKey={api_keys.NEWS_API_KEY}')

    #Make API request
    response = requests.get(url)
    #Return list of dictionary items which are the articles
    return [story for story in response.json()["articles"]]


def get_current_article_titles(data: list=[]):
    """Creates a list of article titles

    Args:
        data (list, optional): Takes in the articles as a. Defaults to [].

    Returns:
        list: Returns a list of article titles
    """
    return [] if len(data) == 0 else [x['title'] for x in data]


def update_news(current_news:list = []):
    """Returns a list of articles that haven't been seen before

    Args:
        current_news (list, optional): The current articles. Defaults to [].

    Returns:
        list: Returns a list of the new articles
    """
    #Make news request
    news_request = news_API_request()
    #Get the titles for the current news articles in use
    current_news_titles = get_current_article_titles(current_news)
    #Return a list of new articles where the title hasnt been seen before
    return [article for article in news_request if article['title'] not in current_news_titles]
