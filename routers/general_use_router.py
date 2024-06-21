from http.client import HTTPResponse
from fastapi import HTTPException, APIRouter
from models.songModels import Song_metadata
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
import json
from dotenv import load_dotenv

general_use_router = APIRouter()


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

client = connect_to_mongo(CONNECTION_STRING)
db = client.valentin_music_db

# Function to get collection (handles creation if needed)
def get_collection(collection_name):
    if collection_name not in db.list_collection_names():
        db.create_collection(collection_name)
    return db[collection_name]


# Endpoint 1: Search for songs (full-text search example)
@general_use_router.post("/search_songs",  tags=["general_use"])
async def search_songs(search_criteria: Song_metadata):
    all_results = []
    for collection_name in db.list_collection_names():
        collection = db[collection_name]
        query = {}
        for field, value in search_criteria.model_dump().items():
            if value:
                query[field] = {"$regex": value, "$options": "i"}  # Case-insensitive regex search
        results = collection.find(query)
        all_results.extend(results)
    return all_results

# Endpoint 2: Get all collections
@general_use_router.get("/collections",  tags=["general_use"])
async def get_collections():
    collections = db.list_collection_names()
    return collections

# Endpoint 3: Add a song document
@general_use_router.post("/add_song",  tags=["general_use"])
async def add_song(song: Song_metadata, collection_name: str):
    collection = get_collection(collection_name)
    collection.insert_one(song.model_dump())
    return {"message": "Song added successfully!"}

