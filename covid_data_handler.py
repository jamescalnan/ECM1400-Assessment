import csv
import json
import logging
import sched
import time

from uk_covid19 import Cov19API

import sv

# Initialise the scheduler
scheduler = sched.scheduler(time.time,
                            time.sleep)


def parse_csv_data(csv_filename):
    logging.info("Parsing CSV data.")
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
    # If the value at [increment][4] is either '' or None then continue to go down the list recursively
    if data[increment][4] in ['', None]:
        return get_total_deaths(data, increment + 1)
    # If the value isn't '' or None then return the value
    return data[increment][4]


def starting_index(data:list, col:int, increment:int):
    """Getting the first index where data appears in the COVID-19 daya

    Args:
        data (list): The covid CSV data
        col (int): The index of the desired column
        increment (int): The increment

    Returns:
        int: The first idnex where data valid appears
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
    logging.info("Attemping to process CSV data.")
    # Get the starting index where data appears
    start_idx = starting_index(covid_csv_data, 6, 1)
    #Get the sum of the cases in the last 7 days
    last7days_cases = sum([int(covid_csv_data[x + 1][6])
                           for x in range(start_idx, start_idx + 7) if covid_csv_data[x + 1][6].isnumeric()])

    # Get the starting index where data appears
    start_idx = starting_index(covid_csv_data, 5, 1)
    # Get the current amount of hospital cases
    # if there is no data then it is set to 'No data'
    current_hospital_cases = ((int(covid_csv_data[start_idx - 1][5]))
                              if start_idx is not None else "No Data")

    # Get the starting index where data appears
    start_idx = starting_index(covid_csv_data, 4, 1)
    # Get the current amount of deaths
    total_deaths = ((int(covid_csv_data[start_idx][4]))
                    if start_idx is not None else "No Data")
    logging.info("CSV data parsed")
    return last7days_cases, current_hospital_cases, total_deaths


def covid_API_request(location: str = json.loads(open("config.json", encoding="utf8").read())['location'],
                      location_type: str = json.loads(open("config.json", encoding="utf8").read())['location_type']):
    """Makes a request to the Cov19API

    Args:
        location (str, optional): The location parameter. Defaults to "Exeter".
        location_type (str, optional): The location type parameter. Defaults to "ltla".

    Returns:
        list: Returns a list of data in a format that can be used by the process_covid_csv_data
    """
    # Initialise the filters
    filters = [
        f'areaType={location_type}',
        f'areaName={location}'
    ]

    # Initialise the structure
    struct = {"areaCode": "areaCode",
              "areaName": "areaName",
              "areaType": "areaType",
              "date": "date",
              "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
              "hospitalCases": "hospitalCases",
              "newCasesBySpecimenDate": "newCasesBySpecimenDate"}
    
    logging.info("Attemping COVID-19 API call.")
    # Make the API call
    api = Cov19API(filters=filters, structure=struct)
    # Return the data as CSV
    data = api.get_csv()
    logging.info("Successful COVID-19 API call.")
    # Split the data into a format that can be used
    return [row.split(",") for row in data.split("\n")][1:][:-1]


def get_covid_data(name):
    """Updates the sv.covid_data variable with new data

    Args:
        name (str): The name of the update
    """
    # If the name is  in the cancelled threads list then don't do the update
    if (name, "covid") in sv.cancelled_threads:
        # Remove the name from the cancelled threads list
        sv.cancelled_threads.remove((name, "covid"))
        logging.info("Cancelled thread executed.")
        return

    #Get the data for the local area that is defined inside of the config file
    local_data = covid_API_request()
    # Get the national data
    national_data = covid_API_request(json.loads(open("config.json", encoding="utf8").read())['nation'], 'nation')

    #Parse the local data
    local_data = process_covid_csv_data(local_data)
    #Parse the national data
    national_data = process_covid_csv_data(national_data)

    # Add the data to the list
    sv.covid_data.append((local_data[0],
                          national_data[0],
                          national_data[1],
                          national_data[2]))

    logging.info("COVID-19 data updated.")


def schedule_covid_updates(update_interval:float, update_name:str = "", test=False):
    """Schedule updates for covid

    Args:
        update_interval (float): The amount of the seconds until the update
        update_name (str): The name of the update
    """
    if test:
        return True
    # Add the update to the scheduler
    scheduler.enter(update_interval, 1, get_covid_data, (update_name,))
    # Run the scheduler
    scheduler.run()
