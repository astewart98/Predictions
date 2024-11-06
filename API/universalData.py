import pymssql
import os
from dotenv import load_dotenv

load_dotenv()

def create_connection():
        pymssql.connect(
        server=os.getenv("DB_SERVER"),
        port=int(os.getenv("DB_PORT", 1433)),  # Default to 1433
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


current_year = 2024
current_week = None  
start_end_times = []  