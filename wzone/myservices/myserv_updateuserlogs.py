import datetime
import json
from urllib import request
from pymongo import MongoClient 
from myservices.myserv_mongodbconnect import myserv_mongodbconnect
from myservices.myserv_jsonresponse_merger import myserv_jsonresponse_merger 
class myserv_updateuserlogs:
    def __init__(self):  
        mongo_db = myserv_mongodbconnect()  
        dbconnect = mongo_db.get_connection() 
        self.collection = dbconnect['mpwz_users_logs']  
        self.api_call_history = [] 

    def log_api_call(self, response_data):
        self.collection.insert_one(response_data)
        self.api_call_history.append(response_data)
        print("API Calling:",response_data,"\n")

    def get_current_datetime(self):
        now =  datetime.datetime.now().isoformat()
        return now  


