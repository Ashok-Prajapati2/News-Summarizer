from flask import Flask, render_template, request, redirect, url_for, flash,session
import json
app = Flask(__name__)
from pymongo import MongoClient 

def finddata(query):
    client =  MongoClient('mongodb://localhost:27017/')
    db = client['StoreData']

    collection = db[query]
    documents = list(collection.find({}))
    for data in documents:
        if '_id' in data:
            data['_id'] = str(data['_id'])

    with open('data.json', 'w',encoding='utf-8') as file:
        json.dump(documents, file)
        
finddata('science')
@app.route('/')
def index():

    return render_template('index.html')