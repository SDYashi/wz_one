# config.py
import os

class Config:
    # MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/flask_db')
    # SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    MONGO_URI= "mongodb://localhost:27017/admin"
    SECRET_KEY= '8ff09627ca698e84a587ccd3ae005f625ece33b3c999062e62dbf6e70c722323'  