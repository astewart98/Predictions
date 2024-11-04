import pymssql

def create_connection():
    return pymssql.connect(
        server='localhost',
        port=1433,
        user='sa',
        password='Yubullyme69!',
        database='projectionsDatabase'
    )

current_year = 2024
current_week = None  
start_end_times = []  