import requests
import pymssql
import time
import logging
import datetime
import pytz  
import schedule
import universalData  
from nflActiveDatesTimes import update_week_and_times  

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    # Connect to database
    conn = universalData.create_connection()
    cursor = conn.cursor()
    logging.info("Database connection established.")
except pymssql.DatabaseError as e:
    logging.error(f"Error connecting to the database: {e}")
    raise SystemExit("Exiting due to database connection failure.")

def cache_schedule():
    global schedule_cache
    current_week = 9
    current_year = universalData.current_year
    
    if current_week is None:
        logging.warning("Current week not set. Cannot cache schedule.")
        return

    # Query NFL schedule and store in cache 
    query_schedule = """
        SELECT schedule_id, team_1_abv, team_2_abv
        FROM nflScheduleTable
        WHERE week_id = %s AND year_id = %s;
    """
    try:
        cursor.execute(query_schedule, (current_week, current_year))
        schedule_cache = {(row[1], row[2]): row[0] for row in cursor.fetchall()}  
        logging.info("Schedule cache populated successfully.")
    except pymssql.DatabaseError as e:
        logging.error(f"Error fetching schedule data: {e}")

def fetch_data():
    current_week = 9
    current_year = universalData.current_year

    if current_week is None:
        logging.warning("Current week not set. Cannot fetch data.")
        return

    try:
        url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={current_year}&seasontype=2&week={current_week}"
        response = requests.get(url)
        response.raise_for_status()  
        data = response.json()
        logging.info("Data fetched successfully from API.")

        # Extract current NFL scores
        bulk_data = []
        for event in data['events']:
            for game in event['competitions']:
                if game['status']['type']['state'] in ['in', 'post']:  
                    team_2_abv = game['competitors'][0]['team']['abbreviation']  
                    team_1_abv = game['competitors'][1]['team']['abbreviation']  
                    score_2 = game['competitors'][0]['score']  
                    score_1 = game['competitors'][1]['score']  

                    schedule_id = schedule_cache.get((team_1_abv, team_2_abv))
                    if schedule_id is not None:
                        bulk_data.append((schedule_id, score_1, score_2))

        # Store scores in database
        if bulk_data:
            insert_sql = """
                MERGE actualScoreTable AS target
                USING (VALUES (%s, %s, %s)) AS source (schedule_id, a_score_team_1, a_score_team_2)
                ON target.schedule_id = source.schedule_id
                WHEN MATCHED THEN 
                    UPDATE SET a_score_team_1 = source.a_score_team_1, a_score_team_2 = source.a_score_team_2
                WHEN NOT MATCHED THEN
                    INSERT (schedule_id, a_score_team_1, a_score_team_2)
                    VALUES (source.schedule_id, source.a_score_team_1, source.a_score_team_2);
            """
            cursor.executemany(insert_sql, bulk_data)
            conn.commit()
            logging.info("Database updated successfully with new scores.")
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
    except pymssql.DatabaseError as e:
        logging.error(f"Database operation failed: {e}")

# Only run during live NFL game times
def should_run_fetch():
    now = datetime.datetime.now(pytz.UTC)  
    for start, end in universalData.start_end_times:
        if start <= now <= end:
            return True
    return False

def run_fetch_if_in_time():
    if should_run_fetch():
        fetch_data()

def weekly_update():
    update_week_and_times()  
    cache_schedule()  

update_week_and_times()  
cache_schedule()  

fetch_data() 

# Cache schedule once a week, extract scores every 5 minutes during gametime
schedule.every().tuesday.at("08:00").do(weekly_update)
schedule.every(5).minutes.do(run_fetch_if_in_time)

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    logging.info("Process interrupted. Closing database connection.")
    cursor.close()
    conn.close()
