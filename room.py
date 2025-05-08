from pymongo import MongoClient
from config import Config
import secrets
from datetime import datetime
from bson import ObjectId

class Room:
    def __init__(self):
        self.collection = MongoClient(Config.MONGO_URI).dicey.rooms

    def create(self, title, description, max_participants, creator_id):
        room_code = secrets.token_hex(3)[:6]  # Generate a 6-character room code
        room = {
            "title": title,
            "description": description or "",
            "max_participants": max_participants,
            "creator_id": creator_id,
            "room_code": room_code,
            "is_open": True,
            "participants": [ObjectId(creator_id)],
            "created_at": datetime.utcnow()
        }
        result = self.collection.insert_one(room)
        room["_id"] = result.inserted_id
        print(f"Room inserted: room_id={room['_id']}, room_code={room['room_code']}")
        return room

    def find_by_code(self, room_code):
        room = self.collection.find_one({"room_code": room_code})
        if room:
            print(f"Room found in DB: room_code={room_code}, room_id={room['_id']}")
        else:
            print(f"No room found in DB for room_code={room_code}")
        return room

    def find_by_id(self, room_id):
        try:
            room = self.collection.find_one({"_id": ObjectId(room_id)})
            if room:
                print(f"Room found in DB: room_id={room_id}")
            else:
                print(f"No room found in DB for room_id={room_id}")
            return room
        except ValueError:
            print(f"Invalid room_id format: {room_id}")
            raise

    def add_participant(self, room_id, user_id):
        self.collection.update_one(
            {"_id": ObjectId(room_id)},
            {"$addToSet": {"participants": ObjectId(user_id)}}
        )
        print(f"Participant added: user_id={user_id}, room_id={room_id}")