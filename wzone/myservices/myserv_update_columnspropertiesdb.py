from sqlite3 import Binary
from myservices.myserv_connection_mongodb import myserv_connection_mongodb 

class myserv_updatedbproperties:
    def __init__(self): 
            self.mongo_db = myserv_connection_mongodb()  
            self.dbconnect = self.mongo_db.get_connection() 

    def change_field_type(self, collection_name, field_name, from_property, to_property):
        collection = self.dbconnect[collection_name]

        # Define the MongoDB type conversion based on from_property and to_property
        if from_property == "string" and to_property == "int":
            # Convert string to int
            result = collection.update_many(
                {field_name: {"$type": "string"}},  
                [{"$set": {field_name: {"$toInt": f"${field_name}"}}}]  
            )
        elif from_property == "int" and to_property == "string":
            # Convert int to string
            result = collection.update_many(
                {field_name: {"$type": "int"}}, 
                [{"$set": {field_name: {"$toString": f"${field_name}"}}}] 
            )
        else:
            raise ValueError("Unsupported conversion from {} to {}".format(from_property, to_property))
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

