import pymssql
import logging
import pytz
import universalData

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Connect to database
try:
    conn = universalData.create_connection()
    cursor = conn.cursor()
    logging.info("Database connection established.")
except pymssql.DatabaseError as e:
    logging.error(f"Error connecting to the database: {e}")
    raise SystemExit("Exiting due to database connection failure.")

# Pulls start/end times for closest date ranges into future
def update_week_and_times():
    query_closest_week = """
        SELECT TOP 5 week_id, start_date_time, end_date_time
        FROM onDaysTable
        WHERE year_id = %s AND start_date_time > GETUTCDATE()
        ORDER BY start_date_time ASC;
    """
    try:
        cursor.execute(query_closest_week, (universalData.current_year,))
        results = cursor.fetchall()

        # Selects start/end times with proper week ID
        if results:
            universalData.current_week = results[0][0]
            query_times_for_current_week = """
                SELECT start_date_time, end_date_time
                FROM onDaysTable
                WHERE year_id = %s AND week_id = %s;
            """
            cursor.execute(query_times_for_current_week, (universalData.current_year, universalData.current_week))
            universalData.start_end_times = [(row[0], row[1]) for row in cursor.fetchall()] 

            utc = pytz.UTC
            universalData.start_end_times = [(utc.localize(start), utc.localize(end)) for start, end in universalData.start_end_times]

            logging.info(f"Current week set to {universalData.current_week} with start/end times for {len(universalData.start_end_times)} intervals.")
        else:
            logging.warning("No future weeks found in the database.")
    
    except pymssql.DatabaseError as e:
        logging.error(f"Error querying week and times: {e}")
