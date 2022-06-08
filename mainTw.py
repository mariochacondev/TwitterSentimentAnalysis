import re
from textblob import TextBlob
import tweepy
from login import *
import emoji
from pydantic import BaseModel


class Tweet(BaseModel):
    username: str
    created_at: str | None = ''
    tweet: str
    subjectivity: str | None = ''
    sentiment: str | None = ''



def twitter_client():
    auth = tweepy.OAuthHandler(APY_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    return tweepy.API(auth)


def get_tweets(keyword, client, limit):
    tweets = []
    response = tweepy.Cursor(client.search_tweets,
                             q=keyword+'-filter:retweets',
                             count=limit,
                             tweet_mode='extended').items(limit)
    for tweet in response:
        each_tweet = Tweet(username=tweet.user.screen_name, tweet=tweet.full_text, created_at=tweet.created_at.strftime("%d/%m/%Y %H:%M"))
        tweets.append(each_tweet)
    return tweets


def process_tweets(tweets_list):
    formatted_tweets = []
    for elem in tweets_list:
        elem.tweet = emoji.replace_emoji(elem.tweet, replace='')
        elem.tweet = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", elem.tweet).split())
        if elem.tweet:
            formatted_tweets.append(elem)
    return formatted_tweets


def analyze_tweets(formatted_tweets):
    for elem in formatted_tweets:
        tweet_subjectivity = TextBlob(elem.tweet).sentiment.subjectivity
        tweet_polarity = TextBlob(elem.tweet).sentiment.polarity
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

        elem.subjectivity = subjectivity
        elem.sentiment = polarity
    return formatted_tweets


if __name__ == '__main__':
    keyword = input('Enter the keyword to search and analyse: ')
    client = twitter_client()
    tweets = get_tweets(keyword, client, limit=50)
    cleaned_tweets = process_tweets(tweets)
    for elem in analyze_tweets(cleaned_tweets):
        print(elem)

