import os
import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch the user and password from the environment variables
user = os.getenv('MONGO_DB_USER')
if not user:
    raise ValueError("No user set for MongoDB. Please set the MONGO_DB_USER environment variable.")

password = os.getenv('MONGO_DB_PASSWORD')
if not password:
    raise ValueError("No password set for MongoDB. Please set the MONGO_DB_PASSWORD environment variable.")

# Construct the connection string to your MongoDB Atlas cluster
CONNECTION_STRING = f"mongodb+srv://{user}:{password}@cluster0.rskew5e.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

def connect_to_mongo(connection_string):
    client = MongoClient(connection_string, server_api=ServerApi('1'))
    return client

def read_json_files(folder_path):
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    data = {}
    for json_file in json_files:
        with open(os.path.join(folder_path, json_file), 'r', encoding='utf-8') as file:
            collection_name = os.path.splitext(json_file)[0]
            data[collection_name] = json.load(file)
    return data

def upload_to_mongo(db, data):
    for collection_name, documents in data.items():
        collection = db[collection_name]
        print("Collection: ", collection)
        #print("Documents: ", documents)
        
        if isinstance(documents, list):
            collection.insert_many(documents)
        else:
            collection.insert_one(documents)
        

def main():
    folder_path = "C:/Users/valentin/Documents/TrackFinder/music_folder"
    client = connect_to_mongo(CONNECTION_STRING)
    db = client.valentin_music_db
    data = read_json_files(folder_path)
    #print("\n\n DATA: \n\n", data)
    #print("\n\n")
    #upload_to_mongo(db, data)
    print("Data uploaded successfully.")

if __name__ == "__main__":
    main()
