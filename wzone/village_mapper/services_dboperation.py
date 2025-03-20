import psycopg2

class services_dboperation:    
    def __init__(self, hosttype):
        self.host =hosttype
        if self.host == 'localhost':
            self.dbname = 'postgres'
            self.user = 'postgres'
            self.password = 'Superadmin#1234'
            self.host = '127.0.0.1'
            self.port = '5433'
        else:
            self.dbname = 'postgres'
            self.user = 'deepak'
            self.password = 'myyashi#1705'
            self.host = '10.98.0.87'
            self.port = '5432'

    def get_connection(self):
        return psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )

    def create_table(self, fetch_query):
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            cursor.execute(fetch_query)
            conn.commit()
            print("Local table created successfully.")
            
        except Exception as e:
            print(f"Error creating local table: {e}")
        finally:
            cursor.close()
            conn.close()

    def fetch_data(self, fetch_query):
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(fetch_query)
            data = cursor.fetchall()
            return data
            
        except Exception as e:
            print(f"Error fetching data from database: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def insert_data(self, insert_query, data):
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            cursor.executemany(insert_query, data)
            conn.commit()
            print(f"Inserted {len(data)} records into local table.")
            
        except Exception as e:
            print(f"Error inserting data into database: {e}")
        finally:
            cursor.close()
            conn.close()

    def update_data(self, update_query, data):
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            cursor.executemany(update_query, data)
            conn.commit()
            print(f"Updated {len(data)} records in local table.")
            
        except Exception as e:
            print(f"Error updating data in database: {e}")
        finally:
            cursor.close()
            conn.close()

    def delete_data(self, delete_query, data):
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            cursor.executemany(delete_query, data)
            conn.commit()
            print(f"Deleted {len(data)} records from local table.")
            
        except Exception as e:
            print(f"Error deleting data from database: {e}")
        finally:
            cursor.close()
            conn.close()

    def truncate_table(self, table_name):
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"TRUNCATE TABLE {table_name};")
            conn.commit()
            print(f"Truncated table {table_name}.")
            
        except Exception as e:
            print(f"Error truncating table: {e}")
        finally:
            cursor.close()
            conn.close()

    def drop_table(self, table_name):
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            conn.commit()
            print(f"Dropped table {table_name}.")
            
        except Exception as e:
            print(f"Error dropping table: {e}")
        finally:
            cursor.close()
            conn.close()

