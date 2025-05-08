from flask import Blueprint, request, jsonify
from models.user import User
import bcrypt
from utils.jwt_utils import generate_token
from bson import ObjectId

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    
    existing_user = User.find_by_email(email)
    if existing_user:
        return jsonify({"error": "Email already exists"}), 400
    
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    User.create(email, password_hash)
    return jsonify({"message": "User created"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    user = User.find_by_email(email)
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"]):
        return jsonify({"error": "Invalid credentials"}), 401
    
    token = generate_token(user["_id"])
    return jsonify({"token": token, "user_id": str(user["_id"])}), 200