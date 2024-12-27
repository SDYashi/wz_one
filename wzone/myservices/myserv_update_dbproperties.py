from myservices.myserv_connection_mongodb import myserv_connection_mongodb 
# from myserv_connection_mongodb import myserv_connection_mongodb 
class MyServUpdateDBProperties:
    def __init__(self): 
        self.mongo_db = myserv_connection_mongodb()  
        self.dbconnect = self.mongo_db.get_connection() 

    def change_field_type(self, collection_name, field_name, from_property, to_property):
        collection = self.dbconnect[collection_name]
        result = collection.update_many(
            {field_name: {"$type": from_property}},  
            [{"$set": {field_name: {to_property: f"${field_name}"}}}]  
        )
        print(f'Modified {result.modified_count} documents.')

    def change_all_fields_to_string(self, collection_name):
        collection = self.dbconnect[collection_name]
        cursor = collection.find()
        for doc in cursor:
            updates = {}
            for field, value in doc.items():
                if field != "_id":  # Exclude the _id field from updates
                    updates[field] = str(value)
            if updates:
                collection.update_one({"_id": doc["_id"]}, {"$set": updates})
                print(f"Updated document with _id: {doc['_id']}")    

    def mongo_dbconnect_close(self):
        status = self.mongo_db.close_connection()
        return status

def main():
    # Create an instance of the MyServUpdateDBProperties class
    db_updater = MyServUpdateDBProperties()
    
    # Example usage of change_field_type
    collection_name = "mpwz_user_action_history"
    field_name = "mpwz_id"
    from_property = "string"  # e.g., "int"
    to_property = "int"      # e.g., "string"
    
    db_updater.change_field_type(collection_name, field_name, from_property, to_property)
    
    # Example usage of change_all_fields_to_string
    # db_updater.change_all_fields_to_string(collection_name)
    
    # Close the database connection
    db_updater.mongo_dbconnect_close()

if __name__ == "__main__":
    main()