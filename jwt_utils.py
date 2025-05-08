import jwt
from datetime import datetime, timedelta
from config import Config

def generate_token(user_id):
    try:
        payload = {
            "user_id": str(user_id),
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)
        print(f"Generated JWT token for user_id {user_id}: {token}")
        return token
    except Exception as e:
        print(f"Error generating JWT token: {str(e)}")
        raise

def verify_token(token):
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        print("Token verification failed: Token expired")
        raise
    except jwt.InvalidTokenError:
        print("Token verification failed: Invalid token")
        raise