import os
import pymssql
from dotenv import load_dotenv

load_dotenv()

def create_connection():
    return pymssql.connect(
        host="/cloudsql/sports-predictions-440800:us-east5:projections-database",
        user="sqlserver",
        password="Yubullyme69!",
        database="projectionsDatabase"
    )

current_year = 2024
current_week = None  
start_end_times = []  