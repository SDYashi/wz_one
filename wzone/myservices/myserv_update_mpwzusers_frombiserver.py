import psycopg2
from pymongo import MongoClient
from myserv_generate_mpwz_id_forrecords import myserv_generate_mpwz_id_forrecords
from myserv_update_users_logs import myserv_update_users_logs
class myserv_update_mpwzusers_frombiserver: 

    def __init__(self, pg_config, mongo_config):
        self.pg_conn = psycopg2.connect(**pg_config)
        self.mongo_client = MongoClient(mongo_config['uri'])
        self.mongo_db = self.mongo_client[mongo_config['db']]
        self.mongo_collection = self.mongo_db[mongo_config['collection']] 

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
            # Create the user_data dictionary for insert into mpwz_users
            log_entry_event = myserv_update_users_logs()
            myseq_mpwz_id = myserv_generate_mpwz_id_forrecords.get_next_sequence('mpwz_users')   
            user_data = {
                'mpwz_id': myseq_mpwz_id,
                'user_person_type': record[0], 
                'employee_number': record[1], 
                'employee_name': record[2], 
                'first_name': record[3],
                'last_name': record[4],
                'blood_type': record[5],
                'date_of_birth': record[6],
                'original_date_of_hire': record[7],
                'registered_disabled_flag': record[8],
                'town_of_birth': record[9],
                'email_address': record[10],
                'gender': record[11],
                'nationality': record[12],
                'marital_status': record[13],
                'last_updated_by': record[14],
                'pan_number': record[15],
                'gpf_pran': record[16],
                'height': record[17],
                'p_id': record[18],
                'parent_wing': record[19],
                'res_catg': record[20],
                'sb_no': record[21],
                'phy_loc': record[22],
                'app_ord': record[23],
                'opt_filled': record[24],
                'r _year': record[25],
                'designation': record[26],
                'grade': record[27],
                'office': record[28],
                'work_location': record[29],
                'work_location_code': record[30],
                'class': record[31],
                'class_as_perjob': record[32],
                'tech_nontech': record[33],
                'payroll_name': record[34],
                'pay_basis': record[35],
                'pay_in_payband': record[36],
                'user_status': record[37],
                'oic_no': record[38],
                'oic_name': record[39],
                'emp_catg': record[40],
                'soft_kff': record[41],
                'position_name': record[42],
                'organization_id': record[43],
                'location_id': record[44],
                'person_id': record[45],
                'address': record[46],
                'town': record[47],
                'state': record[48],
                'qual': record[49],
                'assignment_start_date': record[50],
                'assignment_start_at_location': record[51],
                'assignment_start_date_at_org': record[52],
                'phone_no': record[53],
                'pay_proposal_id': record[54],
                'assignment_id': record[55],
                'aadhar_number': record[56],
                'employee_class': record[57]
            }
            if not self.mongo_collection.find_one({'employee_number': employee_number}):
                self.mongo_collection.insert_one(user_data)
                print(f"{insert_records} user information saved successfully for: {employee_number}")
            else:
                print(f"{insert_records} User information is already exists in database: {employee_number}")
            insert_records=insert_records+1

    def sync_databases(self):
        records = self.fetch_postgresql_data()
        self.insert_into_mongo(records)

    def close_connections(self):
        self.pg_conn.close()
        self.mongo_client.close()

# Configuration for PostgreSQL and MongoDB
pg_config = {
    'dbname': 'postgres',
    'user': 'biro',
    'password': 'biro',
    'host': '10.98.0.87',
    'port': '5432'
}

mongo_config = {
    'uri': 'mongodb://localhost:27017/',
    'db': 'admin',
    'collection': 'mpwz_users'
}

if __name__ == "__main__":
    db_sync = myserv_update_mpwzusers_frombiserver(pg_config, mongo_config)
    try:
        db_sync.sync_databases()
    finally:
        db_sync.close_connections()