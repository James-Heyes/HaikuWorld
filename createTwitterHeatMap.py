import tweepy
import re
import json
import numpy as np
import datetime
from itertools import groupby
from os import environ


#Twitter API credentials
CONSUMER_KEY = environ['CONSUMER_KEY']
CONSUMER_SECRET = environ['CONSUMER_SECRET']
ACCESS_KEY = environ['ACCESS_KEY']
ACCESS_SECRET = environ['ACCESS_SECRET']


def flattenList(inpList):
    return [item for sublist in inpList for item in sublist]


def normalize(inpList):
    return [item/sum(inpList) for item in inpList]


def get_all_tweets(screen_name):
    #Twitter only allows access to a users most recent 3240 tweets with this method
    #authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    #initialize a list to hold all the tweepy Tweets
    alltweets = []  
    #make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name = screen_name,count=200)
    #save most recent tweets
    alltweets.extend(new_tweets)
    #save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1
    #keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        print(f"getting tweets before {oldest}")
        #all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
        #save most recent tweets
        alltweets.extend(new_tweets)
        #update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1
        print(f"...{len(alltweets)} tweets downloaded so far")
    outtweets = [[tweet.id_str, tweet.created_at, tweet.retweet_count, tweet.favorite_count] for tweet in alltweets]

    return outtweets


def createTweetFile(inputUsernameList, filename="tweets.json"):
    '''Creates a file with all tweets from given input user list'''
    outtweets = []
    for user in inputUsernameList:
        outtweets += [(user, get_all_tweets(user))]
    
    with open(filename, 'w') as outfile:
        outfile.write(json.dumps(outtweets, indent=4, sort_keys=True, default=str))
    return filename



def createTweetSchedule(tweetsPerWeek=7, filename="probabilities.json"):
    with open(filename, 'r') as infile:
        tweets = json.loads(infile.read())
    choices = [np.random.choice(np.arange(1, 169), p=tweets) for x in range(10)]
    choices.sort()
    # randomly select times based on probabilities
    choices = []
    for ind in range(tweetsPerWeek):
        choice = np.random.choice(np.arange(0, len(tweets)), p=tweets)
        choices += [choice]
        del tweets[choice]
        tweets = normalize(tweets)
    choices.sort()
    tweetSchedule = choices

    return tweetSchedule


def writeHourProbabilities(tweetFile="SupremeHaiku_tweets.json", filename="probabilities.json"):
    # Load tweet file
    with open(tweetFile, 'r') as infile:
        tweets = json.loads(infile.read())
    tweets = flattenList([x[1] for x in tweets])

    # Convert datetime formate
    tweets = [tweet[0:1]
              +[datetime.datetime(*[int(x) for x in re.split('[^\d]', tweet[1])])]
              +tweet[2:] for tweet in tweets]
    # Convert to 168 hour clock
    tweets = [[tweet[1].weekday()*24 + tweet[1].hour ]+tweet[0:1]+tweet[2:] for tweet in tweets]
    tweets.sort(key=lambda x: x[0])
    tweets = [list(v) for i, v in groupby(tweets, lambda x: x[0])]
    tweets = [(tweetList[0][0], [tweet[1::]for tweet in tweetList]) for tweetList in tweets]
    emptyInd = [x for x in range(168) if x not in [tweetList[0] for tweetList in tweets]]
    tweets = dict(tweets)
    # Fill in empty indices
    tweets = [(x, tweets[x]) if x not in emptyInd else (x, []) for x in range(168)]
    tweets = [sum([tweet[1]+tweet[2] for tweet in tweetList[1]]) for tweetList in tweets]
    # Normalize probabilites
    probabilities = normalize(tweets)

    with open(filename, 'w') as outfile:
        outfile.write(json.dumps(probabilities, indent=4, sort_keys=True, default=str))
    return filename


if __name__ == '__main__':
    userList = ["Its_Haiku_Time", "thelindsayellis", "JennyENicholson"]
    #filename = createTweetFile(userList)
    #print(writeHourProbabilities(tweetFile='tweets.json'))
    schedule = createTweetSchedule()
    #print(schedule)
    #print([(x//24, x%24) for x in schedule])