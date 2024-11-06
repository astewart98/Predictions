import pymssql
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        # Determine the environment and connection string
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_name = os.getenv("DB_NAME")

        # Get the Cloud SQL connection name from environment variable
        cloud_sql_connection_name = os.getenv("CLOUDSQL_CONNECTION_NAME")
        
        # Cloud SQL Unix socket file path
        unix_socket = f"/cloudsql/{cloud_sql_connection_name}"

        # Initialize the connection
        self.connection = pymssql.connect(
            server=unix_socket,
            user=db_user,
            password=db_password,
            database=db_name
        )

    def __enter__(self):
        # Return the connection object when entering the `with` block
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        # Close the connection when exiting the `with` block
        self.connection.close()

def create_connection():
    return DatabaseConnection()

current_year = 2024
current_week = None  
start_end_times = []  