import json
from pymongo import MongoClient 

def finddata(query):
    client =  MongoClient('mongodb://localhost:27017/')
    db = client['StoreData']

    collection = db[query]
    documents = list(collection.find({}))
    for data in documents:
        if '_id' in data:
            data['_id'] = str(data['_id'])

    # with open('data.json', 'w',encoding='utf-8') as file:
        # json.dump(documents, file)
    return documents
        