import time
import datetime
import random
import tweepy
import poemGenerator
import mailHandler
from os import environ
import createTwitterHeatMap
from bisect import bisect_right
from apscheduler.events import EVENT_JOB_EXECUTED
from apscheduler.schedulers.blocking import BlockingScheduler

try:
    CONSUMER_KEY = environ['CONSUMER_KEY']
    CONSUMER_SECRET = environ['CONSUMER_SECRET']
    ACCESS_KEY = environ['ACCESS_KEY']
    ACCESS_SECRET = environ['ACCESS_SECRET']
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
except:
    pass

scheduler = BlockingScheduler()


def closestValue(value, a):
    return min(range(len(a)), key=lambda i: abs(a[i]-value))


def circular_search(points, bound, value):
    ## normalize / sort input points to [0, bound)
    points = sorted(list(set([i % bound for i in points])))
    ## normalize search value to [0, bound)
    value %= bound
    ## wrap the circle left and right
    ext_points = [i-bound for i in points] + points + [i+bound for i in points]
    ## identify the "nearest not less than" point; no
    ## edge cases since points always exist above & below
    index = bisect_right(ext_points, value)
    ## choose the nearest point; will always be either the
    ## index found by bisection, or the next-lower index
    if abs(ext_points[index]-value) >= abs(ext_points[index-1]-value):
        index -= 1
    ## map index to [0, npoints)
    index %= len(points)

    return index


def getPoem():
    poems = poemGenerator.getApprovedPoem()
    if poems:
        poem = poems[0]

    else:
        # run coroutine
        poem = None
    return poem


def updateStatus(shutdown=0):
    poem = getPoem()
    if not poem:
        #Sigh
        #mailHandler.alertEmail()
    while not poem:
        #No Poem
        time.sleep(3600)
        poem = getPoem()
    try:
        print(poem['body'])
        #api.update_status(poem['body'])
        #poemGenerator.stampUsedPoem(poem['id'])
    except:
        print("tweet failed")
    if shutdown:
        addJobs()
    return None


def addJobs():
    schedule = createTwitterHeatMap.createTweetSchedule(14)
    today = datetime.datetime.today()
    year, month, day, hour, minute, second = today.timetuple()[0:6]
    weekday = datetime.datetime.weekday(today)
    dayHour = weekday * 24 + hour
    closest = circular_search(schedule, 168, dayHour)
    schedule = schedule[closest+1::]
    #Add jobs to scheduler
    schedule = [datetime.datetime(year, month, day+(job//24 - weekday), job%24) for job in schedule]
    firstTime = today + datetime.timedelta(seconds=5)
    schedule = [firstTime] + schedule
    for x, job in enumerate(schedule):
        scheduler.add_job(updateStatus, 'date', run_date=job, args=[x==len(schedule)-1])


def updateLoop():
    addJobs()
    scheduler.start()


if __name__ == "__main__":
    updateLoop()

