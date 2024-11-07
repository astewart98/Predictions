import pymssql
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        # Initialize the connection
        self.connection = pymssql.connect(
            server=os.getenv("DB_SERVER"),
            port=int(os.getenv("DB_PORT", 1433)),  # Default to 1433
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
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