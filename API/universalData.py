import pymssql
import os

def create_connection():
    try:
        # Establish connection using Cloud SQL Unix socket path
        connection = pymssql.connect(
            host="/cloudsql/sports-predictions-440800:us-east5:projections-database",
            user="sqlserver",              # Database username
            password="Yubullyme69!",        # Database password
            database="projectionsDatabase"  # Target database name
        )
        print("Connection successful!")  # Debug: confirms successful connection
        return connection
    except pymssql.OperationalError as e:
        print("Error connecting to the database:", e)  # Debugging message for connection issues
        raise


current_year = 2024
current_week = None  
start_end_times = []  