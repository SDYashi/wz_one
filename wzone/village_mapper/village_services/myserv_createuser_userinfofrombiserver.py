import psycopg2
from pymongo import MongoClient
from myservices_oneapp.myserv_generate_mpwz_id_forrecords import myserv_generate_mpwz_id_forrecords
class myserv_createuser_userinfofrombiserver: 

    def __init__(self, pg_config_remote, pg_config_local):
        self.pg_conn_remote = psycopg2.connect(**pg_config_remote)
        self.pg_conn_local = psycopg2.connect(**pg_config_local)

    def fetch_postgresql_data(self):
        cursor = self.pg_conn_remote.cursor()
        cursor.execute("SELECT * FROM  warehouse.erp_mppk_employee_detail_new;")
        records = cursor.fetchall()
        cursor.close()
        return records

def insert_into_vill_users(self, records):
    cursor = self.pg_conn_remote.cursor()
    for record in records:
        # Assuming 'record' is a tuple or list containing the necessary fields
        cursor.execute("""
            INSERT INTO public.vill_users (
                id, user_role, username, password, work_location_code, 
                status, token_app, token_issuedon, token_expiredon, 
                created_by, created_on, updated_by, updated_on, 
                access_modules, "access_sidebar"
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            record[0],  # id
            record[1],  # user_role
            record[2],  # username
            record[3],  # password
            record[4],  # work_location_code
            record[5],  # status
            record[6],  # token_app
            record[7],  # token_issuedon
            record[8],  # token_expiredon
            record[9],  # created_by
            record[10], # created_on
            record[11], # updated_by
            record[12], # updated_on
            record[13], # access_modules
            record[14]  # access_sidebar
        ))
    self.pg_conn_remote.commit()
    cursor.close()


  
    def sync_databases(self):
        records = self.fetch_postgresql_data()
        self.insert_into_mongo(records)
        return None

    def close_connections(self):
        self.pg_conn.close()
        self.mongo_client.close()




