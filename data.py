import json
import os
from pymongo import MongoClient

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['StoreData']

# Path to the JSON file
json_file_path = 'data.json'

collection = db['data science']

# Load the JSON file
try:
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # Insert data into MongoDB collection
    if isinstance(data, list):  # Ensure the data is a list of documents
        result = collection.insert_many(data)  # Insert multiple documents
        print(f"Inserted {len(result.inserted_ids)} documents into the collection.")
    else:
        print("The JSON file does not contain a list of documents.")
except FileNotFoundError:
    print(f"The file {json_file_path} was not found.")
except json.JSONDecodeError:
    print("Error decoding JSON. Please check the file format.")
except Exception as e:
    print(f"An error occurred: {e}")

