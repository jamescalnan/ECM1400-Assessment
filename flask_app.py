from flask import Flask, render_template, request
from covid_data_handler import *
from covid_news_handling import *


app = Flask(__name__)

@app.route("/index")
def home():
    data = covid_API_request()
    seven_day, hospital_cases, total_deaths = process_covid_csv_data(data)
    
    news_articles = []
    news_articles = update_news(news_articles)
    
    if "notif" in request.args:
        news_articles = update_news([news_articles])
        c.print(request.args)

    return render_template(
    "index.html",
    updates="HELLO",
    deaths_total=total_deaths,
    local_7day_infections=seven_day,nation_location="Exeter",
    national_7day_infections="XXX",title="Hello World!",
    location="EXETER 2",
    news_articles=news_articles,notification={'title':'Test'},
    image="covidimage.jpg",
    hospital_cases=hospital_cases)
    

app.run(debug=True)
