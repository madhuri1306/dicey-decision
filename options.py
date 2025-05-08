from flask import Blueprint, request, jsonify
from models.room import Room
from models.option import Option
from utils.jwt_utils import verify_token
from bson import ObjectId

options_bp = Blueprint("options", __name__)

@options_bp.route("/create", methods=["POST"])
def create_option():
    print("Create option attempt")
    
    # Get and preprocess the Authorization header
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

    data = request.get_json()
    room_id = data.get("room_id")
    option_text = data.get("option_text")

    if not room_id or not option_text:
        print(f"Missing room_id or option_text: room_id={room_id}, option_text={option_text}")
        return jsonify({"error": "room_id and option_text are required"}), 400

    # Verify room exists and is open
    room_model = Room()
    try:
        room = room_model.find_by_id(room_id)
    except ValueError:
        print(f"Invalid room_id format: {room_id}")
        return jsonify({"error": "Invalid room_id format"}), 400
        
    if not room:
        print(f"Room not found for room_id={room_id}")
        return jsonify({"error": "Room not found"}), 404
    
    if not room["is_open"]:
        print(f"Room is closed: room_id={room['_id']}")
        return jsonify({"error": "Room is closed"}), 400

    # Verify user is a participant
    if ObjectId(user_id) not in room["participants"]:
        print(f"User not in room: user_id={user_id}, room_id={room['_id']}")
        return jsonify({"error": "User not in room"}), 403

    # Create option
    option_model = Option()
    option = option_model.create(room_id, option_text, user_id)
    print(f"Option created: option_id={option['_id']}, room_id={room_id}")
    
    return jsonify({
        "option_id": str(option["_id"]),
        "option_text": option["option_text"],
        "room_id": str(option["room_id"])
    }), 201