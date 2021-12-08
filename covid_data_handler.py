import csv
import time
import sched
import json
from rich.console import Console
from uk_covid19 import Cov19API
import sv

c= Console()
scheduler = sched.scheduler(time.time,
                            time.sleep)

def infections(data: list):
    return data[0]#[0]

def hospital(data: list):
    return data[1]#[1]

def deaths(data: list):
    return data[2]#[2]

def parse_csv_data(csv_filename):
    """Parses CSV data

    Args:
        csv_filename (str): CSV file

    Returns:
        list: Returns the csv data in a list file
    """
    return [row for row in csv.reader(open(csv_filename, encoding="utf8"))]


def get_total_deaths(data, increment):
    """Gets the data for the total deaths

    Args:
        data (list): CSV data
        increment (int): used for recursion

    Returns:
        string: the total death number
    """
    c.print(data[increment][4])
    if data[increment][4] in ['', None]:
        return get_total_deaths(data, increment + 1)
    return data[increment][4]


def starting_index(data, col, increment):
    """Gets the starting index when to start looking at the data

    Args:
        data (list): CSV data
        x (int): Used for recursion

    Returns:
        int: Starting index
    """
    if increment + 2 > len(data):
        return None
    if data[increment + 1][col] != '':
        return increment + 1
    return starting_index(data, col, increment + 1)


def process_covid_csv_data(covid_csv_data):
    """Processes the Covid CSV data

    Args:
        covid_csv_data (list): CSV data

    Returns:
        int: The total last 7 days worth of cases
        int: The current hospital cases
        int: The current total deaths
    """
    start_idx = starting_index(covid_csv_data, 6, 1)
    last7days_cases = "{:,}".format(sum([int(covid_csv_data[x + 1][6])
                                         for x in range(start_idx, start_idx + 7)]))

    start_idx = starting_index(covid_csv_data, 5, 1)
    current_hospital_cases = ("{:,}".format(int(covid_csv_data[start_idx - 1][5]))
                              if start_idx is not None else "No Data")

    start_idx = starting_index(covid_csv_data, 4, 1)
    total_deaths = ("{:,}".format(int(covid_csv_data[start_idx][4]))
                    if start_idx is not None else "No Data")

    return last7days_cases, current_hospital_cases, total_deaths


def covid_API_request(location: str=json.loads(open("config.json", encoding="utf8").read())['location'],
                      location_type: str=json.loads(open("config.json", encoding="utf8").read())['location_type']):
    """Makes a request to the Cov19API

    Args:
        location (str, optional): The location parameter. Defaults to "Exeter".
        location_type (str, optional): The location type parameter. Defaults to "ltla".

    Returns:
        list: Returns a list of data in a format that can be used by the process_covid_csv_data
    """
    england_only = [
        f'areaType={location_type}',
        f'areaName={location}'
    ]

    struct = {"areaCode" : "areaCode",
        "areaName" : "areaName",
        "areaType" : "areaType",
        "date" : "date",
        "cumDailyNsoDeathsByDeathDate" : "cumDailyNsoDeathsByDeathDate",
        "hospitalCases" : "hospitalCases",
        "newCasesBySpecimenDate" : "newCasesBySpecimenDate"}

    api = Cov19API(filters=england_only, structure=struct)
    data = api.get_csv()
    return [row.split(",") for row in data.split("\n")][1:][:-1]


def get_covid_data(name):
    if (name, "covid") in sv.cancelled_threads:
        sv.cancelled_threads.remove((name, "covid"))
        return

    local_data = covid_API_request()
    national_data = covid_API_request(json.loads(open("config.json", encoding="utf8").read())['nation'], 'nation')
    
    local_data = process_covid_csv_data(local_data)
    national_data = process_covid_csv_data(national_data)


    sv.covid_data.append((infections(local_data),
                         infections(national_data),
                         hospital(national_data),
                         deaths(national_data)))

    c.print("[red]UPDATE DONE")
    c.print(f"NEW DATA: {sv.covid_data}")


def schedule_covid_updates(delay, prio, thread_name):
    scheduler.enter(delay, prio, get_covid_data, (thread_name, ))
    scheduler.run()
