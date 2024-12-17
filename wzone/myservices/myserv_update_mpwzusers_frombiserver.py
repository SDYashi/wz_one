import psycopg2
from pymongo import MongoClient
from myservices.myserv_generate_mpwz_id_forrecords import myserv_generate_mpwz_id_forrecords
class myserv_update_mpwzusers_frombiserver: 

    def __init__(self, pg_config, mongo_config):
        self.pg_conn = psycopg2.connect(**pg_config)
        self.mongo_client = MongoClient(mongo_config['uri'])
        self.mongo_db = self.mongo_client[mongo_config['db']]
        self.mongo_collection = self.mongo_db[mongo_config['collection']]       
        self.seq_gen = myserv_generate_mpwz_id_forrecords()

    def fetch_postgresql_data(self):
        cursor = self.pg_conn.cursor()
        cursor.execute("SELECT * FROM  warehouse.erp_mppk_employee_detail_new;")
        records = cursor.fetchall()
        cursor.close()
        return records

    def insert_into_mongo(self, records):
        insert_records=1
        for record in records:
            employee_number = record[1]  
            myseq_mpwz_id = self.seq_gen.get_next_sequence('mpwz_users')   
            user_data = {
                'mpwz_id': str(myseq_mpwz_id),
                'user_person_type': str(record[0]), 
                'employee_number': str(record[1]), 
                'employee_name': str(record[2]), 
                'first_name': str(record[3]),
                'last_name': str(record[4]),
                'blood_type': str(record[5]),
                'date_of_birth': str(record[6]),
                'original_date_of_hire': str(record[7]),
                'registered_disabled_flag': str(record[8]),
                'town_of_birth': str(record[9]),
                'email_address': str(record[10]),
                'gender': str(record[11]),
                'nationality': str(record[12]),
                'marital_status': str(record[13]),
                'last_updated_by': str(record[14]),
                'pan_number': str(record[15]),
                'gpf_pran': str(record[16]),
                'height': str(record[17]),
                'p_id': str(record[18]),
                'parent_wing': str(record[19]),
                'res_catg': str(record[20]),
                'sb_no': str(record[21]),
                'phy_loc': str(record[22]),
                'app_ord': str(record[23]),
                'opt_filled': str(record[24]),
                'r_year': str(record[25]), 
                'designation': str(record[26]),
                'grade': str(record[27]),
                'office': str(record[28]),
                'work_location': str(record[29]),
                'work_location_code': str(record[30]),
                'class': str(record[31]),
                'class_as_perjob': str(record[32]),
                'tech_nontech': str(record[33]),
                'payroll_name': str(record[34]),
                'pay_basis': str(record[35]),
                'pay_in_payband': str(record[36]),
                'user_status': str(record[37]),
                'oic_no': str(record[38]),
                'oic_name': str(record[39]),
                'emp_catg': str(record[40]),
                'soft_kff': str(record[41]),
                'position_name': str(record[42]),
                'organization_id': str(record[43]),
                'location_id': str(record[44]),
                'person_id': str(record[45]),
                'address': str(record[46]),
                'town': str(record[47]),
                'state': str(record[48]),
                'qual': str(record[49]),
                'assignment_start_date': str(record[50]),
                'assignment_start_at_location': str(record[51]),
                'assignment_start_date_at_org': str(record[52]),
                'phone_no': str(record[53]),
                'pay_proposal_id': str(record[54]),
                'assignment_id': str(record[55]),
                'aadhar_number': str(record[56]),
                'employee_class': str(record[57])
            }
            if not self.mongo_collection.find_one({'employee_number': employee_number}):
                self.mongo_collection.insert_one(user_data)
                print(f"{insert_records} new user information saved successfully for: {employee_number}")
            else:
                self.mongo_collection.delete_one(user_data)
                self.mongo_collection.insert_one(user_data)
                print(f"{insert_records} user information is already existed in database so updated sccessfully for: {employee_number}")
            insert_records=insert_records+1

    def sync_databases(self):
        records = self.fetch_postgresql_data()
        self.insert_into_mongo(records)
        return None

    def close_connections(self):
        self.pg_conn.close()
        self.mongo_client.close()



