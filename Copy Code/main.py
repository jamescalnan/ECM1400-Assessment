from flask import Flask, render_template,request
import datetime , threading
from covid_data_handler import *
from covid_news_handling import *
from schedHandler import schedHandler
global updates
nation="england"

update_covid_data()
update_news()

updates = []

newsHandler = schedHandler(newssched)
covidHandler = schedHandler(covidsched)

app = Flask(__name__)



@app.route("/index")
def index():
    newCases = 0
    for x in range(0,7):
        newCases += covid_data[x]["newCasesByPublishDate"]
        
    nation_data = covid_API_request("england","nation")
    nationCases = 0
    for x in range(0,7):
        nationCases += nation_data[x]["newCasesByPublishDate"]
    
    #print(request.args) http://127.0.0.1:5002/index?alarm=12%3A03&two=124&repeat=repeat&covid-data=covid-data&news=news
    if "notif" in request.args:
        remove_article(request.args["notif"])
    if "alarm" in request.args and "two" in request.args:
        content = ""
        currentTime = datetime.datetime.now()
        alarmTime = request.args["alarm"].split(":")
        wantedTime = currentTime.replace(hour=int(alarmTime[0]),minute=int(alarmTime[1]))
        
        if wantedTime < currentTime:
            wantedTime.replace(day=wantedTime.day+1)

        secondsUntilUpdate = (wantedTime - currentTime).total_seconds()
        title = request.args["two"]
        
        repeating = False
        if "repeat" in request.args:
            content = "repeating "
            repeating = True
        if "news" in request.args:
            newscontent = content + "update at " + request.args["alarm"] + " for news."
            newscontent = list(newscontent)
            newscontent[0] = newscontent[0].upper()
            newscontent = ''.join(newscontent)
            newsHandler.addEvent(update_news,secondsUntilUpdate,"News Data Update:"+request.args["two"],newscontent,repeat=repeating)
        if "covid-data" in request.args:
            datacontent = content + "update at " + request.args["alarm"] + " for covid data."
            datacontent = list(datacontent)
            datacontent[0] = datacontent[0].upper()
            datacontent = ''.join(datacontent)
            covidHandler.addEvent(update_news,secondsUntilUpdate,"Covid Data Update:"+request.args["two"],datacontent,repeat=repeating)

    if "alarm_item" in request.args:

        updates = covidHandler.getEvents()
        for item in updates:
            if item["title"] == request.args["alarm_item"]:
                queueEvents = item["events"]
                for e in queueEvents:
                    covidHandler.removeEvent(e)

        updates = newsHandler.getEvents()
        for item in updates:
            if item["title"] == request.args["alarm_item"]:
                queueEvents = item["events"]
                for e in queueEvents:
                    newsHandler.removeEvent(e)
                

        

    #last7DaysInfections = int(covid_data[2]["cumCasesByPublishDate"]) - int(covid_data[8]["cumCasesByPublishDate"])
    ## Var decomp
    ## updates
    ## title
    ## location
    ## local_7day_infections
    ## national_7day_infections
    ## nation_location
    ## hospital_cases
    ## deaths_total
    ## news_articles
    ## notification
    ## favicon
    ## image
    updates = []
    updates += covidHandler.getEvents()
    updates += newsHandler.getEvents()

    return render_template(
    "index.html",
    updates=updates,
    deaths_total=nation_data[1]["cumDeaths28DaysByDeathDate"],
    local_7day_infections=newCases,nation_location=nation_data[0]["areaName"],
    national_7day_infections=nationCases,title="Hello World!",
    location=covid_data[0]["areaName"],
    news_articles=news_articles,notification={'title':'Test'},
    image="covidimage.jpg",
    hospital_cases=get_hospital_cases())

if __name__ == "__main__":
    app.run(port=5002,debug=True)