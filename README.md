# ECM1400 Assessment

---

#### COVID-19 Dashboard project for module ECM1400

 The goal of the project was to allow the user to retrieve up-to-date COVID-19 data and news stories.
 The User should also be able to schedule updates for the COVID-19 data and the news stories.
 
 The program was implemented using numerous modules, including:
 - flask: This was used to render and run the html template that was provided
 - sched: The sched module was used in conjunction with the threading module in order to 
 allow for the program to schedule data updates
 - threading: The threading module was used so that the program wouldn't hang when executing
 scheduled update
 - pytest: The pytest module was used to test the programs functions to ensure that everything
 works correctly
 - uk_covid19: This was used to retrieve data from PHE
 - requests: This was used to make API requests
 - json: This was used to load API responses into a readable format
 - logging: This module was used to log events when the program is running
 - rich: This was used when making the program to print variables and other
 things to the console in a nice readable format

---

 ##Running the program

 ####Python Version
 This program is intended to be run on Python 3.9 64 bit

 ####Required Modules
 The required modules for this program can be installed using pip.
 Running `pip -r requirements.txt` inside the project folder will install
 the required modules.

 ####Personalising the dashboard
 You can personalise the dashboard by changing the contents of the `config.json` file.
 Inside the file you can change the location that COVID-19 data is retrieved from.
 You can also change the search terms for the news articles.

 ####API Keys
 Inside the `config.json` file you will need to change the api key.
 If you go to the [News API](https://newsapi.org/) website you will be able to make
 an account and get your own API key. This key will then need to be put into the 
 `config.json` file.

 ####Logging
 All runtime errors will be logged inside the log file. The default save location for the logging
 file will be inside the main project folder. This can be changed in the `config.json` file.

 ####Testing
 The projects testing files can be tested using the pytest module. These tests can be run 
 by typing `pytest` in a terminal in the root directory. This module will then automatically
 find python files that have a suffix of '_test.py' and run the assertions inside them.

 # Project documentation
 #####Standard python modules:
 - [sched](https://docs.python.org/3/library/sched.html)
 - [os](https://docs.python.org/3/library/os.html)
 - [time](https://docs.python.org/3/library/time.html)
 - [logging](https://docs.python.org/3/library/logging.html)
 - [json](https://docs.python.org/3/library/json.html)
 - [csv](https://docs.python.org/3/library/csv.html)

 #####Third-party python modules:
 - [uk_covid19](https://publichealthengland.github.io/coronavirus-dashboard-api-python-sdk/)
 - [requests](https://pypi.org/project/requests/)
 - [pytest](https://docs.pytest.org/en/6.2.x/)
 - [flask](https://flask.palletsprojects.com/en/2.0.x/)
 - [rich](https://github.com/willmcgugan/rich)

 ###Function descriptions

 covid_data_handler.py
 - parse_csv_data: This will interpret the csv data and return it in 
 a convenient format for other functions to use.
 - get_total_deaths: This function will recursively loop over the `cumDailyNsoDeathsByDeathDate` column
 in the data until it reaches a value which is then returned.
 - starting_index: This function will recursively look down the column that
 it's given until it finds a desired value.
 - process_covid_csv_data: This function will combine the three previous functions
 to return `last7days_cases`, `current_hospital_cases` and `total_deaths`.
 - covid_API_request: This function will make the API request and return
 the data in a list format.
 - get_covid_data: This function will append the data to the list that is used
 to update the data on the html
 - schedule_covid_updates: This function will be used to schedule updates to the COVID-19 data
 
 covid_news_handling.py
 - news_api_request: This function will make the API request
 - get_current_article_titles: This function will return the titles from the list passed through
 - update_news: This function will remove articles and use the API to get new articles
 - remove_article: This function will remove an article from the list
 - get_updated_news_data: This function will return new news data to be used in the scheduler
 - schedule_news_updates: This function will be used to schedule updates to the news data

 flask_app.py
 - format_time: This function will format the time into HH:MM format
 - get_seconds_until_update: This function will calculate the amount of seconds
 until the inputted time
 - update_elapsed: This function will check to see if an update has elapsed
 - enqueue_update: This function will enqueue an update in update queue
 - start_thread: This function will start a thread
 - do_tests: This function will run the pytest module and log the result
 
 ##Author
 James Calnan
 jdc235@exeter.ac.uk
 
 ##Specification
 https://vle.exeter.ac.uk/pluginfile.php/2954508/mod_label/intro/CA-specification.pdf
 
