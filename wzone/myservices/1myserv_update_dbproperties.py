from sqlite3 import Binary
from myservices.myserv_connection_mongodb import myserv_connection_mongodb 

class myserv_updatedbproperties:
    def __init__(self): 
            self.mongo_db = myserv_connection_mongodb()  
            self.dbconnect = self.mongo_db.get_connection() 

    def change_field_type(self, collection_name, field_name):
        collection = self.dbconnect[collection_name]
        result = collection.update_many(
            {field_name: {"$type": "int"}},  
            [{"$set": {field_name: {"$toString": f"${field_name}"}}}]  
        )
        print(f'Modified {result.modified_count} documents.')
        
    def change_field_type_to_binary(self, collection_name, field_name):
        collection = self.dbconnect[collection_name]
        result = collection.update_many(
            {field_name: {"$type": "string"}},  # Find documents where the field is a string
            [{"$set": {field_name: Binary(f"${field_name}".encode('utf-8'))}}]  # Convert to Binary
        )
        
        print(f'Modified {result.modified_count} documents.')
    
    # def change_all_fields_to_string(self, collection_name):
    #     collection = self.dbconnect[collection_name]
    #     cursor = collection.find()
    #     for doc in cursor:
    #         updates = {}
    #         for field, value in doc.items():
    #             updates[field] = str(value)
    #         if updates:
    #             collection.update_one({"_id": doc["_id"]}, {"$set": updates})
    #             print(f"Updated document with _id: {doc['_id']}")    

if __name__ == "__main__":
    db_updater = myserv_updatedbproperties()
    # db_updater.change_field_type(collection_name='mpwz_integration_users', field_name='employee_number')
    db_updater.change_field_type_to_binary('mpwz_integration_users', 'password')
    # db_updater.change_all_fields_to_string(collection_name='mpwz_users')