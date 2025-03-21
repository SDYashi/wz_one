import datetime
import json
from urllib import request
from myservices_oneapp.myserv_connection_mongodb import myserv_connection_mongodb
class myserv_update_users_logs:
    def __init__(self):  
        self.mongo_db = myserv_connection_mongodb()  
        self.dbconnect = self.mongo_db.get_connection() 
        self.collection = self.dbconnect['mpwz_users_logs']  
        self.api_call_history = [] 

    def log_api_call(self, response_data):
        self.collection.insert_one(response_data)
        self.api_call_history.append(response_data)
        # print("users log:-",response_data)

    def get_current_datetime(self):
        now =  str(datetime.datetime.now())
        return now  

    def mongo_dbconnect_close(self):
        status = self.mongo_db.close_connection()
        return status 


