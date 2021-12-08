from covid_data_handler import *

def test_parse_csv_data():
    data = parse_csv_data("nation_2021-10-28.csv")
    assert len(data) == 639, "Not equal"


def test_process_covid_csv_data():
    last7days_cases, current_hospital_cases, total_deaths = process_covid_csv_data(
        parse_csv_data("nation_2021-10-28.csv"))

    assert last7days_cases == 240299
    assert current_hospital_cases == 7019
    assert total_deaths == 141544

def test_covid_API_request():
    data = covid_API_request()
    assert isinstance(data, list)
    assert len(data) > 0
    assert len(data[0]) == 7

def test_schedule_covid_updates():
    schedule_covid_updates(update_interval=10, update_name='update test')
