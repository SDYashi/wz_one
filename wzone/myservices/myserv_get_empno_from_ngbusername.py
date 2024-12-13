from flask import Flask, jsonify
from myserv_connection_mongodb import myserv_connection_mongodb

class myserv_get_empno_from_ngbusername:
    
    def __init__(self):
        try:    
            self.mongo_db = myserv_connection_mongodb('admin')   
            self.dbconnect = self.mongo_db.get_connection() 
            self.usersprofiles_collection = self.dbconnect['mpwz_ngb_usersprofiles']
            self.offices_collection = self.dbconnect['mpwz_offices']
            self.user_collection = self.dbconnect['mpwz_users']
        except Exception as e:
            print(f"Unexpected error while setting up MongoDB: {e}")
            raise
    def get_user_info(self, username):
        try:
            user_profile = self.usersprofiles_collection.find_one({'username': username})
            if not user_profile:
                return None  
            else:
                role = user_profile.get('role')
                location_code = user_profile.get('location_code')
                print('ngb user role & primary location code:', role, "-", location_code)
                
                office_info = self.offices_collection.find_one({'location_code': location_code})
                if not office_info:
                    return None
                
                if role == 'oic':
                    user_info = self.get_employee_details(location_code)
                elif role == 'ee':
                    division_code = office_info.get('division_code')
                    user_info = self.get_employee_details(division_code)
                elif role == 'se':
                    circle_code = office_info.get('circle_code')
                    user_info = self.get_employee_details(circle_code)
                else:
                    return None
                            
                if user_info:  # user_info is a list
                    user_info_dict = user_info[0] if len(user_info) > 0 else None
                    if user_info_dict:
                        employee_no = user_info_dict.get('employee_number')
                        return employee_no
                    
                return None
        except Exception as e:
            print(f"Unexpected error while getting user info: {e}")
            return None   

    def get_employee_details(self, work_location_code):
        oic_no_list = self.user_collection.distinct("oic_no", {"user_status": "Active Assignment"})   
        query = {
            "work_location_code": work_location_code,
            "employee_number": {"$in": oic_no_list}
        }        
        # Fetch employee details
        employee_details = list(self.user_collection.find(query))
        return employee_details
       
    def mongo_dbconnect_close(self):
        status = self.mongo_db.close_connection()
        return status


if __name__ == "__main__":
    user_profile_manager = myserv_get_empno_from_ngbusername() 
    employee_no = user_profile_manager.get_user_info('ae_kwz')
    # employee_no = user_profile_manager.get_user_info('ee_khandwa_city')
    # employee_no = user_profile_manager.get_user_info('se_khandwa')
    if employee_no is not None:
        print("employee_number", employee_no)
    else:
         print("employee_number is not found", employee_no , 200)