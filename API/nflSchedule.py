import requests
from API import universalData

# Connect to database
conn = universalData.create_connection()
cursor = conn.cursor()

current_year = universalData.current_year

# Extracts all 18 NFL weeks through looping each week
try:
    for current_week in range(1, 19):
        url = f"https://cdn.espn.com/core/nfl/schedule?xhr=1&year={current_year}&week={current_week}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            bulk_data = []
            game_id = 1

            # Data extraction
            if 'content' in data and 'schedule' in data['content']:
                schedule = data['content']['schedule']
                for date_key, week_data in schedule.items():
                    if 'games' in week_data:
                        for game in week_data['games']:
                            team_2_abv = game['competitions'][0]['competitors'][0]['team']['abbreviation']
                            team_1_abv = game['competitions'][0]['competitors'][1]['team']['abbreviation']
                            bulk_data.append((current_year, current_week, game_id, team_1_abv, team_2_abv))
                            game_id += 1

            # Insert into database
            if bulk_data:
                insert_sql = """
                    INSERT INTO nflScheduleTable (year_id, week_id, game_id, team_1_abv, team_2_abv)
                    VALUES (%s, %s, %s, %s, %s)
                """

                print("Executing SQL command:")
                print(insert_sql)
                print("With data:")
                for data in bulk_data:
                    print(data)
                cursor.executemany(insert_sql, bulk_data)
                print(f"Week {current_week} data inserted successfully.")
            else:
                print(f"No games found for Year: {current_year}, Week: {current_week}")
        else:
            print(f"Failed to fetch data for Year: {current_year}, Week: {current_week} (Status Code: {response.status_code})")
    conn.commit()

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    cursor.close()
    conn.close()
