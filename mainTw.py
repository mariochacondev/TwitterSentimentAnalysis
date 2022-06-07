import re
from textblob import TextBlob
import tweepy
from login import *
import pandas as pd
import emoji

pd.set_option('max_colwidth', 30)
pd.set_option('display.max_columns', 4)
pd.set_option('display.max_rows', 100)


def auth_twitter():
    auth = tweepy.OAuthHandler(APY_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    client = tweepy.API(auth)
    return client


def get_tweets(keyword):
    client = auth_twitter()
    limit = 100
    tweets = tweepy.Cursor(client.search_tweets,
                           q=keyword,
                           count=limit,
                           tweet_mode='extended').items(limit)
    return [tweet.user.screen_name + ' ' + tweet.full_text + '\n' for tweet in tweets]


def clean_tweets(keyword):
    formatted_tweets = []
    for tweet in get_tweets(keyword):
        tweet = re.sub('\\n', '', tweet)
        tweet = emoji.replace_emoji(tweet, replace='')
        tweet = re.sub('#[A-Za-z0-9]+', '', tweet)
        tweet = re.sub(u'[\u4e00-\u9fff]', '', tweet)
        tweet = re.sub(r"http\S+", '', tweet)
        formatted_tweets.append(tweet)
    return [tweet for tweet in formatted_tweets]


def analyze_tweets(keyword):
    df = pd.DataFrame()
    for tweet in clean_tweets(keyword):
        tweet_subjectivity = TextBlob(tweet).sentiment.subjectivity
        tweet_polarity = TextBlob(tweet).sentiment.polarity
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
        username = tweet.split()
        data = pd.DataFrame({'Username': username[0], 'Tweet': [tweet], 'Subjectivity': [subjectivity], 'Sentiment': [polarity]})
        df = pd.concat([df, data], ignore_index=True)
    return df.set_index('Username')


if __name__ == '__main__':
    keyword = input('Enter the keyword to search: ')
    print(analyze_tweets(keyword))

