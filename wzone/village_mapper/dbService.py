import psycopg2

class DatabaseConfig:    
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def get_connection(self):
        """Create and return a database connection."""
        return psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )


class DatabaseOperations:    
    def __init__(self, db_config):
        self.db_config = db_config

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


def main():
    # Configuration for local and remote databases
    local_db_config = DatabaseConfig(
        dbname='local_db_name',
        user='local_user',
        password='local_password',
        host='localhost',
        port='5432'
    )

    remote_db_config = DatabaseConfig(
        dbname='remote_db_name',
        user='remote_user',
        password='remote_password',
        host='remote_host',
        port='5432'
    )

    # Create DatabaseOperations instances
    local_db_operations = DatabaseOperations(local_db_config)
    remote_db_operations = DatabaseOperations(remote_db_config)

    # Create local table
    local_db_operations.create_table()

    # Fetch data from remote database
    fetch_query = "SELECT name, age FROM remote_table;"
    remote_data = remote_db_operations.fetch_data(fetch_query)

    # Insert fetched data into local database
    if remote_data:
        insert_query = "INSERT INTO my_table (name, age) VALUES (%s, %s);"
        local_db_operations.insert_data(insert_query, remote_data)


