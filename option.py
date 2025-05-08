from pymongo import MongoClient
from config import Config
from bson import ObjectId
from datetime import datetime

class Option:
    def __init__(self):
        self.collection = MongoClient(Config.MONGO_URI).dicey.options

    def create(self, room_id, option_text, creator_id):
        option = {
            "room_id": ObjectId(room_id),
            "option_text": option_text,
            "creator_id": ObjectId(creator_id),
            "created_at": datetime.utcnow(),
            "votes": []
        }
        result = self.collection.insert_one(option)
        option["_id"] = result.inserted_id
        print(f"Option inserted: option_id={option['_id']}, room_id={room_id}")
        return option