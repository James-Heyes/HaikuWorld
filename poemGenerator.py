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
    API_URL = "http://localhost:5000"
    API_USERNAME = 'test1'
    API_PASSWORD = 'test1'


def sendPoems(poemFile='outputPoems.json'):
    with open(poemFile, 'r') as outfile:
        poems = json.load(outfile)
    for poem in poems:
        #poem = poem.replace('\n', '\\n')
        title = poem.split('\n')[0]
        addNewPoem(title, poem)


def addNewPoem(title, poem, overrideApproval=0):
    '''Posts poem to API'''
    response = requests.post(API_URL+"/api/poems",
                             json={"title":title,"body":poem},
                             auth=(API_USERNAME, API_PASSWORD))
    
    return response.json()


def getPoembyIndex(id):
    '''Gets poem by index'''
    response = requests.get(API_URL+'/api/poems/'+str(id),
                            auth=(API_USERNAME, API_PASSWORD))
    
    return response.json()


def getApprovedPoem(page=1, per_page=10):
    response = requests.get(API_URL+'/api/poems/approved',
                            json={"page":page,"per_page":10},
                            auth=(API_USERNAME, API_PASSWORD))
        
    return response.json()['items']


def stampUsedPoem(id):
    '''Posts poem to API'''
    response = requests.put(API_URL+'/api/poems/stamp_used/'+str(id),
                             json={'used':1},
                             auth=(API_USERNAME, API_PASSWORD))
    
    return response.json()    

if __name__ == "__main__":
    #print(getApprovedPoem(1))
    stampUsedPoem(27)
    #sendPoems()


