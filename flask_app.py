from os import name
from flask import Flask, render_template, request
import flask
import datetime
from flask.helpers import url_for
import threading
from covid_data_handler import *
from covid_news_handling import *
import sv

nation = "england"
location = "Exeter"

#[["Covid update", f"Repeat: {True}"]]
data = covid_API_request()


local_data = process_covid_csv_data(data)
national_data = process_covid_csv_data(covid_API_request(nation, "nation"))

sv.covid_data = [(local_data[0], national_data[0], national_data[1], national_data[2], "INIT")]

c.print(sv.covid_data)
input()

app = Flask(__name__)


def get_seconds_till_update(ut: str= None):
    current_time = datetime.datetime.now()
    update_time = ut.split(":")
    wanted_time = current_time.replace(hour=int(update_time[0]), minute=int(update_time[1]), second=0)

    if wanted_time < current_time:
        wanted_time.replace(day=wanted_time.day + 1)

    return (wanted_time - current_time).total_seconds()


def update_elapsed(updated_time):
    current_time = datetime.datetime.now()
    update_time = updated_time.split(":")
    wanted_time = current_time.replace(hour=int(update_time[0]), minute=int(update_time[1]), second=0)

    return wanted_time < current_time
        


@app.route("/index", methods=["POST","GET"])
def home():
    c.print("\n\n[red]START\n\n")

    if "notif" in request.args:
        sv.news_articles = remove_article(request.args["notif"], sv.news_articles)
        return flask.redirect(request.path)

    #?update=05%3A05&two=53&repeat=repeat&covid-data=covid-data&news=news

    if "update_item" in request.args:
        update_to_be_removed = (request.args['update_item'].split(': ')[-1])
        new_update_queue = []#[item for item in sv.update_queue if not item['name'] == update_to_be_removed]
        sv.cancelled_threads.append(update_to_be_removed)
        for item in sv.update_queue:
            if item['name'] == update_to_be_removed:
                continue
            new_update_queue.append(item)
        sv.update_queue = new_update_queue.copy()
        return flask.redirect(request.path)
        


    if "update" in request.args:
        
        time = request.args['update']
        update_name = request.args['two']
        repeat_update = 'repeat' in request.args
        covid_update = 'covid-data' in request.args
        news_update = 'news' in request.args
        
        time_till_update = get_seconds_till_update(time)
        
        
        
        if covid_update:
            sv.update_queue.append({'content' : f'{"Repeating" if repeat_update else ""} update at {time} for covid data',
                            'title' : f'Covid data update: {update_name}',
                            'data' : sv.covid_data,
                            'name' : update_name,
                            'time' : time,
                            'repeating' : repeat_update,
                            'type' : 'covid'})
            c.print(sv.update_queue)
            #return flask.redirect(request.path)
            #todo NEED TO MAKE THE UPDATE QUEUE REMOVE ITEMS ONCE THEYVE BEEN EXECUTED
            #NEED TO MAKE IT SO THAT REPEATING UPDATES WORK
            #NEED TO MAKE IT SO THAT NEWS UPDATES WORK
            #CURRENTLY THE UPDATES FOR THE COVID DATA WORK AND THE DATA IS UPDATED
            #THE SCHEDULED UPDAE DOESNT CONTINUE TO HAPPEN, IT IS A ONE TIME UPDATE OF THE VARIABLES
            threading.Thread(target=schedule_covid_updates, args=(time_till_update, 1, get_covid_data, sv.covid_data, update_name, time, nation, "nation"),name=update_name).start()
            return flask.redirect(request.path)


        #schedule_covid_updates(time_till_update, 1, get_covid_data, )
    #
    if len(sv.covid_data) > 0:
        #i only want to remove the init values if there is also another value in there
        c.print(f"inside of the if statement")
        c.print(sv.covid_data)
        covid_update_in_queue = [x for x in sv.update_queue if x['type'] == 'covid']
        c.print(covid_update_in_queue)
        input()
        if sv.covid_data[0][-1] == "INIT" and len(sv.covid_data) >= 2:
            sv.covid_data = sv.covid_data[1:]
            c.print("[red]HERE")
            c.print(sv.covid_data)
            input()
        elif not sv.covid_data[0][-1] == "INIT" and len(covid_update_in_queue) > 0: #if its not the init data and there is a covid update in the queue
            elapsed_updates = []
            
            for item in sv.update_queue:
                if update_elapsed(item['time']):
                    elapsed_updates.append(item['name'])
            c.print(elapsed_updates)
            input()
            new_update_queue = []
            for item in sv.update_queue:
                if item['name'] in elapsed_updates:
                    continue
                new_update_queue.append(item)
            sv.update_queue = new_update_queue.copy()
            c.print(sv.update_queue)
            input()
            return flask.redirect(request.path)
    # for item in covid_data:
        #check if time has elapsed

        
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

    c.print(f"here\n{sv.covid_data}")
    input()
    return render_template(
        "index.html",
        updates=sv.update_queue,
        deaths_total=sv.covid_data[-1][3],
        local_7day_infections=sv.covid_data[-1][0],nation_location=nation.title(),
        national_7day_infections=sv.covid_data[-1][1],title="COVID-19 Dashboard",
        location=location.title(),
        news_articles=sv.news_articles[:4],notification={'title':'Test'},
        image="covidimage.jpg",
        hospital_cases=sv.covid_data[-1][2]
    )


@app.route('/')
def redirect():
    return flask.redirect(url_for('home'))

app.run(debug=True)
