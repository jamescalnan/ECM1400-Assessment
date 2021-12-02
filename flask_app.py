from flask import Flask, render_template, request
import flask
import datetime
from flask.helpers import url_for
import threading
from covid_data_handler import *
from covid_news_handling import *
import shared_variables

nation = "england"
location = "Exeter"

update_queue = []#[["Covid update", f"Repeat: {True}"]]
data = covid_API_request()

covid_data = []

local_data = process_covid_csv_data(data)
national_data = process_covid_csv_data(covid_API_request(nation, "nation"))

covid_data = [(local_data[0], national_data[0], national_data[1], national_data[2])]

c.print(covid_data)
input()

app = Flask(__name__)


def get_seconds_till_update(ut: str= None):
    if update_news is None:
        return
    current_time = datetime.datetime.now()
    update_time = ut.split(":")
    wanted_time = current_time.replace(hour=int(update_time[0]), minute=int(update_time[1]), second=0)

    if wanted_time < current_time:
        wanted_time.replace(day=wanted_time.day + 1)

    return (wanted_time - current_time).total_seconds()


@app.route("/index", methods=["POST","GET"])
def home():
    c.print("\n\n[red]START\n\n")

    if "notif" in request.args:
        shared_variables.news_articles = remove_article(request.args["notif"], shared_variables.news_articles)
        return flask.redirect(request.path)

    #?update=05%3A05&two=53&repeat=repeat&covid-data=covid-data&news=news

    if "update" in request.args:
        time = request.args['update']
        update_name = request.args['two']
        repeat_update = 'repeat' in request.args
        covid_update = 'covid-data' in request.args
        news_update = 'news' in request.args
        
        time_till_update = get_seconds_till_update(time)
        if covid_update:
            update_queue.append({'content' : f'{"Repeating" if repeat_update else ""} update at {time} for covid data',
                            'title' : f'Covid data update: {update_name}',
                            'data' : covid_data})
            c.print(update_queue)
            threading.Thread(target=schedule_covid_updates, args=(time_till_update, 1, get_covid_data, covid_data, nation, "nation")).start()


        #schedule_covid_updates(time_till_update, 1, get_covid_data, )

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

    c.print(covid_data)
    input()
    return render_template(
        "index.html",
        updates=update_queue,
        deaths_total=covid_data[0][3],
        local_7day_infections=covid_data[0][0],nation_location=nation.title(),
        national_7day_infections=covid_data[0][1],title="COVID-19 Dashboard",
        location=location.title(),
        news_articles=shared_variables.news_articles[:4],notification={'title':'Test'},
        image="covidimage.jpg",
        hospital_cases=covid_data[0][2]
    )


@app.route('/')
def redirect():
    return flask.redirect(url_for('home'))

app.run(debug=True)
