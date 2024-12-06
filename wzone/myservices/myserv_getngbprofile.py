from flask import Flask, jsonify 
from myservices.myserv_mongodbconnect import myserv_mongodbconnect 

app = Flask(__name__)
class myserv_getngbprofile:
    def __init__(self):
        try:    
            mongo_db = myserv_mongodbconnect()  
            dbconnect = mongo_db.get_connection() 
            self.usersprofiles_collection = dbconnect['mpwz_ngb_usersprofiles']
            self.offices_collection = dbconnect['mpwz_offices']
            self.user_collection = dbconnect['mpwz_users']
        except Exception as e:
            print(f"Unexpected error while setting up MongoDB: {e}")
            raise

    def get_user_info(self, username):
        try:
            # Get role and location_code from mpwz_ngb_usersprofiles
            user_profile = self.usersprofiles_collection.find_one({'username': username, 'status': 'ACTIVE'})
            if not user_profile:
                return None  
            else:
                role = user_profile.get('role')
                location_code = user_profile.get('location_code')
                print('ngb user role & primary location code:-', role, "-", location_code)
                
                if role == 'oic':
                    office_info = self.offices_collection.find_one({'location_code': location_code})
                    if office_info:
                        location_code = office_info.get('location_code')
                        user_info = self.user_collection.find_one({'work_location_code': location_code, 'role_type': 'oic'})
                        if user_info:
                            employee_no = user_info.get('employee_number')
                            return employee_no
                        else:
                            return  None
                    else:
                         return None
                
                elif role == 'ee':
                    office_info = self.offices_collection.find_one({'location_code': location_code})
                    if office_info:
                        division_code = office_info.get('division_code')
                        user_info = self.user_collection.find_one({'work_location_code': division_code, 'role_type': 'oic'})
                        if user_info:
                            employee_no = user_info.get('employee_number')
                            return employee_no
                        else:
                            return None
                    else:
                        return None
                
                elif role == 'se':
                    office_info = self.offices_collection.find_one({'location_code': location_code})
                    if office_info:
                        circle_code = office_info.get('circle_code')
                        user_info = self.user_collection.find_one({'work_location_code': circle_code, 'role_type': 'oic'})
                        if user_info:
                            employee_no = user_info.get('employee_number')
                            return employee_no
                        else:
                            return None
                    else:
                        return None
                
                return  None
        except Exception as e:
            print(f"Unexpected error while getting user info: {e}")
            return None

# if __name__ == "__main__":
#     user_profile_manager = myserv_getngbprofile()
#     with app.app_context():
#         # username = 'se_khandwa'
#         # username = 'ee_khandwa_city'
#         username = 'ae_kwz'
#         employee_no = user_profile_manager.get_user_info(username)
#         if employee_no is not None:
#             print(f"ERP Profile Employee Number: {employee_no}")
#         else:
#             print("ERP profile Employee not found in database")