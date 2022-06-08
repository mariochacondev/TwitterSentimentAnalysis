import re
from textblob import TextBlob
import tweepy
from login import *
import pandas as pd
import emoji

pd.set_option('max_colwidth', 30)
pd.set_option('display.max_columns', 4)
pd.set_option('display.max_rows', None)

tweets_list = []
formatted_tweets = []

def auth_twitter():
    auth = tweepy.OAuthHandler(APY_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    client = tweepy.API(auth)
    return client


def get_tweets(keyword):
    client = auth_twitter()
    limit = 150
    tweets = tweepy.Cursor(client.search_tweets,
                           q=keyword,
                           count=limit,
                           tweet_mode='extended').items(limit)
    for tweet in tweets:
        each_tweet = {'Username': tweet.user.screen_name, 'Tweet': tweet.full_text}
        tweets_list.append(each_tweet)
    return tweets_list


def clean_tweets():
    for tweet in tweets_list:
        tweet['Tweet'] = re.sub('\\n', '', tweet['Tweet'])
        tweet['Tweet'] = emoji.replace_emoji(tweet['Tweet'], replace='')
        tweet['Tweet'] = re.sub('#[A-Za-z0-9]+', '', tweet['Tweet'])
        tweet['Tweet'] = re.sub(u'[\u4e00-\u9fff]', '', tweet['Tweet'])
        tweet['Tweet'] = re.sub(r"http\S+", '', tweet['Tweet'])
        formatted_tweets.append(tweet)
    return formatted_tweets


def analyze_tweets():
    df = pd.DataFrame()
    for tweet in formatted_tweets:
        tweet_subjectivity = TextBlob(tweet['Tweet']).sentiment.subjectivity
        tweet_polarity = TextBlob(tweet['Tweet']).sentiment.polarity
        if tweet_polarity < 0:
            polarity = 'Negative'
        elif tweet_polarity == 0:
            polarity = 'Neutral'
        else:
            polarity = 'Positive'

        if tweet_subjectivity == 0:
            subjectivity = 'Objective'
        elif 0 < tweet_subjectivity < 1.0:
            subjectivity = 'Subjective'
        else:
            subjectivity = 'Very Subjective'
        data = pd.DataFrame({'Username': tweet['Username'],
                             'Tweet': [tweet['Tweet']],
                             'Subjectivity': [subjectivity],
                             'Sentiment': [polarity]})
        df = pd.concat([df, data], ignore_index=True)
    return df.set_index('Username')


if __name__ == '__main__':
    keyword = input('Enter the keyword to search and analyse: ')
    get_tweets(keyword)
    clean_tweets()
    print(analyze_tweets())

