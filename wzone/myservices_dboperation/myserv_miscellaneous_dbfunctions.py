from pymongo import MongoClient
from datetime import datetime
import pytz
import os
import secrets
import subprocess
class MyService:
    def __init__(self, mongo_uri, database_name, collection_name):
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client[database_name]
        self.collection = self.db[collection_name]

    def change_field_type(self, collection_name, field_name, from_property, to_property):
        collection = self.db[collection_name]
        result = collection.update_many(
            {field_name: {"$type": from_property}},  
            [{"$set": {field_name: {to_property: f"${field_name}"}}}]  
        )
        print(f'Modified {result.modified_count} documents.')

    def change_all_fields_to_string(self, collection_name):
        collection = self.db[collection_name]
        cursor = collection.find()
        for doc in cursor:
            updates = {}
            for field, value in doc.items():
                if field != "_id":  # Exclude the _id field from updates
                    updates[field] = str(value)
            if updates:
                collection.update_one({"_id": doc["_id"]}, {"$set": updates})
                print(f"Updated document with _id: {doc['_id']}")    

    def update_notify_datetime(self, new_notify_datetime):
        new_notify_datetime_str = new_notify_datetime.astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S.%f%z")
        result = self.collection.update_many({}, {"$set": {"notify_datetime": new_notify_datetime_str}})
        print(f"Documents updated: {result.modified_count}")

    def update_notify_status(self, notify_status_from, notify_status_to,app_source):
        result = self.collection.update_many(
            {"app_source": app_source, "notify_status": notify_status_from}, 
            {"$set": {"notify_status": str(notify_status_to)}}  
        )
        print(f"Documents updated: {result.modified_count}")

    @staticmethod
    def generate_secret_key():
        return secrets.token_hex(32)

    @staticmethod
    def set_permanent_env_var_windows(var_name, var_value):
        command = f'setx {var_name} "{var_value}"'
        subprocess.run(command, shell=True, check=True)
        print(f"Permanent environment variable '{var_name}' set to '{var_value}'")

    def update_secret_key(self):
        secret_key = self.generate_secret_key()
        self.set_permanent_env_var_windows('JWT_SECRET_KEY', secret_key)
        return secret_key

    def close_connection(self):
        self.mongo_client.close()

def main():
    MONGO_URI = "mongodb://localhost:27017/"
    DATABASE_NAME = "admin"
    COLLECTION_NAME = "mpwz_notifylist"
     # Create an instance of the MyService class
    service = MyService(MONGO_URI, DATABASE_NAME, COLLECTION_NAME)

    # Example usage of change_field_type
    collection_name = "mpwz_user_action_history"
    field_name = "mpwz_id"
    from_property = "string"  
    to_property = "int"     
    # service.change_field_type(collection_name, field_name, from_property, to_property)
    
    # Example usage of change_all_fields_to_string
    # service.change_all_fields_to_string(collection_name)

    # Example usage of update_notify_datetime
    # new_notify_datetime = datetime.fromisoformat("2024-12-27T11:46:40.309+00:00")
    # service.update_notify_datetime(new_notify_datetime)

    # Example usage of update_notify_status
    service.update_notify_status(notify_status_from='APPROVED', 
                                 notify_status_to='PENDING', 
                                 app_source='ngb')

    # Example usage of update_secret_key
    # service.update_secret_key()

    # Close the MongoDB connection
    service.close_connection()

if __name__ == "__main__":
    main()