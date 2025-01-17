import datetime
import bcrypt
from pymongo import MongoClient
from myservices.myserv_generate_mpwz_id_forrecords import myserv_generate_mpwz_id_forrecords
from myservices.myserv_connection_mongodb import myserv_connection_mongodb

class myserv_update_mpwzintegrationusers_frommpwzusers:

    def __init__(self):     
        self.mongo_db = myserv_connection_mongodb()  
        self.dbconnect = self.mongo_db.get_connection() 
        self.users_collection = self.dbconnect['mpwz_users']
        self.integration_collection = self.dbconnect['mpwz_integration_users']        
        self.seq_gen = myserv_generate_mpwz_id_forrecords()

    def process_users(self):
        # Retrieve usernames and location codes from mpwz_users
        users = self.users_collection.find({}, {'employee_number': 1, 'work_location_code': 1})        
        insert_records=1
        new_users = []
        for user in users:
            username = user.get('employee_number')
            location_code = user.get('work_location_code')

            # Check if username exists in mpwz_integration_appusers
            existing_user = self.integration_collection.find_one({'username': username})
            
            if existing_user is None: 
                common_password = '123456'               
                myseq_mpwz_id =  self.seq_gen.get_next_sequence('mpwz_integration_users')                 
                hashed_password = bcrypt.hashpw(common_password.encode('utf-8'), bcrypt.gensalt()) 
                new_user = {
                    'mpwz_id': myseq_mpwz_id,
                    'user_role':"android_user",  
                    'username': username,  
                    'password': hashed_password,  
                    'work_location_code': location_code,
                    'status': "ACTIVE",
                    'token_app': "ttttttteeeeeesssssstttttttokenapp",
                    'token_issuedon': "2024-12-02T14:01:23",
                    'token_expiredon': "2024-12-02T14:01:23",
                    'created_by': "migration_user",
                    'created_on': str(datetime.datetime.now()),
                    'updated_by': "NA",
                    'updated_on': "NA"
                }
                results = self.integration_collection.insert_one(new_user)                 
                if results:
                    print(f"{insert_records}user created successfully for {username}")
                    insert_records=insert_records+1
                    new_users.append(new_user)
            # else:
            #     print(f"user already created in one app {username}") 
        
        # Return response
        if new_users:
            return {"new_users": new_users,
                    "msg": f"{insert_records} new users created successfully."}
        else:
            return {"msg": "No new user found for id creation."}

    def mongo_dbconnect_close(self):
        status = self.mongo_db.close_connection()
        return status
    
