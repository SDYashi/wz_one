# myservices/ip_service.py

from flask import request, jsonify
from pymongo import MongoClient
from myservices.myserv_connection_mongodb import myserv_connection_mongodb

class myserv_ip_service:
    def __init__(self):    
        self.mongo_db = myserv_connection_mongodb()  
        self.dbconnect = self.mongo_db.get_connection()  
        self.ip_collection = self.dbconnect['mpwz_iplist_adminpanel']

    def get_allowed_ips(self):
        # Fetch allowed IPs from MongoDB
        allowed_ips = self.ip_collection.find({}, {"_id": 0, "ip_address": 1})
        return {ip['ip_address'] for ip in allowed_ips}

    def ip_required(self, f):
        def wrapper(*args, **kwargs):
            allowed_ips = self.get_allowed_ips()
            client_ip = request.remote_addr
            
            if client_ip not in allowed_ips:
                return jsonify({"error": "Forbidden: Your IP address is not allowed."}), 403
            
            return f(*args, **kwargs)
        return wrapper
    
    def insert_user_info(self, user_info):
        # Insert user information into the collection
        result = self.ip_collection.insert_one(user_info)
        return str(result.inserted_id)      