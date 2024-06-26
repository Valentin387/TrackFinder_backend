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

# here's a function that receives the Song_metadata object and returns a JSON format without the default placeholder fields (0, "string"):
def clean_song_metadata(song_data: Song_metadata) -> dict:
  """
  This function cleans a Song_metadata object by removing fields with default placeholder values.

  Args:
      song_data: The Song_metadata object to be cleaned.

  Returns:
      A dictionary containing only non-default fields from the song data.
  """
  cleaned_data = {}
  for field, value in song_data.model_dump(exclude_unset=True).items():
    # Exclude fields with default values (0 and "string")
    if value not in (0, "string", ""):
      cleaned_data[field] = value
  return cleaned_data


# Function to get collection (handles creation if needed)
def get_collection(collection_name):
    if collection_name not in db.list_collection_names():
        db.create_collection(collection_name)
    return db[collection_name]

proyection_boolean_dict = { "_id": 0, 
                            "bitrate": 0,
                            "commentaries": 0,
                            "track_number": 0,
                            }

# Endpoint 1: Search for songs (full-text search example)
@general_use_router.post("/search_songs",  tags=["general_use"])
async def search_songs(input: Song_metadata):
    try:
        search_criteria = clean_song_metadata(input)
        #------
        all_results = []
        for collection_name in db.list_collection_names():
            collection = db[collection_name]
            results_in_this_collection = []
            
            query = {}
            # Iterate over the search criteria and build the query for every field independently of the others
            for field, value in search_criteria.items():
                query.clear()
                query[field] = {"$regex": value, "$options": "i"}  # Case-insensitive regex search
                results = collection.find(query, proyection_boolean_dict)
                field_results = [dict(result) for result in results]
                if len(field_results)>0:
                    results_in_this_collection.extend(field_results)
            #Hardcoding testing:
            #results = collection.find({"title": { "$regex": "wa", "$options": "i" }}, proyection_boolean_dict)

            # append the results of this collection to the all_results list 
            if len(results_in_this_collection)>0:
                all_results.append({ collection_name :results_in_this_collection})
        # return all the results
        return all_results
    except Exception as e:
        return {"message": f"An error occurred: {str(e)}"}

# Endpoint 2: Get all collections
@general_use_router.get("/collections",  tags=["general_use"])
async def get_collections():
    try:
        collections = db.list_collection_names()
        return collections
    except Exception as e:
        return {"message": f"An error occurred: {str(e)}"}

# Endpoint 3: Add a song document
@general_use_router.post("/add_song",  tags=["general_use"])
async def add_song(song: Song_metadata, collection_name: str):
    try:
        collection = get_collection(collection_name)
        collection.insert_one(song.model_dump())
        return {"message": "Song added successfully!"}
    except Exception as e:
        return {"message": f"An error occurred: {str(e)}"}

