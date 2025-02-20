import requests
import psycopg2
from psycopg2 import sql

class DataFetcher:
    def __init__(self, db_config):
        self.api_url = "http://mpezgis.in/DWZ/api/proposed_wk_dtls.php?dc_code={}"
        self.db_config = db_config

    def fetch_data(self, dc_code):
        try:
            response = requests.get(self.api_url.format(dc_code))
            response.raise_for_status() 
            return response.json()  
        except requests.RequestException as e:
            print(f"Error fetching data from API for dc_code {dc_code}: {e}")
            return None

    def insert_data(self, data):
        try:
            # Connect to the PostgreSQL database
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            # Prepare the SQL insert statement
            insert_query = sql.SQL("""
                INSERT INTO proposed_work_details (
                   circle_code, division_code, dc_code, feeder_id, fdr_name, ss_id, scheme_code, work_status, creation_dt
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)  
            """)

            # Iterate over the fetched data and insert it into the database
            for item in data['WORK_DETAILS']:
                values = (
                    item['CIRCLE_CODE'],
                    item['DIVISION_CODE'],
                    item['DC_CODE'],
                    item['FEEDER_ID'],
                    item['FDR_NAME'],
                    item['SS_ID'],
                    item['SCHEME_CODE'],
                    item['WORK_STATUS'],
                    item['CREATION_DT']
                )
                cursor.execute(insert_query, values)
                print("Row Data inserted successfully.",values)

            # Commit the transaction
            conn.commit()
            print("Data inserted successfully.")

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error inserting data into PostgreSQL: {error}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def fetch_dc_codes(self):
        dc_codes = []
        try:
            # Connect to the PostgreSQL database
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            # Prepare the SQL select statement
            select_query = sql.SQL("SELECT c_code FROM public.t_location_master")
            cursor.execute(select_query)

            # Fetch all dc_codes
            dc_codes = cursor.fetchall()
            dc_codes = [code[0] for code in dc_codes]  # Extract the first element from each tuple

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error fetching dc_codes from PostgreSQL: {error}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        return dc_codes

    def run(self):
        dc_codes = self.fetch_dc_codes()
        for dc_code in dc_codes:
            data = self.fetch_data(dc_code)
            if data:
                self.insert_data(data)

# Database configuration
db_config = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'Superadmin#1234',
    'host': 'localhost', 
    'port': '5433'   
}

# Create an instance of the DataFetcher class and run it
data_fetcher = DataFetcher(db_config)
data_fetcher.run()