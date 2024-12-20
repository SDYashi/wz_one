from flask import Flask, jsonify
from pymongo import MongoClient
from myservices.myserv_connection_mongodb import myserv_connection_mongodb

class myserv_update_dbservices:
    def __init__(self): 
        self.mongo_db = myserv_connection_mongodb()  
        self.dbconnect = self.mongo_db.get_connection() 

    def get_collection_status(self):
        collections = self.dbconnect.list_collection_names()  # Ensure this is called as a method
        total_rows = 0
        total_size_bytes = 0
        collection_stats = {}

        for collection_name in collections:
            stats = self.dbconnect.command("collStats", collection_name)            
            # Get collection row count and size
            row_count = stats['count']
            collection_size_bytes = stats['size']
            
            # Update totals
            total_rows += row_count
            total_size_bytes += collection_size_bytes
            
            # Store collection-wise stats
            collection_stats[collection_name] = {
                "row_count": row_count,
                "size_gb": round(collection_size_bytes / (1024 ** 3), 4)
            }

        total_size_gb = round(total_size_bytes / (1024 ** 3), 4)  # Convert bytes to GB and round to 2 decimal places


        return total_rows, total_size_gb, collection_stats
   
    def mongo_dbconnect_close(self):
        try:
            self.mongo_db.close_connection()
            return "Connection closed successfully."  # Return success message
        except Exception as e:
            print(f"Error while closing connection: {e}")
            return None