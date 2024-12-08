from flask import jsonify
import bcrypt
from wzone.myservices.myserv_connection_mongodb import myserv_connection_mongodb 

class myserv_resetpassword:
    def __init__(self):     
        mongo_db = myserv_connection_mongodb()  
        dbconnect = mongo_db.get_connection()        
        self.sequence_collection = dbconnect['mpwz_users']

    def changepasswordfor_all(self, common_password):
        hashed_password = bcrypt.hashpw(common_password.encode('utf-8'), bcrypt.gensalt()) 
        result = self.sequence_collection.update_many(
            {}, 
            {"$set": {"password": hashed_password}}
        )
        if result.modified_count > 0:
            return {"msg": f"Password set to {common_password} for {result.modified_count} users."}, 200
        else:
            return {"msg": "No users found or password unchanged."}, 404

    def changepasswordfor_user(self, user,password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) 
        # Update the password for single user
        result = self.sequence_collection.update_one(
            {"username": username}, 
            {"$set": {"password": hashed_password}}
        )
        if result.modified_count > 0:
            return {"msg": f"Password changed successfully for {user}"}, 200
        else:
            return {"msg": "user not found or password unchanged."}, 404
          
if __name__ == "__main__":
    password_manager = myserv_resetpassword()
    username = "34480244"  
    password = "123456"  
    response, status_code = password_manager.changepasswordfor_all(password)
    print(f"response{response} and {status_code}")
    response, status_code = password_manager.changepasswordfor_user(username,password)
    print(f"response{response} and {status_code}")