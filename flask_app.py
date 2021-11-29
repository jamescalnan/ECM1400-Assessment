from flask import Flask, render_template, request, redirect
import flask
from flask.helpers import url_for
from covid_data_handler import *
from covid_news_handling import *

nation = "england"
location = "Exeter"
app = Flask(__name__)


@app.route("/index", methods=["POST","GET"])
def home():
    c.print("\n\n[red]START\n\n")
    data = covid_API_request()
    local_seven_day, local_hospital_cases, local_total_deaths = process_covid_csv_data(data)
    
    national_seven_day, national_hospital_cases, national_total_deaths = process_covid_csv_data(covid_API_request(nation, "nation"))
    
    news_articles = update_news()
    
    if "notif" in request.args:
        news_articles = remove_article(request.args["notif"], news_articles)
        return flask.redirect(request.path)

    #?update=05%3A05&two=53&repeat=repeat&covid-data=covid-data&news=news
    
    if "update" in request.args:
        c.print(request.args)
        c.print(f"time: {request.args['update']}")
        c.print(f"label: {request.args['two']}")
        c.print(f"repeat: {'repeat' in request.args}")
        c.print(f"update covid: {'covid-data' in request.args}")
        c.print(f"update news: {'news' in request.args}")
        
        input()
    
    """
    time: 19:36
    label: update_label
    repeat: true
    up cov: true
    up news: true
    
    ?update=19%3A36&two=update_label&repeat=repeat&covid-data=covid-data&news=news
    """
    
    """
    ?update=19%3A34&two=label&covid-data=covid-data
    """

    return render_template(
    "index.html",
    updates="",
    deaths_total=national_total_deaths,
    local_7day_infections=local_seven_day,nation_location=nation.title(),
    national_7day_infections=national_seven_day,title="COVID-19 Dashboard",
    location=location.title(),
    news_articles=news_articles[:4],notification={'title':'Test'},
    image="covidimage.jpg",
    hospital_cases=national_hospital_cases)
    
@app.route('/')
def redirect():
    return redirect(url_for('/index'))

app.run(debug=True)
