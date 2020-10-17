from os import environ
from flask import Flask
import requests
from django.shortcuts import render
from django.http import HttpResponse

app = Flask(__name__)
app.run(host= '0.0.0.0', port=environ.get('PORT'))


@app.route('/')
def hello_world():
    r = requests.get('http://httpbin.org/status/418')
    return HttpResponse('<pre>' + r.text + '</pre>')