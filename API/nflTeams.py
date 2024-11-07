import requests
import universalData  

# Connect to database
conn = universalData.create_connection()

cursor = conn.cursor()
url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=2024&seasontype=2&week=1"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    bulk_data = []
    
    # Extract NFL team data
    for game in data['events']:
        for competitor in game['competitions'][0]['competitors']:
            team_name = competitor['team']['name']
            team_abv = competitor['team']['abbreviation']
            team_logo = competitor['team']['logo']
            team_color_code = competitor['team']['color']
            team_location = competitor['team']['location']
            bulk_data.append((team_name, team_abv, team_logo, team_color_code, team_location))

    # Insert into database 
    if bulk_data:
        insert_sql = """
            INSERT INTO nflTeamTable (team_name, team_abv, team_logo, team_color_code, team_location)
            VALUES (%s, %s, %s, %s, %s)
        """

        print("Executing SQL command:")
        print(insert_sql)
        print("With data:")
        for data in bulk_data:
            print(data)

        cursor.executemany(insert_sql, bulk_data)
        print("Team data inserted successfully.")

        conn.commit()
    else:
        print("No data found.")
else:
    print(f"Failed to fetch data. (Status Code: {response.status_code})")

cursor.close()
conn.close()
