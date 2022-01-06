# Get Started

## STEP 1
Start a virtual enviornment to install the dependencies independently.

### MAC/UNIX
```
    python3 -m venv venv  # creates a virtual enviornment directory 'venv'
    . venv/bin/activate   # activates the already formed directory 'venv'
```

### WINDOWS
```
    py -m venv venv  # creates a virtual enviornment directory 'venv'
    .\venv\Scripts\activate  # activates the already formed directory 'venv'
```

## STEP 2
Install the dependencies with the following command -
```
    pip install -r requirements.txt
```

## STEP 3
After you make sure all the dependencies are installed, you are ready to run the code!
### MAC/UNIX
```
    python3 CovidBoosterV.py
```

### WINDOWS
```
    py CovidBoosterV.py
```
It takes about 5 seconds to analyze the current data and delivers output in terms of wordclouds and different types of plots.

# About the Project
"Sentiment Analysis on Covid 19 Vaccines Booster Doses using Twitter API" project is divided into TWO parts.

Folder Structure
 ```
    data
        |_ csv
            |_ General.csv
            |_ ModernaVaccine.csv
            |_ PfizerVaccine.csv
```

## 1. Fetch the tweets from twitter API
Collecting the tweets using Twitter API. Therefore, the function responsible for this is 
```
    fetchTwitterTweets()
    resultSet = reportGeneration()
    MappingAndPlotting(resultSet)
```
In this part, we create a directory on the parent path as "data" and a tweets.csv file inside it which contains our collected data from the twitter API.


## 2. Use the already collected tweets
Using the saved 
```
    #fetchTwitterTweets()
    resultSet = reportGeneration()
    MappingAndPlotting(resultSet)
```

NOTE: Make sure `fetchTwitterTweets()` should be COMMENTED otherwise it will start collecting the tweets again and it is a time consuming process. Therefore, we can use the already collected and saved data in `./data/csv/tweets.csv`.