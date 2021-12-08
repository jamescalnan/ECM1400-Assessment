import datetime
import threading
import logging

import flask
from flask import Flask, render_template, request
from flask.helpers import url_for
from rich.console import Console

from covid_data_handler import *
from covid_news_handling import *

NATION = "england"
location = "Exeter"

c = Console()


logging.basicConfig(
    filename='output1.log',
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')


data = covid_API_request()

local_data = process_covid_csv_data(data)
national_data = process_covid_csv_data(covid_API_request(NATION, "nation"))

sv.covid_data = [(local_data[0], national_data[0], national_data[1], national_data[2], "INIT")]

logging.info("Variables initialised successfully.")

app = Flask(__name__)


def format_time(in_time):
    return (f"{' ' if len(str(in_time.hour)) == 1 else ''}{in_time.hour}" +
            f":{' ' if len(str(in_time.minute)) == 1 else ''}{in_time.minute}")


def get_seconds_till_update(ut: str):
    current_time = datetime.datetime.now()
    update_time = ut.split(":")
    wanted_time = current_time.replace(hour=int(update_time[0]), minute=int(update_time[1]), second=0)

    if wanted_time < current_time:
        wanted_time = wanted_time.replace(day=wanted_time.day + 1)

    return (wanted_time - current_time).total_seconds(), wanted_time


def update_elapsed(updated_time):
    current_time = datetime.datetime.now()
    return updated_time < current_time


def enqueue_update(request_time: str = format_time(datetime.datetime.now()),
                   update_type: str = "News",
                   update_name: str = "EMPTY",
                   news_update: bool = True,
                   update_time: datetime = datetime.datetime.now(),
                   repeat_update: bool = False):
    sv.update_queue.append(
        {'content': f'{"Repeating update" if repeat_update else "Update"} at {request_time} for {update_type} data',
         'title': f'{update_type} data update: {update_name}',
         'data': sv.news_articles if news_update else sv.covid_data,
         'name': update_name,
         'time': update_time,
         'repeating': repeat_update,
         'type': update_type.lower()})
    logging.info("Update added to update queue.")


def start_thread(target=schedule_covid_updates, seconds_till_update: float = 5, update_name: str = "update",
                 thread_type: str = ''):
    threading.Thread(target=target,
                     args=(seconds_till_update,
                           1,
                           update_name),
                     name=update_name + thread_type).start()
    logging.info("Thread started.")


@app.route("/index", methods=["POST", "GET"])
def home():
    if "notif" in request.args:
        sv.news_articles = remove_article(request.args["notif"], sv.news_articles)
        return flask.redirect(request.path)

    # ?update=05%3A05&two=53&repeat=repeat&covid-data=covid-data&news=news

    if "update_item" in request.args:
        update_to_be_removed = (request.args['update_item'].split(': ')[-1])
        update_type = request.args['update_item'].split(" ")[0].lower()

        sv.cancelled_threads.append((update_to_be_removed, update_type.lower()))
        sv.update_queue = [item for item in sv.update_queue if
                           not (item['name'] == update_to_be_removed and item['type'] == update_type)]
        logging.info("Update queue updated.")
        return flask.redirect(request.path)

    if "update" in request.args:
        logging.info("Attemping to add update(s) to update queue.")
        request_time = request.args['update']
        update_name = request.args['two']
        repeat_update = 'repeat' in request.args
        covid_update = 'covid-data' in request.args
        news_update = 'news' in request.args

        seconds_till_update, update_time = get_seconds_till_update(request_time)
        logging.info("Time till update calculated.")

        if covid_update:
            logging.info("Attemping to add to update queue.")
            enqueue_update(request_time, "COVID-19", update_name, covid_update, update_time, repeat_update)
            logging.info("Attemping to start thread")
            start_thread(schedule_covid_updates, seconds_till_update, update_name)
            if not news_update:
                return flask.redirect(request.path)

        if news_update:
            logging.info("Attemping to add to update queue.")
            enqueue_update(request_time, "News", update_name, news_update, update_time, repeat_update)
            logging.info("Attemping to start thread.")
            start_thread(schedule_news_updates, seconds_till_update, update_name)
            return flask.redirect(request.path)

    if len(sv.update_queue) > 0:
        logging.info("Attempting to find elapsed updates.")
        elapsed_updates = [(i, item['name'],
                            item['repeating'],
                            item['type']) for i, item in enumerate(sv.update_queue) if update_elapsed(item['time'])]

        for item in elapsed_updates:
            if item[2]:
                logging.info("Repeating update found.")
                data = sv.update_queue[item[0]]
                time_in_format = get_seconds_till_update(format_time(data['time']))
                update_type = data['type']
                logging.info("Attemping to start thread.")
                start_thread(schedule_news_updates if update_type == "news" else schedule_covid_updates,
                             time_in_format[0],
                             data['name'],
                             update_type)

                sv.update_queue[item[0]]['time'] = time_in_format[1]
                logging.info("Update queue updated.")
                elapsed_updates.remove(item)
                return flask.redirect(request.path)

        if len(elapsed_updates) > 0:
            new_update_queue = []
            for item in sv.update_queue:
                if item['name'] in [x[1] for x in elapsed_updates] and not item['repeating']:
                    continue
                new_update_queue.append(item)
            sv.update_queue = new_update_queue.copy()
            logging.info("Update queue updated.")
            return flask.redirect(request.path)
        else:
            logging.info("No updates elapsed.")

    logging.info("Rendering flask template.")
    return render_template(
        "index.html",
        updates=sv.update_queue,
        deaths_total=sv.covid_data[-1][3],
        local_7day_infections=sv.covid_data[-1][0], nation_location=NATION.title(),
        national_7day_infections=sv.covid_data[-1][1], title="COVID-19 Dashboard",
        location=location.title(),
        news_articles=sv.news_articles[:4],
        notification={'title': 'Test'},
        image="covidimage.jpg",
        hospital_cases=sv.covid_data[-1][2]
    )


@app.route('/')
def redirect():
    return flask.redirect(url_for('home'))


app.run(debug=True)
