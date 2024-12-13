from pymongo import MongoClient

from myservices.myserv_connection_mongodb import myserv_connection_mongodb
class MongoCollection:
    def __init__(self, collection_name): 
        self.mongo_db = myserv_connection_mongodb()  
        self.dbconnect = self.mongo_db.get_connection()     
        # self.client = MongoClient("mongodb://localhost:27017/", maxPoolSize=50, minPoolSize=10)
        # self.db = self.client['admin']
        self.collection = self.dbconnect[collection_name]

    def insert_one(self, data):
        try:
            result = self.collection.insert_one(data)
            if result:
                # Convert ObjectId to string
                result['_id'] = str(result['_id'])
            return result
        except Exception as e:
            print(f"Error while inserting data: {e}")
            return None

    def insert_many(self, data):
        try:
            result = self.collection.insert_many(data)
            if result:
                # Convert ObjectId to string
                result = [str(id) for id in result.inserted_ids]
            return result
        except Exception as e:
            print(f"Error while inserting data: {e}")
            return None

    def find_one(self, query):
        try:
            result = self.collection.find_one(query)
            if result:
                # Convert ObjectId to string
                result['_id'] = str(result['_id'])
            return result
        except Exception as e:
            print(f"Error while finding data: {e}")
            return None

    def find(self, query):
        try:
            result = self.collection.find(query)
            if result:
                # Convert ObjectId to string
                result = [{**item, '_id': str(item['_id'])} for item in result]
            return result
        except Exception as e:
            print(f"Error while finding data: {e}")
            return None

    def find_all(self):
        try:
            result = self.collection.find()
            if result:
                # Convert ObjectId to string
                result = [{**item, '_id': str(item['_id'])} for item in result]
            return result
        except Exception as e:
            print(f"Error while finding data: {e}")
            return None
    def find_distinct(self, field):
            try:
                result = self.collection.distinct(field)
                return result
            except Exception as e:
                print(f"Error while finding distinct values: {e}")
                return None   

    def update_one(self, query, update_data):
        try:
            result = self.collection.update_one(query, {"$set": update_data})
            if result:
                # Convert ObjectId to string
                result['_id'] = str(result['_id'])
            return result
        except Exception as e:
            print(f"Error while updating data: {e}")
            return None

    def update_many(self, query, update_data):
        try:
            result = self.collection.update_many(query, {"$set": update_data})
            if result:
                # Convert ObjectId to string
                result['_id'] = str(result['_id'])
            return result
        except Exception as e:
            print(f"Error while updating data: {e}")
            return None

    def delete_one(self, query):
        try:
            result = self.collection.delete_one(query)
            if result:
                # Convert ObjectId to string
                result['_id'] = str(result['_id'])
            return result
        except Exception as e:
            print(f"Error while deleting data: {e}")
            return None

    def delete_many(self, query):
        try:
            result = self.collection.delete_many(query)
            if result:
                # Convert ObjectId to string
                result['_id'] = str(result['_id'])
            return result
        except Exception as e:
            print(f"Error while deleting data: {e}")
            return None

    def count_documents(self, query):
        try:
            result = self.collection.count_documents(query)
            return result
        except Exception as e:
            print(f"Error while counting documents: {e}")
            return None

    def aggregate(self, pipeline):
        try:
            result = self.collection.aggregate(pipeline)
            if result:
                # Convert ObjectId to string
                result = [{**item, '_id': str(item['_id'])} for item in result]
            return result
        except Exception as e:
            print(f"Error while aggregating data: {e}")
            return None

    def create_index(self, key_or_list, unique=False):
        try:
            result = self.collection.create_index(key_or_list, unique=unique)
            return result
        except Exception as e:
            print(f"Error while creating index: {e}")
            return None

    def drop_index(self, index_or_name):
        try:
            result = self.collection.drop_index(index_or_name)
            return result
        except Exception as e:
            print(f"Error while dropping index: {e}")
            return None

    def drop_collection(self):
        try:
            result = self.collection.drop()
            return result
        except Exception as e:
            print(f"Error while dropping collection: {e}")
            return None

    def rename_collection(self, new_name):
        try:
            result = self.collection.rename(new_name)
            return result
        except Exception as e:
            print(f"Error while renaming collection: {e}")
            return None

    def create_collection(self, collection_name):
        try:
            result = self.dbconnect.create_collection(collection_name)
            return result
        except Exception as e:
            print(f"Error while creating collection: {e}")
            return None

    def drop_database(self):
        try:
            result = self.dbconnect.drop()
            return result
        except Exception as e:
            print(f"Error while dropping database: {e}")
            return None

    def list_collections(self):
        try:
            result = self.dbconnect.list_collection_names()
            return result
        except Exception as e:
            print(f"Error while listing collections: {e}")
            return None

    def list_databases(self):
        try:
            result = self.dbconnect.client.list_database_names()
            return result
        except Exception as e:
            print(f"Error while listing databases: {e}")
            return None

    def reset_sequence(self, sequence_name):
        try:
            sequence_collection = self.dbconnect['sequences']
            sequence_collection.update_one({"_id": sequence_name}, {"$set": {"value": 0}})
        except Exception as e:
            print(f"Error while resetting sequence: {e}")
            return None

    def mongo_dbconnect_close(self):
        status = self.mongo_db.close_connection()
        return status