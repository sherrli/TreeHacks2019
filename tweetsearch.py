import re
import io
import csv
import tweepy
from tweepy import OAuthHandler
#TextBlob perform simple natural language processing tasks.
#from textblob import TextBlob

consumer_key = 'sz6x0nvL0ls9wacR64MZu23z4'
consumer_secret = 'ofeGnzduikcHX6iaQMqBCIJ666m6nXAQACIAXMJaFhmC6rjRmT'
access_token = '854004678127910913-PUPfQYxIjpBWjXOgE25kys8kmDJdY0G'
access_token_secret = 'BC2TxbhKXkdkZ91DXofF7GX8p2JNfbpHqhshW1bwQkgxN'
# create OAuthHandler object
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# set access token and secret
auth.set_access_token(access_token, access_token_secret)
# create tweepy API object to fetch tweets
api = tweepy.API(auth)


def get_tweets(query, count = 30):

    # empty list to store parsed tweets
    tweets = []
    # tweets.append("TWEETLIST")
    target = io.open("mytweets.txt", 'w', encoding='utf-8')

    query = f'{query} -filter:retweets AND -filter:replies AND -filter:location' 
    # query = 'flu' 

    fetched_tweets = api.search(q=query, count=200000)

    print(len(fetched_tweets))

    for tweet in fetched_tweets:

        # empty dictionary to store required params of a tweet
        parsed_tweet = {}
        # saving text of tweet
        parsed_tweet['text'] = tweet.text
        parsed_tweet['user_location']=tweet.user.location
        if tweet.user.location:
            # print(re.sub("[^A-Za-z]", " ", tweet.user.location))
            # line = re.sub("[^A-Za-z]", " ", tweet.text)
            # location = re.sub("[^A-Za-z]", " ", tweet.user.location)
            location = tweet.user.location
            target.write(location+"\n")
            tweets.append(location)
    
    returned_tweets = []
    for tweet in tweets:
        if "," in str(tweet):
            returned_tweets.append(tweet)

    return returned_tweets

    # creating object of TwitterClient Class
    # calling function to get tweets
tweets = get_tweets(query ="", count = 488990)

target = io.open("locations.csv", 'w', encoding='utf-8')

for tweet in tweets:
    if "," in str(tweet):
        target.write(tweet+"\n")

