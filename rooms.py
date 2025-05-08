from flask import Blueprint, request, jsonify
from models.room import Room
from utils.jwt_utils import verify_token
from bson import ObjectId

rooms_bp = Blueprint("rooms", __name__)

@rooms_bp.route("/create", methods=["POST"])
def create_room():
    # Get and preprocess the Authorization header
    auth_header = request.headers.get("Authorization")
    print(f"Authorization header: {auth_header}")
    
    if not auth_header:
        print("No Authorization header provided")
        return jsonify({"error": "Authorization header required"}), 401
    
    # Strip 'Bearer' prefix if present
    token = auth_header.replace("Bearer ", "").strip()
    print(f"Processed token: {token}")
    
    # Basic token validation (JWT should have 3 segments: header.payload.signature)
    if len(token.split(".")) != 3:
        print(f"Invalid token format: {token}")
        return jsonify({"error": "Invalid token format"}), 401
    
    try:
        user_id = verify_token(token)
        print(f"Verified user_id: {user_id}")
    except Exception as e:
        print(f"Token verification failed: {str(e)}")
        return jsonify({"error": f"Invalid token: {str(e)}"}), 401

    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    max_participants = data.get("max_participants", 10)

    if not title:
        print("Missing title in request")
        return jsonify({"error": "Title is required"}), 400

    room_model = Room()  # Instantiate Room class
    room = room_model.create(title, description, max_participants, user_id)
    print(f"Room created: room_id={room['_id']}, room_code={room['room_code']}")
    return jsonify({
        "room_id": str(room["_id"]),
        "room_code": room["room_code"],
        "invite_link": f"/join/{room['room_code']}"
    }), 201

@rooms_bp.route("/join/<room_code>", methods=["POST"])
def join_room(room_code):
    print(f"Join room attempt: room_code={room_code}")
    
    token = request.headers.get("Authorization")
    print(f"Authorization header: {token}")
    if not token:
        print("No Authorization header provided")
        return jsonify({"error": "Authorization header required"}), 401
    
    token = token.replace("Bearer ", "").strip()
    print(f"Processed token: {token}")
    if len(token.split(".")) != 3:
        print(f"Invalid token format: {token}")
        return jsonify({"error": "Invalid token format"}), 401
    
    try:
        user_id = verify_token(token)
        print(f"Verified user_id: {user_id}")
    except Exception as e:
        print(f"Token verification failed: {str(e)}")
        return jsonify({"error": f"Invalid token: {str(e)}"}), 401

    room_model = Room()  # Instantiate Room class
    room = room_model.find_by_code(room_code)
    if not room:
        print(f"Room not found for room_code={room_code}")
        return jsonify({"error": "Room not found"}), 404

    print(f"Room found: room_id={room['_id']}, room_code={room['room_code']}")
    
    if not room["is_open"]:
        print(f"Room is closed: room_id={room['_id']}")
        return jsonify({"error": "Room is closed"}), 400

    if len(room["participants"]) >= room["max_participants"]:
        print(f"Room is full: room_id={room['_id']}, participants={len(room['participants'])}")
        return jsonify({"error": "Room is full"}), 400

    if ObjectId(user_id) in room["participants"]:
        print(f"User already in room: user_id={user_id}, room_id={room['_id']}")
        return jsonify({"error": "User already in room"}), 400

    room_model.add_participant(room["_id"], user_id)
    print(f"User joined room: user_id={user_id}, room_id={room['_id']}")
    return jsonify({"message": "Joined room", "room_id": str(room["_id"])}), 200