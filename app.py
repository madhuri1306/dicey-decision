from flask import Flask
from pymongo import MongoClient
from config import Config
from routes.auth import auth_bp
from routes.rooms import rooms_bp
from routes.options import options_bp
from routes.votes import votes_bp

app = Flask(__name__)

# MongoDB setup
client = MongoClient(Config.MONGO_URI)
db = client.dicey

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(rooms_bp, url_prefix="/api/rooms")
app.register_blueprint(options_bp, url_prefix="/api/options")
app.register_blueprint(votes_bp, url_prefix="/api/votes")

@app.route("/")
def health_check():
    return {"status": "API is running"}

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)