from  myservices.myserv_connection_mongodb import myserv_connection_mongodb

class MongoCollection:
    def __init__(self, collection_name): 
        self.mongo_db = myserv_connection_mongodb()  
        self.dbconnect = self.mongo_db.get_connection() 
        self.collection = self.dbconnect[collection_name]

    def insert_one(self, data):
        try:
            result = self.collection.insert_one(data)
            print(f"Insert result: {result}")  # Debugging
            return result  # Return the raw result
        except Exception as e:
            print(f"Error while inserting data: {e}")
            return None

    def insert_many(self, data):
        try:
            result = self.collection.insert_many(data)
            print(f"Insert many result: {result.inserted_ids}")  # Debugging
            return result  # Return the raw result
        except Exception as e:
            print(f"Error while inserting data: {e}")
            return None

    def find_one(self, query):
        try:
            result = self.collection.find_one(query)
            return result  # Return the raw result
        except Exception as e:
            print(f"Error while finding data: {e}")
            return None

    def find(self, query):
        try:
            result = self.collection.find(query)
            return list(result)  # Return the raw cursor
        except Exception as e:
            print(f"Error while finding data: {e}")
            return None

    def find_all(self):
        try:
            result = self.collection.find()
            return list(result)  # Return the raw cursor
        except Exception as e:
            print(f"Error while finding data: {e}")
            return None

    def find_distinct(self, field):
        try:
            result = self.collection.distinct(field)
            return result  # Return the raw result
        except Exception as e:
            print(f"Error while finding distinct values: {e}")
            return None   

    def update_one(self, query, update_data):
        try:
            result = self.collection.update_one(query, {"$set": update_data})
            return result  # Return the raw result
        except Exception as e:
            print(f"Error while updating data: {e}")
            return None

    def update_many(self, query, update_data):
        try:
            result = self.collection.update_many(query, {"$set": update_data})
            return result  # Return the raw result
        except Exception as e:
            print(f"Error while updating data: {e}")
            return None

    def delete_one(self, query):
        try:
            result = self.collection.delete_one(query)
            return result  # Return the raw result
        except Exception as e:
            print(f"Error while deleting data: {e}")
            return None

    def delete_many(self, query):
        try:
            result = self.collection.delete_many(query)
            return result  # Return the raw result
        except Exception as e:
            print(f"Error while deleting data: {e}")
            return None

    def count_documents(self, query):
        try:
            result = self.collection.count_documents(query)
            return result  # Return the raw result
        except Exception as e:
            print(f"Error while counting documents: {e}")
            return None

    def aggregate(self, pipeline):
        try:
            result = self.collection.aggregate(pipeline)
            return list(result)  # Return the raw cursor
        except Exception as e:
            print(f"Error while aggregating data: {e}")
            return None

    def create_index(self, key_or_list, unique=False):
        try:
            result = self.collection.create_index(key_or_list, unique=unique)
            return result  # Return the raw result
        except Exception as e:
            print(f"Error while creating index: {e}")
            return None

    def drop_index(self, index_or_name):
        try:
            result = self .collection.drop_index(index_or_name)
            return result  # Return the raw result
        except Exception as e:
            print(f"Error while dropping index: {e}")
            return None

    def drop_collection(self):
        try:
            result = self.collection.drop()
            return result  # Return the raw result
        except Exception as e:
            print(f"Error while dropping collection: {e}")
            return None

    def rename_collection(self, new_name):
        try:
            self.dbconnect[self.collection.name].rename(new_name)
            return f"Collection renamed to {new_name}"  # Return success message
        except Exception as e:
            print(f"Error while renaming collection: {e}")
            return None

    def mongo_dbconnect_close(self):
        try:
            self.dbconnect.close()
            return "Connection closed successfully."  # Return success message
        except Exception as e:
            print(f"Error while closing connection: {e}")
            return None

    def create_database(self, db_name):
        try:
            new_db = self.mongo_db.client[db_name]  # Create a new database
            return f"Database '{db_name}' created successfully."
        except Exception as e:
            print(f"Error while creating database: {e}")
            return None

    def drop_database(self, db_name):
        try:
            self.mongo_db.client.drop_database(db_name)  # Drop the specified database
            return f"Database '{db_name}' dropped successfully."
        except Exception as e:
            print(f"Error while dropping database: {e}")
            return None

    def bulk_write(self, operations):
        try:
            result = self.collection.bulk_write(operations)
            return result  # Return the raw result
        except Exception as e:
            print(f"Error while performing bulk write: {e}")
            return None

    def find_one_and_update(self, query, update_data):
        try:
            result = self.collection.find_one_and_update(query, {"$set": update_data})
            return result  # Return the raw result
        except Exception as e:
            print(f"Error while finding and updating data: {e}")
            return None

    def find_one_and_replace(self, query, replacement):
        try:
            result = self.collection.find_one_and_replace(query, replacement)
            return result  # Return the raw result
        except Exception as e:
            print(f"Error while finding and replacing data: {e}")
            return None

    def find_one_and_delete(self, query):
        try:
            result = self.collection.find_one_and_delete(query)
            return result  # Return the raw result
        except Exception as e:
            print(f"Error while finding and deleting data: {e}")
            return None

    def list_collections(self):
        try:
            collections = self.dbconnect.list_collection_names()
            return collections  # Return the list of collections
        except Exception as e:
            print(f"Error while listing collections: {e}")
            return None

    def get_collection_stats(self):
        try:
            stats = self.dbconnect.command("collStats", self.collection.name)
            return stats  # Return the collection statistics
        except Exception as e:
            print(f"Error while getting collection stats: {e}")
            return None