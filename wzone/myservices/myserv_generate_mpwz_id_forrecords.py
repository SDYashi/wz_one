from datetime import datetime
from pymongo.errors import PyMongoError 
from myservices.myserv_connection_mongodb import myserv_connection_mongodb 

class myserv_generate_mpwz_id_forrecords:

    def __init__(self):      
        self.mongo_db = myserv_connection_mongodb()  
        self.dbconnect = self.mongo_db.get_connection()        
        self.sequence_collection = self.dbconnect['mpwz_sequences']

        self.collections = self.get_collection_names()
        for collection in self.collections:
            self.initialize_sequence(collection)

    def get_collection_names(self):
        return self.dbconnect.list_collection_names()
        
    def initialize_sequence(self, collection_name):
        if not self.sequence_collection.find_one({'_id': collection_name}):
            self.sequence_collection.insert_one({'_id': collection_name, 'seq': 0})

    def get_next_sequence(self, collection_name):
        try:
            result = self.sequence_collection.find_one_and_update(
                {'_id': collection_name},
                {'$inc': {'seq': 1}},  
                return_document=True
            )
            if not result:
                raise ValueError(f"Sequence for {collection_name} not found.")
            
            new_sequence_number = result['seq']
            return new_sequence_number

        except PyMongoError as e:
            print(f"Error while getting sequence for {collection_name}: {e}")
            self.reset_sequence(collection_name)
            return self.get_next_sequence(collection_name)  

        except Exception as e:
            print(f"Unexpected error: {e}")
            return None  
    
    def reset_sequence(self, collection_name):
        try:
            self.sequence_collection.update_one(
                {'_id': collection_name},
                {'$set': {'seq': 0}}
            )
            print(f"Sequence for {collection_name} reset successfully.")
        except PyMongoError as e:
            print(f"Error resetting sequence for {collection_name}: {e}")

    def set_sequence_to_zero(self, collection_name):
        try:
            self.sequence_collection.update_one(
                {'_id': collection_name},
                {'$set': {'seq': 0}}
            )
            print(f"Sequence for {collection_name} set to 0 successfully.")
        except PyMongoError as e:
            print(f"Error setting sequence for {collection_name} to 0: {e}")

    def mongo_dbconnect_close(self):
        status = self.mongo_db.close_connection()
        return status