import time
import datetime
import random
import tweepy
import poemGenerator
import mailHandler
import requests
import json
import dateutil.parser
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
    API_URL = environ['API_URL']
    API_USERNAME = environ['API_USERNAME']
    API_PASSWORD = environ['API_PASSWORD']
    FREQUENCY = int(environ['FREQUENCY'])
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
except:
    pass

scheduler = BlockingScheduler()


def getToken(username, password):
    response = requests.post(url=API_URL+"/api/tokens",
                  auth=(API_USERNAME, API_PASSWORD))
    try:
        token = response.json()['token']
    except:
        token = None

    return token


def addJob(date):
    '''Posts Job to API'''
    date = datetime.datetime.isoformat(date)
    token = getToken(API_USERNAME, API_PASSWORD)
    response = requests.post(API_URL+"/api/jobs",
                             json={"scheduledTime":date},
                             headers={"Authorization": "Bearer "+token})
    #print(response.content)
    #return response.json()


def jobInFuture(job):
    '''Checks if job schedule is still ahead'''
    job = datetime.datetime.fromisoformat(job['scheduledTime'])

    return (datetime.datetime.now() - job) < datetime.timedelta()


def getJobs():
    token = getToken(API_USERNAME, API_PASSWORD)
    response = requests.get(API_URL+"/api/jobs",
                            headers={"Authorization": "Bearer "+token})
    jobs = response.json()
    for job in jobs:
        if not jobInFuture(job):
            removeJob(job['id'])
            jobs.remove(job)
    
    return jobs


def removeJob(id):
    '''Removes Job from API'''
    token = getToken(API_USERNAME, API_PASSWORD)
    response = requests.post(API_URL+"/api/jobs/remove/"+str(id),
                             json={"id":id},
                             headers={"Authorization": "Bearer "+token})
    print(response.content)
    return None



def clearJobSchedule():
    jobs = getJobs()
    for job in jobs:
        removeJob(job['id'])


def closestValue(value, a):
    return min(range(len(a)), key=lambda i: abs(a[i]-value))


def circular_search(points, bound, value):
    points = sorted(list(set([i % bound for i in points])))
    value %= bound
    ext_points = [i-bound for i in points] + points + [i+bound for i in points]
    index = bisect_right(ext_points, value)
    if abs(ext_points[index]-value) >= abs(ext_points[index-1]-value):
        index -= 1
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

def sendTweet(poem):
    print("sent!")
    body = poem['body']
    body += "\n\n#Haiku"
    api.update_status(body)
    poemGenerator.stampUsedPoem(poem['id'])


def updateStatus(id):
    poem = getPoem()
    if not poem:
        #mailHandler.alertEmail()
        pass
    while not poem:
        time.sleep(3600)
        poem = getPoem()
    try:
        sendTweet(poem)
    except:
        print("tweet failed")
    removeJob(id)
    jobs = getJobs()
    if not jobs:
        addJobsToDatabase()
        jobs = getJobs()
        scheduleJobs(jobs)
        
    return None


def addJobsToDatabase():
    schedule = createTwitterHeatMap.createTweetSchedule(FREQUENCY)
    today = datetime.datetime.today()
    year, month, day, hour, minute, second = today.timetuple()[0:6]
    weekday = datetime.datetime.weekday(today)
    dayHour = weekday * 24 + hour
    closest = circular_search(schedule, 168, dayHour)
    schedule = schedule[closest+1::]
    #Add jobs to scheduler
    schedule = [datetime.datetime(year, month, day+(job//24 - weekday), job%24) for job in schedule]
    firstTime = today + datetime.timedelta(minutes=5)
    lastTime = today + datetime.timedelta(days=7-weekday)
    schedule = [firstTime] + schedule + [lastTime]
    for job in schedule:
        addJob(job)
    print(scheduleJobs)


def scheduleJobs(jobs):
    for x, job in enumerate(jobs):
        scheduler.add_job(updateStatus, 'date',
                          run_date=datetime.datetime.fromisoformat(job['scheduledTime']),
                          args=[job['id']])


def pingDB():
    '''Pings to keep worker awake'''
    getPoem()
    return "Ping!"


def updateLoop():
    scheduler.add_job(pingDB, 'interval', minutes=25)
    jobs = getJobs()
    if not jobs:
        addJobsToDatabase()
        jobs = getJobs()
    scheduleJobs(jobs)

    scheduler.start()


if __name__ == "__main__":
    updateLoop()

