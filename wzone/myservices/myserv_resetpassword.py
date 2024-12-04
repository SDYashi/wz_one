from flask import jsonify
import bcrypt
from myserv_mongodbconnect import myserv_mongodbconnect 

class myserv_resetpassword:
    def __init__(self):     
        mongo_db = myserv_mongodbconnect()  
        dbconnect = mongo_db.get_connection()        
        self.sequence_collection = dbconnect['mpwz_users']

    def set_common_password(self, common_password):
        hashed_password = bcrypt.hashpw(common_password.encode('utf-8'), bcrypt.gensalt()) 
        result = self.sequence_collection.update_many(
            {}, 
            {"$set": {"password": hashed_password}}
        )
        if result.modified_count > 0:
            return {"msg": f"Password set to {common_password} for {result.modified_count} users."}, 200
        else:
            return {"msg": "No users found or password unchanged."}, 404
        
if __name__ == "__main__":
    password_manager = myserv_resetpassword()
    common_password = "123456"  
    response, status_code = password_manager.set_common_password(common_password)
    print(f"response{response} and {status_code}")