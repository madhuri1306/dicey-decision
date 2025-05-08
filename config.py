import os

class Config:
    MONGO_URI = "mongodb+srv://hHfRXAiP:R0OxyRjyLh811F5p@us-east-1.ufsuw.mongodb.net/dicey?retryWrites=true&w=majority"
    JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret_key")
    JWT_ALGORITHM = "HS256"