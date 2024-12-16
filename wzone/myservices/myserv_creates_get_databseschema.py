from pymongo import MongoClient
# from myserv_connection_mongodb import myserv_connection_mongodb
from myservices.myserv_connection_mongodb import myserv_connection_mongodb

class myserv_createschema_db:
    def __init__(self):
        self.client = myserv_connection_mongodb()

    def add_database(self, db_name):      
        if db_name in self.client.list_database_names():
            return {"message": f"Database with Name '{db_name}' already exists."}, 400
        else:
            return {"message": f"Database with Name '{db_name}' created."}, 201

    def add_collections(self, db_name, collection_names):
        db = self.client[db_name]
        created_collections = []
        for collection_name in collection_names:
            if collection_name in db.list_collection_names():
                continue
            else:
                db[collection_name]
                created_collections.append(collection_name)
        if created_collections:
            return {"message": f"Collections created: {', '.join(created_collections)}"}, 201
        else:
            return {"message": "No new collections created, all already exist."}, 200

    def list_databases(self):
        databases = self.client.list_database_names()
        return {"databases": databases}, 200

    def list_collections(self, db_name):
        if db_name not in self.client.list_database_names():
            return {"message": f"Database '{db_name}' does not exist."}, 404
        
        db = self.client[db_name]
        collections = db.list_collection_names()
        return {"collections": collections}, 200
    

{
  "db_name": "my_wzonedb",
  "collections": [
            "mpwz_buttons",
            'mpwz_collections_id',
            'mpwz_integrated_app',
            'mpwz_integration_users',
            "mpwz_ngb_usersprofiles",
            "mpwz_notify_status",
            "mpwz_notifylist",
            "mpwz_offices",
            "mpwz_sequences",
            "mpwz_user_action_history",
            "mpwz_users",
            "mpwz_users_api_logs",
            "mpwz_users_logs",
  ]
}