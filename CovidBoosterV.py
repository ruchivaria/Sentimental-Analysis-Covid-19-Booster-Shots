import twitter, datetime
import csv
import os
import pandas
import preprocessor as p
import numpy as np
from textblob import TextBlob
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import plotly.express as px

# load_dotenv()

topics = ["General", "PfizerVaccine", "ModernaVaccine"]
searchHashtags = {
            'General': ['boostershot','GetYourBooster', 'CovidBoosterShot', 'Boosted', 'CovidBooster', 'Booster',
                        'BoosterJab','3rddose','boosterdose','boostershots','boosterdoses','boosters'],
            'PfizerVaccine': ['PfizerBooster', 'PfizerBoosterShot'],
            'ModernaVaccine': ['ModernaBoosterShot', 'ModernaBooster']

            }


def oAuthentication_Login():
    '''
    A static method to authenticate user
    It uses OAuth2.0 specification which takes a bearer token to authenticate user
    '''

    # CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
    # CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
    # BEARER_TOKEN= os.environ.get('BEARER_TOKEN')

    CONSUMER_KEY = 'agQmGHFcg9CDeoUSXUFvdPl lT'
    CONSUMER_SECRET = 'N9rqHRmzCJt4SALlxWOCbYyXno0khHnbFTwBFVnrqEKWA1VlfL'
    BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAE04NwEAAAAAjQ9nJ%2BLef%2Fkj3cM1txJPOBATLJk%3DisQRS6PBXd5VLdOFUFgirQpkoK5oygGUbLMku7G0vYetzIyYJt"

    auth = twitter.OAuth2(CONSUMER_KEY, CONSUMER_SECRET, BEARER_TOKEN)
    api = twitter.Twitter(auth=auth)
    return api


def cleaningResults(rawResult, topic):
    '''
    To take required text for NLP, may change later as per the requirement
    '''
    resultantList = []
    for internalList in rawResult["statuses"]:
        obj = dict()
        obj["tweet"] = internalList["text"]
        obj["id"] = internalList["id_str"]
        obj["name"] = internalList["user"]["name"]
        obj["location"] = internalList["user"]["location"]
        obj["topic"] = topic
        obj["created_at"] = internalList["created_at"]
        obj["processed_on"] = datetime.datetime.now().isoformat(' ', 'seconds')
        resultantList.append(obj)
    return resultantList


def saveTwitterTweetsInCSV(cleanedTweets, topic):
    """
    This method will help us on saving tweets in a CSV file
    """
    try:
        colNames = list(cleanedTweets[0].keys())
        outDir = os.path.join('data', 'csv')
        outFile = os.path.join(outDir, topic + '.csv')
        if not os.path.exists(outFile):
            open(outFile, 'w').close()
        isFileEmpty = os.stat(outFile).st_size == 0
        with open(outFile, mode='a', newline='', encoding='utf-8') as CSV_File:
            CSV_Writer = csv.DictWriter(CSV_File, fieldnames=colNames, extrasaction="ignore")
            if isFileEmpty:
                CSV_Writer.writeheader()
            CSV_Writer.writerows(cleanedTweets)
        print("Inserted Data Successfully!")
    except Exception as e:
        print(e)


def queryTwitterTweets(query, totalCount, topic):
    """
    Queries and finds tweet for different hashtags/topic, it will keep on searching until it finds total count
    """
    twitterApi = oAuthentication_Login()
    metaData = query.split("-RT")[0].split('#')[1]
    resFSearch = twitterApi.search.tweets(q=query, count=500)
    print(resFSearch["search_metadata"])
    saveTwitterTweetsInCSV(cleaningResults(resFSearch, metaData), topic)
    result_count = resFSearch["search_metadata"]["count"]
    nextMax_ID = resFSearch["search_metadata"]["next_results"].split('max_id=')[1].split('&')[0]
    while result_count < totalCount:
        resultInter = twitterApi.search.tweets(q=query, include_entities='true', max_id=nextMax_ID, count=500)
        print(resultInter["search_metadata"])
        print(result_count)
        saveTwitterTweetsInCSV(cleaningResults(resultInter, metaData), topic)
        result_count += resultInter["search_metadata"]["count"]
        if "next_results" in resultInter["search_metadata"]:
            nextMax_ID = resultInter["search_metadata"]["next_results"].split('max_id=')[1].split('&')[0]
        else:
            break


# def get_docs_csv():
#      '''
#     This method is used to download the csv from mongodb
#     '''
#     client = pymongo.MongoClient(mongo)
#     database = client[db]
#     for col in topics:
#         coll = database[col]
#         try:
#             result = coll.find()
#
#             fieldnames = list(result[0].keys())
#             fieldnames.remove('_id')
#
#             output_dir = os.path.join('data', 'csv')
#             output_file = os.path.join(output_dir, col+'.csv')
#             with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
#                 writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction="ignore")
#                 writer.writeheader()
#                 writer.writerows(result)
#
#         except Exception as e:
#             print(e)

def removePunctuationMarks(text):
    '''
    This method is used to clean the tweets
    '''
    punct = ['%', '/', ':', '\\', '&amp;', '&', ';']
    for punctuation in punct:
        text = text.replace(punctuation, '')
    return text


def getCountValue(col_name, analyzer_name, tweets_df):
    '''
    This function returns count of the dataset passed, it uses pands library to do the same
    '''
    count = pandas.DataFrame(tweets_df[col_name].value_counts())
    percentage = pandas.DataFrame(tweets_df[col_name].value_counts(normalize=True).mul(100))
    counts = pandas.concat([count, percentage], axis=1)
    counts = counts.reset_index()
    counts.columns = ['sentiment', 'counts', 'percentage']
    counts.sort_values('sentiment', inplace=True)
    counts['percentage'] = counts['percentage'].apply(lambda x: round(x, 2))
    counts = counts.reset_index(drop=True)
    counts['analyzer'] = analyzer_name
    return counts


def fetchTwitterTweets():
    '''
    This method fetches and stores the tweets for the last seven days and store it in a csv file.
    '''
    try:
        for topickey in searchHashtags.keys():
            for actHashtag in searchHashtags[topickey]:
                queryTwitterTweets("#" + actHashtag + " -RT AND lang:en", 10000, topickey)
        print("Fetched tweets properly!")
    except Exception as e:
        print(e)


def reportGeneration():
    '''
    This method is used to generate the report from the csv
    '''
    try:
        #topics = ["ModernaVaccine", "JohnsonAndJohnsonVaccine", "PfizerVaccine", "Vaccinated"]
        topics = ["General", "PfizerVaccine", "ModernaVaccine"]
        final_bar = []
        result_copy = dict()
        for topic in topics:
            file_dir = os.path.join('data', 'csv')
            file = os.path.join(file_dir, topic + '.csv')
            result = pandas.read_csv(file)
            result.sort_values(by="created_at")
            result_copy[topic] = result.copy()
            result_copy[topic]['tweet_cleaned'] = result_copy[topic]['tweet'].apply(lambda x: p.clean(x))
            result_copy[topic].drop_duplicates(subset='tweet_cleaned', keep='first', inplace=True)

            # remove punctuations
            result_copy[topic]['tweet_cleaned'] = result_copy[topic]['tweet_cleaned'].apply(
                lambda x: removePunctuationMarks(x))

            # Drop tweets which have empty text field
            result_copy[topic]['tweet_cleaned'].replace('', np.nan, inplace=True)
            result_copy[topic]['tweet_cleaned'].replace(' ', np.nan, inplace=True)
            result_copy[topic].dropna(subset=['tweet_cleaned'], inplace=True)

            result_copy[topic] = result_copy[topic].reset_index(drop=True)

            # sentiment analysis
            # Obtain polarity scores generated by TextBlob
            result_copy[topic]['textblob_score'] = result_copy[topic]['tweet_cleaned'].apply(
                lambda x: TextBlob(x).sentiment.polarity)
            # neutral_thresh = 0.05

            # Convert polarity score into sentiment categories
            result_copy[topic]['textblob_sentiment'] = result_copy[topic]['textblob_score'].apply(
                lambda c: 'Positive' if c >= 0.1 else ('Negative' if c <= -(0.1) else 'Neutral'))

            textblob_sentiment_df = getCountValue('textblob_sentiment', 'TextBlob', result_copy[topic])

            final_bar.append(textblob_sentiment_df)

        # bargraph plotting
        fig = plt.figure()
        fig.subplots_adjust(hspace=0.8, wspace=0.8)

        plt.rcParams["figure.figsize"] = (26, 8)

        ax = fig.add_subplot(2, 2, 1)
        ax.set_title(topics[0])
        for index, row in final_bar[0].iterrows():
            ax.text(row.name, row.percentage, round(row.percentage, 1), color='black', ha="center")
        sns.barplot(x="sentiment", y="percentage", data=final_bar[0], ax=ax)

        ax = fig.add_subplot(2, 2, 2)
        ax.set_title(topics[1])
        for index, row in final_bar[1].iterrows():
            ax.text(row.name, row.percentage, round(row.percentage, 1), color='black', ha="center")
        sns.barplot(x="sentiment", y="percentage", data=final_bar[1], ax=ax)

        ax = fig.add_subplot(2, 2, 3)
        ax.set_title(topics[2])
        for index, row in final_bar[2].iterrows():
            ax.text(row.name, row.percentage, round(row.percentage, 1), color='black', ha="center")
        sns.barplot(x="sentiment", y="percentage", data=final_bar[2], ax=ax)

        plt.show()

        # worldcloud
        # #vaccinated
        comment_words = ''
        stopwords = set(STOPWORDS)
        result_copy['General'].head(10)
        for topic in topics:
            for val in result_copy[topic].values:
                row = val[7]
                # print(row)
                tokens = row.split()
                # Converts each token into lowercase
                for i in range(len(tokens)):
                    tokens[i] = tokens[i].lower()

                comment_words += " ".join(tokens) + " "
            wordcloud = WordCloud(width=800, height=800,
                                  background_color='black',
                                  stopwords=stopwords,
                                  min_font_size=10).generate(comment_words)
            plt.figure(figsize=(8, 8), facecolor=None)
            plt.imshow(wordcloud)
            plt.axis("off")
            plt.tight_layout(pad=0)

            plt.show()
        return result_copy

    except Exception as e:
        print(e)


def MappingAndPlotting(result_copy):
    '''
    This method is used for plotting the graph
    '''
    state_codes = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "ID",
                   "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO",
                   "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA",
                   "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

    states_mapping = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
                      "Colorado": "CO", "Connecticut": "CT", "Washington DC": "DC", "Delaware": "DE", "Florida": "FL",
                      "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
                      "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
                      "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
                      "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
                      "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC",
                      "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
                      "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN",
                      "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
                      "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"}

    for topic in topics:
        for index, row in result_copy[topic].iterrows():
            flag = 0
            if row.location:
                location_split = str(row.location).split(',')
                for word in location_split:
                    word = word.strip()
                    for state, code in states_mapping.items():
                        if state == word.title() or code == word:
                            result_copy[topic].at[index, 'us_state_code'] = code
                            result_copy[topic].at[index, 'us_state'] = state
                            flag = 1
                            break
                    if flag == 1:
                        break

    result_states = {}
    for topic in topics:
        result_states[topic] = result_copy[topic][result_copy[topic]['us_state_code'].notna()]
        #topic = 'PfizerVaccine'
        topic = 'General'

    print(len(result_states[topic]))
    result_states[topic]['us_state_code'].head(10)

    df_states = []
    for i in state_codes:
        dic = {'State': i, 'Positive': 0, 'Negative': 0, 'Neutral': 0}
        df_states.append(dic)
    # now update
    for ind, row in result_states[topic].iterrows():
        curr_state = row['us_state_code']
        for item in df_states:
            if item['State'] == curr_state:
                item[row['textblob_sentiment']] = item[row['textblob_sentiment']] + 1
                break

    # positive percentage
    for row in df_states:
        curr_total = int(row['Positive']) + int(row['Negative']) + int(row['Neutral'])
        row.setdefault('Total', curr_total)
        if curr_total > 0:
            row.setdefault('PositivePercentage', round(float(row['Positive'] / row['Total'] * 100), 2))
            row.setdefault('NegativePercentage', round(float(row['Negative'] / row['Total'] * 100), 2))
        else:
            row.setdefault('PositivePercentage', 0)
            row.setdefault('NegativePercentage', 0)
    # print(pandas.DataFrame(df_states))
    state_df = pandas.DataFrame(df_states)

    fig = px.choropleth(state_df, locations='State', locationmode='USA-states',
                        scope='usa', color='PositivePercentage', hover_name='State',
                        hover_data=['Positive', 'Negative', 'Neutral'], range_color=[10, 90],
                        color_continuous_scale='armyrose', title='Covid-19 Booster Vaccine Positive Sentiment Analysis')
    fig.show()

    # negative percentage
    fig = px.choropleth(state_df, locations='State', locationmode='USA-states',
                        scope='usa', color='NegativePercentage', hover_name='State',
                        hover_data=['Positive', 'Negative', 'Neutral'], range_color=[10, 90],
                        color_continuous_scale='sunset', title='Covid-19 Booster Vaccine Negative Sentiment Analysis')
    fig.show()

    positivePercentage = []
    negativePercentage = []
    for staterow in df_states:
        positivePercentage.append(int(staterow['PositivePercentage']))
        negativePercentage.append(int(staterow['NegativePercentage']))

    sumPos = sum(positivePercentage)
    for idx, sRow in enumerate(positivePercentage):
        positivePercentage[idx] = (sRow/sumPos)*100

    sumNeg = sum(negativePercentage)
    for idx, sRow in enumerate(negativePercentage):
        negativePercentage[idx] = (sRow/sumPos)*100

    # Pie chart Positive
    y = np.array(positivePercentage)

    legendLabel = [a + "=" + str(round(b,2)) + "%" for (a, b) in zip(state_codes, positivePercentage)]
    plt.title('Covid-19 Booster Vaccine Positive Sentiment Analysis Pie Chart')
    print(len(positivePercentage))
    explode = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    plt.pie(y, labels=state_codes, explode=explode)
    plt.legend(legendLabel, title="USA States with Positive %", bbox_to_anchor=(0.8, 0.5), loc="center right", fontsize=8, bbox_transform=plt.gcf().transFigure)
    plt.show()

    # Pie chart Negative
    y = np.array(negativePercentage)

    legendLabel = [a + "=" + str(round(b,2)) + "%" for (a, b) in zip(state_codes, negativePercentage)]
    plt.title('Covid-19 Booster Vaccine Negative Sentiment Analysis Pie Chart')
    explode = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.2)
    plt.pie(y, labels=state_codes, explode=explode)
    plt.legend(legendLabel, title="USA States with Negative %", bbox_to_anchor=(0.8, 0.5), loc="center right", fontsize=8, bbox_transform=plt.gcf().transFigure)
    plt.show()

if __name__ == '__main__':
    # fetchTwitterTweets()
    resultSet = reportGeneration()
    MappingAndPlotting(resultSet)
