import api_keys, requests
from rich.console import Console
import sv, time, sched
c = Console()


scheduler = sched.scheduler(time.time,
                            time.sleep)


removed_articles = []

def news_API_request(covid_terms: str="Covid COVID-19 coronavirus"):
    """Makes request to news API

    Args:
        covid_terms (str, optional): Takes in the articles as a string
        Defaults to 'Covid COVID-19 coronavirus'.
        
    Returns:
        list: Returns a list of dictionary items of articles
    """
    sv.page += 1
    url = ('https://newsapi.org/v2/everything?'
       f'q={covid_terms}&'
       'sortBy=popularity&'
       f'page={sv.page}&'
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
    return [] if len(data) == 0 else [x['title'] for x in data[0]]


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
    if len(current_news) == 0:
        current_news_titles = []
    else:
        current_news_titles = get_current_article_titles(current_news)
    #Return a list of new articles where the title hasnt been seen before

    return [article for article in news_request if article['title'] not in current_news_titles and article['title'] not in removed_articles]

def remove_article(article_title:str, current_articles:list = []):
    if len(current_articles) == 0:
        return []
    
    removed_articles.append(article_title)
    return_list = [x for x in current_articles if x['title'] != article_title]
    
    return return_list

def get_updated_news_data(name):
    if (name, "covid") in sv.cancelled_threads:
        sv.cancelled_threads.remove((name, "covid"))
        return
    
    sv.news_articles += update_news()
    sv.news_articles = sv.news_articles[::-1]
    c.print("[red]NEWS UPDATE DONE")

def schedule_news_updates(delay, prio, thread_name=""):
    scheduler.enter(delay, prio, get_updated_news_data, (thread_name, ))
    scheduler.run()

sv.news_articles = update_news()
