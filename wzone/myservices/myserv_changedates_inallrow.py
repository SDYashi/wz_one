from pymongo import MongoClient
from datetime import datetime
import pytz

# MongoDB connection details
MONGO_URI = "mongodb://localhost:27017/"  
DATABASE_NAME = "admin"      
COLLECTION_NAME = "mpwz_notifylist"   

# Create a MongoDB client
client = MongoClient(MONGO_URI)

# Access the database and collection
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Define the new notify_datetime value
new_notify_datetime = datetime.fromisoformat("2024-12-27T11:46:40.309+00:00")

# Update all documents in the collection
result = collection.update_many({}, {"$set": {"notify_datetime": str(new_notify_datetime)}})

# Print the number of documents updated
print(f"Documents updated: {result.modified_count}")

result1 = collection.update_many({}, {"$set": {"notify_refsys_updatedon": str(new_notify_datetime)}})
# Print the number of documents updated
print(f"Documents updated1: {result1.modified_count}")

# Close the MongoDB client
client.close()