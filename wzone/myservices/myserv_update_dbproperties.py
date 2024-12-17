from myservices.myserv_connection_mongodb import myserv_connection_mongodb 

class myserv_update_dbproperties:
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

    
    def change_all_fields_to_string(self, collection_name):
        collection = self.dbconnect[collection_name]
        cursor = collection.find()
        for doc in cursor:
            updates = {}
            for field, value in doc.items():
                updates[field] = str(value)
            if updates:
                collection.update_one({"_id": doc["_id"]}, {"$set": updates})
                print(f"Updated document with _id: {doc['_id']}")    


    def mongo_dbconnect_close(self):
        status = self.mongo_db.close_connection()
        return status