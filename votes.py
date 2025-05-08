from flask import Blueprint, request, jsonify
from models.room import Room
from models.option import Option
from models.vote import Vote
from utils.jwt_utils import verify_token
from utils.random_utils import resolve_tie
from bson import ObjectId
from collections import Counter

votes_bp = Blueprint("votes", __name__)

@votes_bp.route("/<room_id>/vote", methods=["POST"])
def submit_vote(room_id):
    token = request.headers.get("Authorization")
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    room = Room.find_by_id(room_id)
    if not room or ObjectId(user_id) not in room["participants"]:
        return jsonify({"error": "Unauthorized or room not found"}), 403
    
    if not room["is_open"]:
        return jsonify({"error": "Voting is closed"}), 400
    
    if Vote.has_voted(room_id, user_id):
        return jsonify({"error": "Already voted"}), 400
    
    data = request.get_json()
    option_id = data.get("option_id")
    
    option = Option.collection.find_one({"_id": ObjectId(option_id), "room_id": ObjectId(room_id)})
    if not option:
        return jsonify({"error": "Invalid option"}), 400
    
    Vote.create(room_id, user_id, option_id)
    Room.update_last_activity(room_id)
    return jsonify({"message": "Vote recorded"}), 200

@votes_bp.route("/<room_id>/results", methods=["GET"])
def get_results(room_id):
    token = request.headers.get("Authorization")
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    room = Room.find_by_id(room_id)
    if not room or ObjectId(user_id) not in room["participants"]:
        return jsonify({"error": "Unauthorized or room not found"}), 403
    
    if room["is_open"]:
        return jsonify({"error": "Voting is still open"}), 400
    
    votes = Vote.find_by_room(room_id)
    vote_counts = Counter(vote["option_id"] for vote in votes)
    
    options = Option.find_by_room(room_id)
    results = []
    max_votes = max(vote_counts.values(), default=0)
    tied_options = []
    
    for opt in options:
        count = vote_counts.get(opt["_id"], 0)
        results.append({
            "option_id": str(opt["_id"]),
            "text": opt["text"],
            "votes": count
        })
        if count == max_votes and max_votes > 0:
            tied_options.append(opt)
    
    return jsonify({
        "results": results,
        "tied": len(tied_options) > 1
    }), 200

@votes_bp.route("/<room_id>/tiebreaker", methods=["POST"])
def tiebreaker(room_id):
    token = request.headers.get("Authorization")
    user_id = verify_token(token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    room = Room.find_by_id(room_id)
    if not room or str(room["creator_id"]) != user_id:
        return jsonify({"error": "Unauthorized or room not found"}), 403
    
    if room["is_open"]:
        return jsonify({"error": "Voting is still open"}), 400
    
    data = request.get_json()
    method = data.get("method")  # dice, spinner, coin
    
    votes = Vote.find_by_room(room_id)
    vote_counts = Counter(vote["option_id"] for vote in votes)
    max_votes = max(vote_counts.values(), default=0)
    
    tied_option_ids = [opt_id for opt_id, count in vote_counts.items() if count == max_votes]
    tied_options = [opt for opt in Option.find_by_room(room_id) if opt["_id"] in tied_option_ids]
    
    if len(tied_options) <= 1:
        return jsonify({"error": "No tie to resolve"}), 400
    
    winner = resolve_tie(tied_options, method)
    return jsonify({
        "winner": {
            "option_id": str(winner["_id"]),
            "text": winner["text"]
        },
        "method": method
    }), 200