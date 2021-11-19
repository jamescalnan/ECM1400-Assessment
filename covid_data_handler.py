import csv, schedule
from rich.console import Console
from uk_covid19 import Cov19API

c= Console()

def parse_csv_data(csv_filename):
    """Parses CSV data

    Args:
        csv_filename (str): CSV file

    Returns:
        list: Returns the csv data in a list file
    """
    return [row for row in csv.reader(open(csv_filename))]

def get_total_deaths(data, x):
    c.print(data[x][4])
    if data[x][4] in ['', None]:
        return get_total_deaths(data, x + 1)
    return data[x][4]

def starting_index(data, col, x):
    """Gets the starting index when to start looking at the data

    Args:
        data (list): CSV data
        x (int): Used for recursion

    Returns:
        int: Starting index
    """
    if x + 2 > len(data) : return None
    if data[x + 1][col] != '' : return x + 1
    return starting_index(data, col, x + 1)

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
    last7days_cases = sum([int(covid_csv_data[x + 1][6]) for x in range(start_idx, start_idx + 7)])

    start_idx = starting_index(covid_csv_data, 5, 1)
    current_hospital_cases = int(covid_csv_data[start_idx - 1][5]) if start_idx != None else None
    
    start_idx = starting_index(covid_csv_data, 4, 1)
    total_deaths = int(covid_csv_data[start_idx][4]) if start_idx != None else None

    return last7days_cases, current_hospital_cases, total_deaths


def covid_API_request(location: str="Exeter", location_type: str="ltla"):
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


def schedule_covid_updates(update_interval, update_name):
    """Schedules updates

    Args:
        update_interval (int): The update interval
        update_name (str): The name of the update to do
    """
    schedule.every(update_interval).do(update_name)
