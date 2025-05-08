from bson import ObjectId
from pymongo import MongoClient
from config import Config
from datetime import datetime  # Add this import

client = MongoClient(Config.MONGO_URI)
db = client.dicey

class User:
    collection = db.users

    @staticmethod
    def create(email, password_hash):
        return User.collection.insert_one({
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.utcnow()
        })

    @staticmethod
    def find_by_email(email):
        return User.collection.find_one({"email": email})

    @staticmethod
    def find_by_id(user_id):
        return User.collection.find_one({"_id": ObjectId(user_id)})