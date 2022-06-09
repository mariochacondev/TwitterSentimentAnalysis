import re
from textblob import TextBlob
import tweepy
from login import *
import emoji
from pydantic import BaseModel
import matplotlib.pyplot as plt


class Tweet(BaseModel):
    username: str
    created_at: str
    tweet: str
    subjectivity: str | None = ''
    sentiment: str | None = ''

    def canonicalize_text(self):
        self.tweet = emoji.replace_emoji(self.tweet, replace='')
        self.tweet = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", self.tweet).split())

    def analyze(self):
        tweet_subjectivity = TextBlob(self.tweet).sentiment.subjectivity
        tweet_polarity = TextBlob(self.tweet).sentiment.polarity
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

        self.subjectivity = subjectivity
        self.sentiment = polarity


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


def plot_sentiment(tweets):
    positive_tweets = [tweet for tweet in tweets if tweet.sentiment == 'Positive']
    negative_tweets = [tweet for tweet in tweets if tweet.sentiment == 'Negative']
    neutral_tweets = [tweet for tweet in tweets if tweet.sentiment == 'Neutral']
    print("Negative tweets percentage: {} %".format(100 * len(negative_tweets) / len(tweets)))
    print("Positive tweets percentage: {} %".format(100 * len(positive_tweets) / len(tweets)))
    print("Neutral tweets percentage: {} %".format(100 * len(neutral_tweets) / len(tweets)))
    slices_tweets = [format(100 * len(positive_tweets) / len(tweets)), format(100 * len(negative_tweets) / len(tweets)),
                     format(100 * len(neutral_tweets) / len(tweets))]
    analysis = ['Positive', 'Negative', 'Neutral']
    colors = ['g', 'r', 'y']
    plt.title(keyword)
    plt.pie(slices_tweets, labels=analysis, colors=colors, startangle=-40, autopct='%.1f%%')
    plt.show()


if __name__ == '__main__':
    keyword = input('Enter the keyword to search and analyse: ')
    client = twitter_client()
    tweets = get_tweets(keyword, client, limit=150)
    for tweet in tweets:
        tweet.canonicalize_text()
        tweet.analyze()
        print(tweet)
    plot_sentiment(tweets)

