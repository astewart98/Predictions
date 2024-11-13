import pymssql
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.connection = pymssql.connect(
            server="projectionsdatabase.database.windows.net",
            port=1433,
            user="scorecast",
            password="Yubullyme69!",
            database="projectionsdatabase",
            ssl=True
        )

    def __enter__(self):
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()

def create_connection():
    return DatabaseConnection()

current_year = 2024
current_week = None  
start_end_times = []  