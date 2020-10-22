import requests
import json
import time
from bs4 import BeautifulSoup as bs
from os import environ
import re

try:
    API_URL = environ['API_URL']
    API_USERNAME = environ['API_USERNAME']
    API_PASSWORD = environ['API_PASSWORD']
except:
    API_URL = "http://localhost:5000/api/poems"
    API_USERNAME = 'test1'
    API_PASSWORD = 'test1'


def sendPoems(poemFile='outputPoems.json'):
    with open(poemFile, 'r') as outfile:
        poems = json.load(outfile)
    for poem in poems:
        #poem = poem.replace('\n', '\\n')
        title = poem.split('\n')[0]
        addNewPoem(title, poem)


def generateHaiku():
    # some bullshit
    return ['''There once was a man from Nantucket\n<br/>
            who pissed all day in a bucket\n<br/>
            people came from far and near\n<br/>
            to give him a cheer\n<br/>
            and see whether he would fuck it.''',
            "butts", "Dumps like a truck", "Macaroni in a pot",
            "Wet-ass P-Word", "Fee fi fo fum large me in your throat",
            "Pixar-mom lookin' ass", "Guys like what"]


def addNewPoem(title, poem, overrideApproval=0):
    '''Posts poem to API'''
    response = requests.post(API_URL,
                             json={"title":title,"body":poem},
                             auth=(API_USERNAME, API_PASSWORD))
    
    return response.json()


def getPoembyIndex(id):
    '''Gets poem by index'''
    response = requests.get(API_URL+'/'+str(id),
                            auth=(API_USERNAME, API_PASSWORD))
    
    return response.json()


def getApprovedPoem(page=1, per_page=10):
    response = requests.get(API_URL+'/approved',
                            json={"page":page,"per_page":10},
                            auth=(API_USERNAME, API_PASSWORD))
        
    return response.json()['items']


def stampUsedPoem(id):
    '''Posts poem to API'''
    response = requests.put(API_URL+'/stamp_used/'+str(id),
                             json={'used':1},
                             auth=(API_USERNAME, API_PASSWORD))
    
    return response.json()    

if __name__ == "__main__":
    #print(getApprovedPoem(1))
    stampUsedPoem(27)
    #sendPoems()


