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

        # Default connection details for local development
        server = os.getenv("DB_SERVER", "localhost")  # Default to localhost for local dev
        port = int(os.getenv("DB_PORT", 1433))  # Default to 1433 if not set

        # Check if we are running on Cloud Run (based on GAE_ENV)
        if os.getenv("GAE_ENV") == "standard":  # Check if in Cloud Run environment
            connection_name = os.getenv("CLOUDSQL_CONNECTION_NAME", "sports-predictions-440800:us-east5:projections-database")
            server = f"/cloudsql/{connection_name}"  # Use Cloud SQL socket path for Cloud Run

        # Initialize the connection
        self.connection = pymssql.connect(
            server=server,
            port=port,
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