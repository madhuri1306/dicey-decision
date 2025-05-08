from bson import ObjectId
from pymongo import MongoClient
from config import Config
from datetime import datetime  # Add this import

client = MongoClient(Config.MONGO_URI)
db = client.dicey

class Vote:
    collection = db.votes

    @staticmethod
    def create(room_id, user_id, option_id):
        vote = {
            "room_id": ObjectId(room_id),
            "user_id": ObjectId(user_id),
            "option_id": ObjectId(option_id),
            "created_at": datetime.utcnow()
        }
        result = Vote.collection.insert_one(vote)
        return Vote.collection.find_one({"_id": result.inserted_id})

    @staticmethod
    def find_by_room(room_id):
        return list(Vote.collection.find({"room_id": ObjectId(room_id)}))

    @staticmethod
    def has_voted(room_id, user_id):
        return Vote.collection.find_one({
            "room_id": ObjectId(room_id),
            "user_id": ObjectId(user_id)
        }) is not None