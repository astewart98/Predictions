from flask import Flask, request, jsonify, session, redirect, url_for, render_template
import pymssql
import bcrypt
import os
from API import universalData

app = Flask(__name__)
app.secret_key = 'dev_secret_key_12345'
print("DB_SERVER:", os.getenv("DB_SERVER"))
print("DB_USER:", os.getenv("DB_USER"))


# Homepage redirect
@app.route('/')
def home_page():
    return render_template('homePage.html')

# Login logic
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    with universalData.create_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id, password_hash FROM userTable WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user and check_password(password, user[1]):  
                session['user_id'] = user[0]  
                return jsonify({'success': True, 'redirect': url_for('account_page'), 'user_id': user[0]})  
            else:
                return jsonify({'success': False, 'message': 'Invalid credentials'})

# Register logic
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    fname = data['fname']
    lname = data['lname']
    email = data['email']
    password = data['password']

    if not fname or not lname or not email or not password:
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400
    
    # Hash password for security
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        with universalData.create_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO userTable (first_name, last_name, email, password_hash) VALUES (%s, %s, %s, %s)",
                    (fname, lname, email, hashed_password)
                )
                conn.commit()

                return jsonify({'success': True})
    except pymssql.IntegrityError:
        return jsonify({'success': False, 'message': 'Email already exists.'}), 400
    except Exception as e:
        print(f"Error during registration: {e}")  
        return jsonify({'success': False, 'message': str(e)}), 500  

# Create a league
@app.route('/api/create_league', methods=['POST'])
def createLeague():
    data = request.get_json()
    league_name = data['leagueName']
    user_id = data['userId']
    is_private = data['isPrivate']
    league_size = data['leagueSize']
    league_pass = data['leaguePass']

    with universalData.create_connection() as conn:
        with conn.cursor() as cursor:
            # Verify league name doesnt exist for user
            cursor.execute("SELECT league_name FROM leagueTable WHERE lm_user_id = %s AND league_name =%s", (user_id, league_name,))
            leagueNameVerify = cursor.fetchone()

            if leagueNameVerify:
                return jsonify({'success': False, 'message': 'Invalid credentials'})
            else:
                cursor.execute(
                        "INSERT INTO leagueTable (league_name, lm_user_id, is_private, max_members, league_pass) VALUES (%s, %s, %s, %s, %s)",
                        (league_name, user_id, is_private, league_size, league_pass)
                    )
                conn.commit()

                cursor.execute("SELECT league_id FROM leagueTable WHERE lm_user_id = %s AND league_name =%s", (user_id, league_name,))
                league_id = cursor.fetchone()[0]

                return jsonify({'success': True, 'league_id': league_id, 'message': 'League created successfully'})
            
# Create a team
@app.route('/api/create_team', methods=['POST'])
def createTeam():
    data = request.get_json()
    league_id_join = data['leagueIdJoin']
    user_id = data['userId']
    team_name = data['teamName']
    team_picture = data['teamLogo']
    is_lm = data['isLm']
    league_pass = data['leaguePass']

    with universalData.create_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT league_id FROM leagueTable WHERE league_id = %s AND (league_pass = %s OR league_pass IS NULL)", (league_id_join, league_pass,))
            leagueIdVerify = cursor.fetchone()

            # First verify if team name already exists in league
            if leagueIdVerify:
                cursor.execute("""
                    SELECT team_name 
                    FROM userLeagueRelationTable 
                    WHERE league_id = %s AND (team_name = %s OR user_id = %s)
                """, (league_id_join, team_name, user_id))
                leagueTeamVerify = cursor.fetchone()

                if leagueTeamVerify:
                    return jsonify({'success': False, 'message': 'Team Name already exists in this league'})
                else:
                    cursor.execute(
                        "INSERT INTO userLeagueRelationTable (user_id, league_id, team_picture, team_name, is_lm) VALUES (%s, %s, %s, %s, %s)",
                        (user_id, league_id_join, team_picture, team_name, is_lm)
                    )
                    conn.commit()

                    return jsonify({'success': True, 'message': 'Team created successfully.'})
            else:
                return jsonify({'success': False, 'message': 'Invalid League ID or League Password'})
            
@app.route('/api/check_league_privacy/<league_id>', methods=['GET'])
def check_league_privacy(league_id):
    with universalData.create_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT is_private FROM leagueTable WHERE league_id = %s", (league_id,))
            result = cursor.fetchone()
            if result is None:
                return jsonify({'is_private': False}), 404  
            is_private = result[0] == 1
            return jsonify({'is_private': is_private})

# Account page redirect 
@app.route('/accountPage')
def account_page():
    
    if 'user_id' in session:
        return render_template('accountPage.html')  
    else:
        return redirect(url_for('home_page'))  
    
# League page redirect
@app.route('/leaguePage')
def league_page():
    league_id = request.args.get('leagueId')  
    return render_template('leaguePage.html', league_id=league_id) 

def check_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

@app.route('/api/fetch_team_info', methods=['POST'])
def fetch_team_info():
    data = request.get_json()
    user_id = data['user_id']
    league_id = data['league_id']

    with universalData.create_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT team_name, team_picture FROM userLeagueRelationTable WHERE user_id = %s AND league_id = %s", (user_id, league_id))
            team_info_result = cursor.fetchone()

            if team_info_result:
                team_name, team_picture = team_info_result
            else:
                team_name, team_picture = None, None

            return jsonify({
                'team_name': team_name,
                'team_picture': team_picture
            })
        
@app.route('/api/fetch_leagues', methods=['POST'])
def fetch_leagues():
    data = request.get_json()
    user_id = data['user_id']
    year_id = universalData.current_year

    with universalData.create_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT league_id, team_picture, team_name, is_lm FROM userLeagueRelationTable WHERE user_id = %s", (user_id,))
            league_data = cursor.fetchall()

            league_ids = [row[0] for row in league_data]  

            if league_ids:
                placeholders = ', '.join(['%s'] * len(league_ids))
                cursor.execute(f"SELECT league_id, points, winner_correct, correct_score, wins FROM seasonStatsTable WHERE league_id IN ({placeholders}) AND user_id = %s AND year_id = %s", league_ids + [user_id, year_id])
                season_stats_result = cursor.fetchall()

                cursor.execute(f"SELECT league_id, league_name, league_pass FROM leagueTable WHERE league_id IN ({placeholders})", league_ids)
                league_name = cursor.fetchall()
    
            else:
                season_stats_result = []
                league_name = []

            response_data = {
                'league_data': league_data,
                'season_stats_result': season_stats_result,
                'league_name': league_name
            }

            print('Response Data:', response_data)  
            return jsonify(response_data)
        
@app.route('/api/fetch_week_stats', methods=['POST'])
def fetch_week_stats():
    data = request.get_json()
    user_id = data['user_id']
    league_id = data['league_id']
    year_id = universalData.current_year
    week_id = data['week_id']

    with universalData.create_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT points, winner_correct, correct_score, win FROM weeklyStatsTable WHERE user_id = %s AND league_id = %s AND year_id = %s AND week_id = %s", (user_id, league_id, year_id, week_id))
            week_stats_result = cursor.fetchone()

            if week_stats_result:
                points, winner_correct, correct_score, win = week_stats_result
            else:
                points, winner_correct, correct_score, win = 0, 0, 0, 0

            return jsonify({
                'points': points,
                'winner_correct': winner_correct,
                'correct_score': correct_score,
                'win': win
            })
        
@app.route('/api/fetch_season_stats', methods=['POST'])
def fetch_season_stats():
    data = request.get_json()
    user_id = data['user_id']
    league_id = data['league_id']
    year_id = universalData.current_year

    with universalData.create_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT points, winner_correct, correct_score, wins FROM seasonStatsTable WHERE user_id = %s AND league_id = %s AND year_id = %s", (user_id, league_id, year_id))
            season_stats_result = cursor.fetchone()

            if season_stats_result:
                points, winner_correct, correct_score, wins = season_stats_result
            else:
                points, winner_correct, correct_score, wins = 0, 0, 0, 0

            cursor.execute("SELECT user_id, points, winner_correct, wins, correct_score FROM seasonStatsTable WHERE year_id = %s AND league_id = %s AND user_id != %s", (year_id, league_id, user_id,))
            opp_season_stats = cursor.fetchall()

            user_ids = [row[0] for row in opp_season_stats]  

            if user_ids:
                placeholders = ', '.join(['%s'] * len(user_ids))
                cursor.execute(f"SELECT user_id, team_name FROM userLeagueRelationTable WHERE user_id IN ({placeholders}) AND league_id = %s", user_ids + [league_id])
                opp_name = cursor.fetchall()
            else:
                opp_name = []

            return jsonify({
                'points': points,
                'winner_correct': winner_correct,
                'correct_score': correct_score,
                'wins': wins,
                'opp_season_stats': opp_season_stats,
                'opp_name': opp_name
            })

@app.route('/api/fetch_slide_data', methods=['POST'])
def fetch_slide_data():
    data = request.get_json()
    year_id = universalData.current_year
    user_id = data['user_id']
    week_id = data['week_id']
    league_id = data['league_id']

    with universalData.create_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT schedule_id, game_id, team_1_abv, team_2_abv FROM nflScheduleTable WHERE year_id = %s AND week_id = %s", (year_id, week_id))
            week_nfl_schedule = cursor.fetchall()

            cursor.execute("SELECT team_abv, team_logo, team_color_code FROM nflTeamTable")
            nfl_team_info = cursor.fetchall()

            schedule_ids = [row[0] for row in week_nfl_schedule]  

            if schedule_ids:
                placeholders = ', '.join(['%s'] * len(schedule_ids))
                cursor.execute(f"SELECT schedule_id, a_score_team_1, a_score_team_2 FROM actualScoreTable WHERE schedule_id IN ({placeholders})", schedule_ids)
                actual_scores = cursor.fetchall()

                cursor.execute(f"SELECT schedule_id, p_score_team_1, p_score_team_2 FROM predictionTable WHERE schedule_id IN ({placeholders}) AND user_id = %s AND league_id = %s", schedule_ids + [user_id, league_id])
                prediction_scores = cursor.fetchall()
            else:
                actual_scores = []  
                prediction_scores = []

            response_data = {
                'week_nfl_schedule': week_nfl_schedule,
                'actual_scores': actual_scores,
                'prediction_scores': prediction_scores,
                'nfl_team_info': nfl_team_info,
                'current_week_id': week_id
            }

            print('Response Data:', response_data)  
            return jsonify(response_data)
        
@app.route('/api/fetch_opp_data', methods=['POST'])
def fetch_opp_data():
    data = request.get_json()
    year_id = universalData.current_year
    week_id = data['week_id']
    league_id = data['league_id']
    user_id = data['user_id']

    with universalData.create_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id, points, winner_correct, correct_score FROM weeklyStatsTable WHERE year_id = %s AND week_id = %s AND league_id = %s AND user_id != %s", (year_id, week_id, league_id, user_id,))
            opp_points = cursor.fetchall()

            user_ids = [row[0] for row in opp_points]  

            if user_ids:
                placeholders = ', '.join(['%s'] * len(user_ids))
                cursor.execute(f"SELECT user_id, team_name FROM userLeagueRelationTable WHERE user_id IN ({placeholders}) AND league_id = %s", user_ids + [league_id])
                opp_name = cursor.fetchall()
            else:
                opp_name = []

            response_data = {
                'opp_points': opp_points,
                'opp_name': opp_name
            }

            print('Response Data:', response_data)  
            return jsonify(response_data)

@app.route('/api/get_current_week', methods=['GET'])
def get_current_week():
    try:
        with universalData.create_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT week_id
                    FROM onDaysTable
                    WHERE year_id = '2024' AND start_date_time > GETUTCDATE()
                    ORDER BY start_date_time ASC;
                """)
                week = cursor.fetchone()

                if week:
                    week_id = week[0]

                    cursor.execute("""
                        SELECT start_date_time
                        FROM onDaysTable
                        WHERE year_id = '2024' AND week_id = %s
                        ORDER BY start_date_time ASC;
                    """, (week_id,))

                    time = cursor.fetchone()

                    return jsonify({'current_week_id': week[0], 'lock_predictions_time': time[0]})  
                else:
                    return jsonify({'current_week_id': None, 'lock_predictions_time': None})  
    except Exception as e:
        print(f"Error fetching current week: {e}")
        return jsonify({'error': 'Could not fetch current week'}), 500
    
# Submit predictions to database
@app.route('/prediction-submital', methods=['POST'])
def submit_data():
    data = request.get_json()
    user_id = data['user_id']
    league_id = data['league_id']
    predictions = data['predictions']  
    
    with universalData.create_connection() as conn:
        with conn.cursor() as cursor:

            for prediction in predictions:
                schedule_id = prediction['schedule_id']
                p_score_team_1 = prediction['p_score_team_1']
                p_score_team_2 = prediction['p_score_team_2']
                cursor.execute(
                    "INSERT INTO predictionTable (user_id, schedule_id, league_id, p_score_team_1, p_score_team_2) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, schedule_id, league_id, p_score_team_1, p_score_team_2)
                )
            
            conn.commit()
            return jsonify({'success': True})

@app.route('/api/start_end_times', methods=['GET'])
def get_start_end_times():
    start_end_times = [
        (start.isoformat(), end.isoformat()) for start, end in universalData.start_end_times
    ]
    return jsonify(start_end_times)

# Save points and other stats to database
@app.route('/api/save_matchup_stats', methods=['POST'])
def save_matchup_stats():
    data = request.json
    user_id = data['user_id']
    league_id = data['league_id']
    year_id = universalData.current_year
    week_id = data['week_id']

    with universalData.create_connection() as conn:
        with conn.cursor() as cursor:

            for stat in data['stats']:
                schedule_id = stat['schedule_id']
                points = stat['points']
                correct_score = stat['correct_score']
                winner_correct = stat['winner_correct']

                # Save individual matchup
                cursor.execute("""
                    MERGE matchupStatsTable AS target 
                    USING (VALUES (%s, %s, %s, %s, %s, %s, %s, %s))
                    AS source (schedule_id, user_id, league_id, year_id, week_id, points, winner_correct, correct_score)
                    ON target.schedule_id = source.schedule_id
                    WHEN MATCHED THEN
                        UPDATE SET user_id = source.user_id, league_id = source.league_id, year_id = source.year_id, week_id = source.week_id, points = source.points, winner_correct = source.winner_correct, correct_score = source.correct_score
                    WHEN NOT MATCHED THEN
                        INSERT (schedule_id, user_id, league_id, year_id, week_id, points, winner_correct, correct_score)
                        VALUES (source.schedule_id, source.user_id, source.league_id, source.year_id, source.week_id, source.points, source.winner_correct, source.correct_score);
                """, (schedule_id, user_id, league_id, year_id, week_id, points, winner_correct, correct_score))

            conn.commit()

            cursor.execute("""
                SELECT 
                    SUM(points) AS week_points,
                    SUM(CAST(winner_correct AS INT)) AS week_winner_correct,
                    SUM(CAST(correct_score AS INT)) AS week_correct_score
                FROM matchupStatsTable
                WHERE user_id = %s AND league_id = %s AND year_id = %s AND week_id = %s
            """, (user_id, league_id, year_id, week_id))

            cumulative_stats = cursor.fetchone()

            if cumulative_stats:
                week_points, week_winner_correct, week_correct_score = cumulative_stats
            else:
                week_points = week_winner_correct = week_correct_score = 0

            # Save all matchup stats for week
            cursor.execute("""
                MERGE weeklyStatsTable AS target
                USING (VALUES (%s, %s, %s, %s, %s, %s, %s, %s))
                AS source (user_id, league_id, year_id, week_id, points, winner_correct, correct_score, win)
                ON target.user_id = source.user_id AND target.league_id = source.league_id AND target.year_id = source.year_id AND target.week_id = source.week_id
                WHEN MATCHED THEN
                    UPDATE SET points = source.points, winner_correct = source.winner_correct, correct_score = source.correct_score
                WHEN NOT MATCHED THEN
                    INSERT (user_id, league_id, year_id, week_id, points, winner_correct, correct_score, win)
                    VALUES (source.user_id, source.league_id, source.year_id, source.week_id, source.points, source.winner_correct, source.correct_score, 0);  -- Assuming win logic to be added later
            """, (user_id, league_id, year_id, week_id, week_points, week_winner_correct, week_correct_score, 0))  

            conn.commit()

            # Identify league week winner
            query = """
            SELECT TOP 1 user_id, points 
            FROM weeklyStatsTable 
            WHERE league_id = %s AND year_id = %s AND week_id = %s
            ORDER BY points DESC;
            """

            cursor.execute(query, (league_id, year_id, week_id))
            result = cursor.fetchone()

            if result:
                winner_points = result[1]
                if winner_points == 0:
                    cursor.execute("""
                    UPDATE weeklyStatsTable
                    SET win = NULL
                    WHERE league_id = %s AND year_id = %s AND week_id = %s;
                    """, (league_id, year_id, week_id,))

                    conn.commit()

                else:
                    winner_user_id = result[0]
                    cursor.execute("""
                    UPDATE weeklyStatsTable
                    SET win = 1
                    WHERE user_id = %s AND league_id = %s AND year_id = %s AND week_id = %s;
                    """, (winner_user_id, league_id, year_id, week_id,))

                    cursor.execute("""
                        UPDATE weeklyStatsTable
                        SET win = 0
                        WHERE user_id != %s AND league_id = %s AND year_id = %s AND week_id = %s;
                    """, (winner_user_id, league_id, year_id, week_id,))

                    conn.commit()

            cursor.execute("""
                SELECT 
                    SUM(points) AS season_points,
                    SUM(winner_correct) AS season_winner_correct,
                    SUM(correct_score) AS season_correct_score,
                    SUM(CAST(win AS INT)) AS season_wins
                FROM weeklyStatsTable
                WHERE user_id = %s AND league_id = %s AND year_id = %s
            """, (user_id, league_id, year_id))

            cumulative_stats = cursor.fetchone()

            if cumulative_stats:
                season_points, season_winner_correct, season_correct_score, season_wins = cumulative_stats
            else:
                season_points = season_winner_correct = season_correct_score = season_wins = 0

            # Save all matchup stats for season
            cursor.execute("""
                MERGE seasonStatsTable AS target
                USING (VALUES (%s, %s, %s, %s, %s, %s, %s))
                AS source (user_id, league_id, year_id, points, winner_correct, correct_score, wins)
                ON target.user_id = source.user_id AND target.league_id = source.league_id AND target.year_id = source.year_id
                WHEN MATCHED THEN
                    UPDATE SET points = source.points, winner_correct = source.winner_correct, correct_score = source.correct_score, wins = source.wins
                WHEN NOT MATCHED THEN
                    INSERT (user_id, league_id, year_id, points, winner_correct, correct_score, wins)
                    VALUES (source.user_id, source.league_id, source.year_id, source.points, source.winner_correct, source.correct_score, source.wins);
            """, (user_id, league_id, year_id, season_points, season_winner_correct, season_correct_score, season_wins))

            conn.commit()

            return jsonify({'message': 'Matchup stats saved successfully!'}), 201

if __name__ == '__main__':
    app.run(debug=True)
