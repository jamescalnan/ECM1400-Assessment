from flask import Flask, render_template, request
from covid_data_handler import *
from covid_news_handling import *

nation = "england"

app = Flask(__name__)

@app.route("/index")
def home():
    data = covid_API_request()
    local_seven_day, local_hospital_cases, local_total_deaths = process_covid_csv_data(data)
    
    national_seven_day, national_hospital_cases, national_total_deaths = process_covid_csv_data(covid_API_request(nation, "nation"))
    
    c.print(local_hospital_cases, local_total_deaths)
    
    news_articles = []
    news_articles = update_news(news_articles)
    
    if "notif" in request.args:
        news_articles = update_news([news_articles])
        c.print(request.args)

    return render_template(
    "index.html",
    updates="",
    deaths_total=local_total_deaths,
    local_7day_infections=local_seven_day,nation_location=nation.title(),
    national_7day_infections=national_seven_day,title="COVID-19 Dashboard",
    location="EXETER",
    news_articles=news_articles,notification={'title':'Test'},
    image="covidimage.jpg",
    hospital_cases=local_hospital_cases)
    

app.run(debug=True)
