import datetime
import bcrypt
from pymongo import MongoClient
from myserv_generate_mpwz_id_forrecords import myserv_generate_mpwz_id_forrecords

class myserv_update_mpwzintegrationusers_frommpwzusers:

    def _init_(self, mongo_uri, db_name):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client['admin']
        self.users_collection = self.db['mpwz_users']
        self.integration_collection = self.db['mpwz_integration_users']

    def process_users(self):
        #Retrieve usernames and location codes from mpwz_users
        users = self.users_collection.find({}, {'employee_number': 1, 'work_location_code': 1})
        
        new_users = []
        for user in users:
            username = user.get('employee_number')
            location_code = user.get('work_location_code')

            #  Check if username exists in mpwz_integration_appusers
            existing_user = self.integration_collection.find_one({'username': username})
            
            if existing_user is None: 
                common_password='123456'               
                myseq_mpwz_id = myserv_generate_mpwz_id_forrecords.get_next_sequence('mpwz_users')                 
                hashed_password = bcrypt.hashpw(common_password.encode('utf-8'), bcrypt.gensalt()) 
                new_user = {
                    'mpwz_id': myseq_mpwz_id,
                    'username': existing_user['employee_number'],
                    'password': hashed_password,  
                    'work_location_code':location_code,
                    'status': "ACTIVE",
                    'token_app': "ttttttteeeeeesssssstttttttokenapp",
                    'token_issuedon': "2024-12-02T14:01:23",
                    'token_expiredon': "2024-12-02T14:01:23",
                    'created_by': "migration_user",
                    'created_on':  datetime.datetime.now().isoformat(),
                    'updated_by': "NA",
                    'updated_on': "NA"
                }
                self.integration_collection.insert_one(new_user)
                new_users.append(new_user)
        
        # Step 4: Return response
        if new_users:
            return {"new_users": new_users}
        else:
            return {"message": "No new user found for id creation."}

# Example usage
if __name__ == "__main__":
    user_manager = myserv_update_mpwzintegrationusers_frommpwzusers()
    response = user_manager.process_users()
    print(response)