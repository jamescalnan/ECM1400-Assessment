import flask
import datetime
import threading
import sv
from flask import Flask, render_template, request
from flask.helpers import url_for
from covid_data_handler import *
from covid_news_handling import *

NATION = "england"
location = "Exeter"

#[["Covid update", f"Repeat: {True}"]]
data = covid_API_request()


local_data = process_covid_csv_data(data)
national_data = process_covid_csv_data(covid_API_request(NATION, "nation"))

sv.covid_data = [(local_data[0], national_data[0], national_data[1], national_data[2], "INIT")]

app = Flask(__name__)

def format_time(in_time):
    return (f"{' ' if len(str(in_time.hour)) == 1 else ''}{in_time.hour}:{' ' if len(str(in_time.minute)) == 1 else ''}{in_time.minute}")

def get_seconds_till_update(ut: str):
    current_time = datetime.datetime.now()
    update_time = ut.split(":")
    wanted_time = current_time.replace(hour=int(update_time[0]), minute=int(update_time[1]), second=0)


    if wanted_time < current_time:
        wanted_time = wanted_time.replace(day=wanted_time.day + 1)

    return (wanted_time - current_time).total_seconds(), wanted_time# if not repeating else 86400 - (wanted_time - current_time).total_seconds()


def update_elapsed(updated_time):
    current_time = datetime.datetime.now()
    #update_time = updated_time.split(":")
    #wanted_time = current_time.replace(hour=int(update_time[0]), minute=int(update_time[1]), second=0)
    return updated_time < current_time
        


@app.route("/index", methods=["POST","GET"])
def home():
    c.print("\n\n[red]START\n\n")

    if "notif" in request.args:
        sv.news_articles = remove_article(request.args["notif"], sv.news_articles)
        return flask.redirect(request.path)

    #?update=05%3A05&two=53&repeat=repeat&covid-data=covid-data&news=news

    if "update_item" in request.args:
        update_to_be_removed = (request.args['update_item'].split(': ')[-1])
        update_type = request.args['update_item'].split(" ")[0].lower()
        
        sv.cancelled_threads.append((update_to_be_removed, update_type.lower()))
        sv.update_queue = [item for item in sv.update_queue if not (item['name'] == update_to_be_removed and item['type'] == update_type)]
        
        return flask.redirect(request.path)
        


    if "update" in request.args:

        time = request.args['update']
        update_name = request.args['two']
        repeat_update = 'repeat' in request.args
        covid_update = 'covid-data' in request.args
        news_update = 'news' in request.args
        
        seconds_till_update, update_time = get_seconds_till_update(time)
        
        if covid_update:
            sv.update_queue.append({'content' : f'{"Repeating" if repeat_update else ""} update at {time} for covid data',
                            'title' : f'Covid data update: {update_name}',
                            'data' : sv.covid_data,
                            'name' : update_name,
                            'time' : update_time,
                            'repeating' : repeat_update,
                            'type' : 'covid'})
            threading.Thread(target=schedule_covid_updates,
                             args=(seconds_till_update,
                                   1,
                                   update_name),
                             name=update_name).start()
            if not news_update:
                return flask.redirect(request.path)

        if news_update:
            sv.update_queue.append({'content' : f'{"Repeating" if repeat_update else ""} update at {time} for news data',
                            'title' : f'News data update: {update_name}',
                            'data' : sv.news_articles,
                            'name' : update_name,
                            'time' : update_time,
                            'repeating' : repeat_update,
                            'type' : 'news'})
            threading.Thread(target=schedule_news_updates,
                             args=(seconds_till_update,
                                   1,
                                   update_name),
                             name=update_name).start()
            return flask.redirect(request.path)


    #
    covid_update_in_queue = [x for x in sv.update_queue if x['type'] == 'covid']
    if len(covid_update_in_queue) > 0:
        elapsed_updates = []
        for i, item in enumerate(sv.update_queue):
            if update_elapsed(item['time']) and item['type'] == 'covid':
                elapsed_updates.append((i, item['name'], item['repeating']))
        for item in elapsed_updates:
            if item[2]:
                #the update is repeating
                #requeue the update
                data = sv.update_queue[item[0]]
                time_in_format = format_time(data['time'])
                time_in_format = get_seconds_till_update(time_in_format)

                threading.Thread(target=schedule_covid_updates,
                             args=(time_in_format[0],
                                   1,
                                   data['name']),
                             name=data['name']).start()
                
                sv.update_queue[item[0]]['time'] = time_in_format[1]
                elapsed_updates.remove(item)
                
        if len(elapsed_updates) > 0:

            new_update_queue = []
            for item in sv.update_queue:
                if item['name'] in [x[1] for x in elapsed_updates] and item['type'] == 'covid' and not item['repeating']:
                    continue
                new_update_queue.append(item)
            sv.update_queue = new_update_queue.copy()
            
            return flask.redirect(request.path)


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
        local_7day_infections=sv.covid_data[-1][0],nation_location=NATION.title(),
        national_7day_infections=sv.covid_data[-1][1],title="COVID-19 Dashboard",
        location=location.title(),
        news_articles=sv.news_articles[:4],
        notification={'title':'Test'},
        image="covidimage.jpg",
        hospital_cases=sv.covid_data[-1][2]
    )


@app.route('/')
def redirect():
    return flask.redirect(url_for('home'))

app.run(debug=True)
