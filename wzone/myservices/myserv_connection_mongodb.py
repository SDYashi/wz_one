from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from myservices.myserv_varriable_list import myserv_varriable_list
class myserv_connection_mongodb:
    def __init__(self):
        self.uri = myserv_varriable_list.mongo_config_URI
        self.db_name = myserv_varriable_list.mongo_config_DB
        self.client = None
        self.db = None

    def get_connection(self):
        if self.client is None:
            try:
                self.client = MongoClient(self.uri)
                self.db = self.client[self.db_name]
                # print("MongoDB connection established.")
            except ConnectionFailure as e:
                print(f"Could not connect to MongoDB: {e}")
        return self.db

    def close_connection(self):
        if self.client is not None:
            self.client.close()
            self.client = None
            self.db = None
    
            
