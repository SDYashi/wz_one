from pymongo import MongoClient

class MongoCollection:
    def __init__(self, db_name, collection_name, uri="mongodb://localhost:27017/", max_pool_size=50, min_pool_size=10):
       
         # Configure MongoDB with connection pooling
        self.client = MongoClient(uri, maxPoolSize=max_pool_size, minPoolSize=min_pool_size)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_one(self, data):
        try:
            result = self.collection.insert_one(data)
            return result
        except Exception as e:
            print(f"Error inserting data: {e}")
            return None

    def find_one(self, query):
        try:
            result = self.collection.find_one(query)
            return result
        except Exception as e:
            print(f"Error finding data: {e}")
            return None

    def update_one(self, query, update_data):
        try:
            result = self.collection.update_one(query, {"$set": update_data})
            return result
        except Exception as e:
            print(f"Error updating data: {e}")
            return None

    def reset_sequence(self, sequence_name):
        try:
            sequence_collection = self.db['sequences']
            sequence_collection.update_one({"_id": sequence_name}, {"$set": {"value": 0}})
        except Exception as e:
            print(f"Error resetting sequence: {e}")
            return None
