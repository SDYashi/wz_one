import datetime
import json
from urllib import request
from myservices.myserv_connection_mongodb import myserv_connection_mongodb
class myserv_update_users_api_logs:
    def __init__(self):  
        mongo_db = myserv_connection_mongodb('admin')  
        dbconnect = mongo_db.get_connection() 
        self.collection = dbconnect['mpwz_users_api_logs']  
        self.history = []
        
    def log_api_call_status(self, api_name, request_time, response_time, server_load, success):
        api_call_record = {
            'api_name': api_name,
            'request_time': request_time,
            'response_time': response_time,
            'server_load': server_load,
            'success': success,
            'timestamp': datetime.datetime.now().isoformat()
        }
        print("qpi response status :-",api_call_record)
        result = self.collection.insert_one(api_call_record)
        if result:
              self.history.append(api_call_record)
        else:
             print("something went while updating api status in db")      

    def calculate_server_load(self):
        return len(self.history) * 0.1  

    def get_history(self):
        return self.history


