from pymongo import MongoClient

class myserv_createschema_db:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')

    def add_database(self, db_name):      
        if db_name in self.client.list_database_names():
            print(f"Database with Name '{db_name}' already exists.")
            return False
        else:
            # Create a new database
            self.client[db_name]
            print(f"Database with Name'{db_name}' created.")
            return True

    def add_collections(self, db_name, collection_names):
        db = self.client[db_name]        
        for collection_name in collection_names:
            if collection_name in db.list_collection_names():
                print(f"Collection '{collection_name}' already exists in database '{db_name}'.")
            else:
                # Create a new collection
                db[collection_name]
                print(f"Collection '{collection_name}' created in database '{db_name}'.")    

    def list_databases(self):
        """List all databases."""
        databases = self.client.list_database_names()
        print("Databases:")
        for db in databases:
            print(f"- {db}")
        return databases    

    def list_collections(self, db_name):
        if db_name not in self.client.list_database_names():
            print(f"Database '{db_name}' does not exist.")
            return None
        
        db = self.client[db_name]
        collections = db.list_collection_names()
        print(f"Collections in database '{db_name}':")
        for collection in collections:
            print(f"- {collection}")   
        return collections             

if __name__ == "__main__":
    mongo_handler = myserv_createschema_db()
    database_name = 'my_wzonedb'
    collections_to_create = ['collection1', 'collection2', 'collection3']

    if mongo_handler.add_database(database_name):
        mongo_handler.add_collections(database_name, collections_to_create)

    # List all databases and its collections
    databaselist = mongo_handler.list_databases()
    for database in databaselist:
         mongo_handler.list_collections(database)   
    
  