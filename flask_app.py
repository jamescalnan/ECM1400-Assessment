import datetime
import threading

import flask
from flask import Flask, render_template, request
from flask.helpers import url_for

from covid_data_handler import *
from covid_news_handling import *

# Initialise data from the config file
NATION = json.loads(open("config.json", encoding="utf8").read())['nation']
LOCATION = json.loads(open("config.json", encoding="utf8").read())['location']

c = Console()

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Initialise the log file
logging.basicConfig(
    filename='out.log',
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')

# Initialise the local and and national data
local_data = process_covid_csv_data(covid_API_request())
national_data = process_covid_csv_data(covid_API_request(NATION, "nation"))
# Initialise the data in the sv.covid_data variable
sv.covid_data = [(local_data[0], national_data[0], national_data[1], national_data[2], "INIT")]


logging.info("Variables initialised successfully.")


app = Flask(__name__)


def format_time(in_time):
    """Formatting the time

    Args:
        in_time (datetime): Datetime input

    Returns:
        str: The formatted time in HH:MM format
    """
    return (f"{' ' if len(str(in_time.hour)) == 1 else ''}{in_time.hour}" +
            f":{' ' if len(str(in_time.minute)) == 1 else ''}{in_time.minute}")


def get_seconds_till_update(ut: str):
    """Calculates the seconds until the update time

    Args:
        ut (str): The time that the user entered

    Returns:
        (float, datetime): The seconds until the update, the datetime format of the wanted time
    """
    # Initialise the current time
    current_time = datetime.datetime.now()
    # Split the inputted time
    update_time = ut.split(":")
    # Initialise the inputted time into datetime format
    wanted_time = current_time.replace(hour=int(update_time[0]), minute=int(update_time[1]), second=0)

    # If the wanted_time is less than the current time then that means that the desired time 
    # is the next day
    if wanted_time < current_time:
        # Add one day to the wanted time
        wanted_time = wanted_time.replace(day=wanted_time.day + 1)

    # Return the variables
    return (wanted_time - current_time).total_seconds(), wanted_time


def update_elapsed(updated_time: datetime=datetime.datetime.now()):
    """Checks if the update has elapsed

    Args:
        updated_time (datetime, optional): The time that the update is going to happen at or has happened at. Defaults to datetime.datetime.now().

    Returns:
        bool: Checks whether the current time is less than the update time
    """
    return updated_time < datetime.datetime.now()


def enqueue_update(request_time: str = format_time(datetime.datetime.now()),
                   update_type: str = "News",
                   update_name: str = "EMPTY",
                   news_update: bool = True,
                   update_time: datetime = datetime.datetime.now(),
                   repeat_update: bool = False):
    """Adds an item to the update queue

    Args:
        request_time (str, optional): The time that the user entered. Defaults to format_time(datetime.datetime.now()).
        update_type (str, optional): The type of update, either Covid or News. Defaults to "News".
        update_name (str, optional): The name of the update. Defaults to "EMPTY".
        news_update (bool, optional): Boolean if it is a news update. Defaults to True.
        update_time (datetime, optional): The time that the update is supposed to happen. Defaults to datetime.datetime.now().
        repeat_update (bool, optional): Whether it is a repeat update. Defaults to False.
    """
    # Add the values to the sv.update_queue variable
    sv.update_queue.append(
        {'content': f'{"Repeating update" if repeat_update else "Update"} at {request_time} for {update_type} data',
         'title': f'{update_type} data update: {update_name}',
         'data': sv.news_articles if news_update else sv.covid_data,
         'name': update_name,
         'time': update_time,
         'repeating': repeat_update,
         'type': update_type.lower()})
    logging.info("Update added to update queue.")


def start_thread(target=schedule_covid_updates,
                 seconds_till_update: float = 5,
                 update_name: str = "update",
                 thread_type: str = ''):
    """Starts the thread for the scheduler

    Args:
        target (function, optional): The function for the scheduler. Defaults to schedule_covid_updates.
        seconds_till_update (float, optional): The time (seconds) till the update. Defaults to 5.
        update_name (str, optional): The name of the update. Defaults to "update".
        thread_type (str, optional): The type of thread. Defaults to ''.
    """
    # Start the thread
    threading.Thread(target=target,
                     args=(seconds_till_update,
                           update_name),
                     name=update_name + thread_type).start()
    logging.info("Thread started.")


@app.route("/index", methods=["POST", "GET"])
def home():
    """The home route

    """
    
    # If the user has tried to remove an item from the news list
    if "notif" in request.args:
        # Call the remove_article function 
        sv.news_articles = remove_article(request.args["notif"], sv.news_articles)
        # Update the page
        return flask.redirect(request.path)

    # If the user has tried to remove an update from the update list
    if "update_item" in request.args:
        # Get the name of the update
        update_to_be_removed = (request.args['update_item'].split(': ')[-1])
        # Get the type of the update
        update_type = request.args['update_item'].split(" ")[0].lower()

        # Add the name and type to the cancelled threads list
        sv.cancelled_threads.append((update_to_be_removed, update_type.lower()))
        #Update the update queue to remove the item
        sv.update_queue = [item for item in sv.update_queue if
                           not (item['name'] == update_to_be_removed and item['type'] == update_type)]
        logging.info("Update queue updated.")
        # Update the page
        return flask.redirect(request.path)

    # If the user has tried to add an update
    if "update" in request.args:
        logging.info("Attemping to add update(s) to update queue.")
        # Initialise the data from the user update
        request_time = request.args['update']
        update_name = request.args['two']
        repeat_update = 'repeat' in request.args
        covid_update = 'covid-data' in request.args
        news_update = 'news' in request.args

        # Calculate the seconds until the update and the datetime format
        seconds_till_update, update_time = get_seconds_till_update(request_time)
        logging.info("Time till update calculated.")

        # Check if its a covid update
        if covid_update:
            logging.info("Attemping to add to update queue.")
            # Enqueue the update
            enqueue_update(request_time, "COVID-19", update_name, covid_update, update_time, repeat_update)
            logging.info("Attemping to start thread")
            # Start the thread
            start_thread(schedule_covid_updates, seconds_till_update, update_name)

        #Check if its a news update
        if news_update:
            logging.info("Attemping to add to update queue.")
            # Enqueue the update
            enqueue_update(request_time, "News", update_name, news_update, update_time, repeat_update)
            logging.info("Attemping to start thread.")
            # Start the thread
            start_thread(schedule_news_updates, seconds_till_update, update_name)
        
        # Redirect the page
        return flask.redirect(request.path)

    # Check if there are items present in the update queue
    if len(sv.update_queue) > 0:
        logging.info("Attempting to find elapsed updates.")
        # Initialise a tuple (int, bool, str) from the update queue which includes update data
        # from updates that have already elapsed
        elapsed_updates = [(i, item['name'],
                            item['repeating'],
                            item['type']) for i, item in enumerate(sv.update_queue) if update_elapsed(item['time'])]

        # Look through the elapsed updates
        for item in elapsed_updates:
            # Check if its a repeating update
            if item[2]:
                logging.info("Repeating update found.")
                # Save the update data in a temperary update
                data = sv.update_queue[item[0]]
                # Calculate the time until the update
                time_in_format = get_seconds_till_update(format_time(data['time']))
                # Store the update type
                update_type = data['type']
                logging.info("Attemping to start thread.")
                # Start the thread
                start_thread(schedule_news_updates if update_type == "news" else schedule_covid_updates,
                             time_in_format[0],
                             data['name'],
                             update_type)

                # Update the time in the update queue to the new time
                sv.update_queue[item[0]]['time'] = time_in_format[1]
                logging.info("Update queue updated.")
                # Remove the elapsed update from the list
                elapsed_updates.remove(item)

        # Check if there are still updates in the elapsed updates list
        if len(elapsed_updates) > 0:
            # If there is then that means that these are elapsed updates that aren't repeating
            update_names = [x[1] for x in elapsed_updates]
            # Update the queue so that only unelapsed and repeating items remain
            sv.update_queue = [item for item in sv.update_queue
                               if item['name'] not in update_names
                               and item['repeating']]

            logging.info("Update queue updated.")
        else:
            logging.info("No updates elapsed.")

    logging.info("Rendering flask template.")
    # Render the flask template
    return render_template(
        "index.html",
        updates=sv.update_queue,
        deaths_total=sv.covid_data[-1][3],
        local_7day_infections=sv.covid_data[-1][0], nation_location=NATION.title(),
        national_7day_infections=sv.covid_data[-1][1], title="COVID-19 Dashboard",
        location=LOCATION.title(),
        news_articles=sv.news_articles[:4],
        notification={'title': 'Test'},
        image="covid19.png",
        hospital_cases=sv.covid_data[-1][2]
    )


@app.route('/')
def redirect():
    return flask.redirect(url_for('home'))


app.run(debug=True)
