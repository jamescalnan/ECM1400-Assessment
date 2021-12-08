from covid_data_handler import *
from covid_news_handling import *
from rich.console import Console

c = Console()


def test_parse_csv_data():
    data = parse_csv_data("nation_2021-10-28.csv")
    assert len(data) == 639, "Not equal"


def test_process_covid_csv_data():
    last7days_cases, current_hospital_cases, total_deaths = process_covid_csv_data(
        parse_csv_data("nation_2021-10-28.csv"))

    c.print(last7days_cases, current_hospital_cases, total_deaths)

    assert last7days_cases == 240299
    assert current_hospital_cases == 7019
    assert total_deaths == 141544


c.print(process_covid_csv_data(covid_API_request("exeter", "ltla")))
