IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'projectionsDatabase')
BEGIN
    CREATE DATABASE projectionsDatabase;
END

USE projectionsDatabase;

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'userTable')
BEGIN
    CREATE TABLE userTable (
        user_id INT PRIMARY KEY IDENTITY(1,1),
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_login DATETIME
    );
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'leagueTable')
BEGIN
    CREATE TABLE leagueTable (
        league_id INT PRIMARY KEY IDENTITY(1,1),
        league_name VARCHAR(30) NOT NULL,
        lm_user_id INT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_private BIT DEFAULT 0,
        max_members INT DEFAULT 10,
        FOREIGN KEY (lm_user_id) REFERENCES userTable(user_id)
    );
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'userLeagueRelationTable')
BEGIN
    CREATE TABLE userLeagueRelationTable (
        user_league_id INT PRIMARY KEY IDENTITY (1,1),
        user_id INT NOT NULL,
        league_id INT NOT NULL,
        team_picture VARBINARY(MAX),
        team_name VARCHAR(30) NOT NULL,
        is_lm BIT DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES userTable(user_id),
        FOREIGN KEY (league_id) REFERENCES leagueTable(league_id),
        CONSTRAINT uc_league_manager UNIQUE (league_id, is_lm)
    );
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'nflTeamTable')
BEGIN
    CREATE TABLE nflTeamTable (
        team_id INT PRIMARY KEY IDENTITY (1,1),
        team_name VARCHAR(30) UNIQUE NOT NULL,
        team_abv VARCHAR(3) UNIQUE NOT NULL,
        team_logo VARBINARY(MAX) NOT NULL,
        team_color_code VARCHAR(7) NOT NULL
    );
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'nflScheduleTable')
BEGIN
    CREATE TABLE nflScheduleTable (
        schedule_id INT PRIMARY KEY IDENTITY (1,1),
        year INT NOT NULL,
        week INT NOT NULL,
        game INT NOT NULL,
        team_1_abv VARCHAR(3) NOT NULL,
        team_2_abv VARCHAR(3) NOT NULL,
        FOREIGN KEY (team_1_abv) REFERENCES nflTeamTable(team_abv),
        FOREIGN KEY (team_2_abv) REFERENCES nflTeamTable(team_abv)
    );
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'predictionTable')
BEGIN
    CREATE TABLE predictionTable (
        prediction_id INT PRIMARY KEY IDENTITY (1,1),
        user_id INT NOT NULL,
        schedule_id INT NOT NULL,
        league_id INT NOT NULL,
        p_score_team_1 INT NOT NULL,
        p_score_team_2 INT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES userTable(user_id),
        FOREIGN KEY (schedule_id) REFERENCES nflScheduleTable(schedule_id),
        FOREIGN KEY (league_id) REFERENCES leagueTable(league_id)
    );
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'actualScoreTable')
BEGIN
    CREATE TABLE actualScoreTable (
        actual_id INT PRIMARY KEY IDENTITY (1,1),
        schedule_id INT NOT NULL,
        a_score_team_1 INT NOT NULL,
        a_score_team_2 INT NOT NULL,
        FOREIGN KEY (schedule_id) REFERENCES nflScheduleTable(schedule_id)
    );
END

IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'nflScheduleTable' AND COLUMN_NAME = 'year')
BEGIN
    EXEC sp_rename 'nflScheduleTable.year', 'year_id', 'COLUMN';
END

IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'nflScheduleTable' AND COLUMN_NAME = 'week')
BEGIN
    EXEC sp_rename 'nflScheduleTable.week', 'week_id', 'COLUMN';
END

IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'nflScheduleTable' AND COLUMN_NAME = 'game')
BEGIN
    EXEC sp_rename 'nflScheduleTable.game', 'game_id', 'COLUMN';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'UC_Week_Game' AND object_id = OBJECT_ID('nflScheduleTable'))
BEGIN
    ALTER TABLE nflScheduleTable
    ADD CONSTRAINT UC_Week_Game UNIQUE (week_id, game_id);
END

IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'nflTeamTable' AND COLUMN_NAME = 'team_logo' AND DATA_TYPE = 'varbinary')
BEGIN
    ALTER TABLE nflTeamTable
    ALTER COLUMN team_logo VARCHAR(255) NOT NULL;
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'onDaysTable')
BEGIN
    CREATE TABLE onDaysTable (
        on_id INT PRIMARY KEY IDENTITY (1,1),
        year_id INT NOT NULL,
        week_id INT NOT NULL,
        day_id VARCHAR(2) NOT NULL,
        start_date_time DATETIME2 UNIQUE NOT NULL,
        end_date_time DATETIME2 UNIQUE NOT NULL
    );
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'matchupStatsTable')
BEGIN
    CREATE TABLE matchupStatsTable (
        matchup_stats_id INT PRIMARY KEY IDENTITY (1,1),
        schedule_id INT NOT NULL,
        user_id INT NOT NULL,
        league_id INT NOT NULL,
        year_id INT NOT NULL,
        week_id INT NOT NULL,
        points INT NOT NULL,
        winner_correct BIT NOT NULL,
        correct_score BIT NOT NULL,
        FOREIGN KEY (schedule_id) REFERENCES nflScheduleTable(schedule_id),
        FOREIGN KEY (user_id) REFERENCES userTable(user_id),
        FOREIGN KEY (league_id) REFERENCES leagueTable(league_id)
    );
END

ALTER TABLE matchupStatsTable
ALTER COLUMN points DECIMAL(4, 2) NOT NULL;

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'weeklyStatsTable')
BEGIN
    CREATE TABLE weeklyStatsTable (
        weekly_stats_id INT PRIMARY KEY IDENTITY (1,1),
        user_id INT NOT NULL,
        league_id INT NOT NULL,
        year_id INT NOT NULL,
        week_id INT NOT NULL,
        points DECIMAL(5, 2) NOT NULL,
        winner_correct BIT NOT NULL,
        correct_score BIT NOT NULL,
        win BIT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES userTable(user_id),
        FOREIGN KEY (league_id) REFERENCES leagueTable(league_id)
    );
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'seasonStatsTable')
BEGIN
    CREATE TABLE seasonStatsTable (
        season_stats_id INT PRIMARY KEY IDENTITY (1,1),
        user_id INT NOT NULL,
        league_id INT NOT NULL,
        year_id INT NOT NULL,
        points DECIMAL(6, 2) NOT NULL,
        winner_correct BIT NOT NULL,
        correct_score BIT NOT NULL,
        wins INT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES userTable(user_id),
        FOREIGN KEY (league_id) REFERENCES leagueTable(league_id)
    );
END

ALTER TABLE weeklyStatsTable
ALTER COLUMN winner_correct INT NOT NULL;

ALTER TABLE weeklyStatsTable
ALTER COLUMN correct_score INT NOT NULL;

ALTER TABLE seasonStatsTable
ALTER COLUMN winner_correct INT NOT NULL;

ALTER TABLE seasonStatsTable
ALTER COLUMN correct_score INT NOT NULL;

ALTER TABLE userLeagueRelationTable
ALTER COLUMN team_picture VARCHAR(255) NOT NULL;

ALTER TABLE userLeagueRelationTable
ALTER COLUMN team_name VARCHAR(20) NOT NULL;

ALTER TABLE leagueTable
ALTER COLUMN is_private BIT NOT NULL;

ALTER TABLE leagueTable
ALTER COLUMN max_members INT NOT NULL;

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'leagueTable' AND COLUMN_NAME = 'league_pass')
BEGIN
    ALTER TABLE leagueTable
    ADD league_pass INT,
    CONSTRAINT CK_league_pass CHECK (
        (is_private = 0 AND league_pass IS NULL) OR
        (is_private = 1 AND league_pass BETWEEN 0 AND 9999)
    );
END

IF NOT EXISTS (SELECT * FROM sys.sequences WHERE name = 'KeySequence')
BEGIN
    CREATE SEQUENCE KeySequence
    AS INT
    START WITH 1
    INCREMENT BY 1;
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'userTable')
BEGIN
    CREATE TABLE userTable (
        user_id INT PRIMARY KEY DEFAULT NEXT VALUE FOR KeySequence,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_login DATETIME
    );
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'actualScoreTable')
BEGIN
    CREATE TABLE actualScoreTable (
        actual_id INT PRIMARY KEY DEFAULT NEXT VALUE FOR KeySequence,
        schedule_id INT NOT NULL,
        a_score_team_1 INT NOT NULL,
        a_score_team_2 INT NOT NULL,
        FOREIGN KEY (schedule_id) REFERENCES nflScheduleTable(schedule_id)
    );
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'leagueTable')
BEGIN
    CREATE TABLE leagueTable (
        league_id INT PRIMARY KEY DEFAULT NEXT VALUE FOR KeySequence,
        league_name VARCHAR(30) NOT NULL,
        lm_user_id INT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_private BIT DEFAULT 0,
        max_members INT DEFAULT 10,
        league_pass INT,
        CONSTRAINT CK_league_pass CHECK (
            (is_private = 0 AND league_pass IS NULL) OR
            (is_private = 1 AND league_pass BETWEEN 0 AND 9999)
        ),
        FOREIGN KEY (lm_user_id) REFERENCES userTable(user_id)
    );
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'userLeagueRelationTable')
BEGIN
    CREATE TABLE userLeagueRelationTable (
        user_league_id INT PRIMARY KEY DEFAULT NEXT VALUE FOR KeySequence,
        user_id INT NOT NULL,
        league_id INT NOT NULL,
        team_picture VARCHAR(255) NOT NULL,
        team_name VARCHAR(20) NOT NULL,
        is_lm BIT DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES userTable(user_id),
        FOREIGN KEY (league_id) REFERENCES leagueTable(league_id),
        CONSTRAINT uc_league_manager UNIQUE (league_id, is_lm)
    );
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'predictionTable')
BEGIN
    CREATE TABLE predictionTable (
        prediction_id INT PRIMARY KEY DEFAULT NEXT VALUE FOR KeySequence,
        user_id INT NOT NULL,
        schedule_id INT NOT NULL,
        league_id INT NOT NULL,
        p_score_team_1 INT NOT NULL,
        p_score_team_2 INT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES userTable(user_id),
        FOREIGN KEY (schedule_id) REFERENCES nflScheduleTable(schedule_id),
        FOREIGN KEY (league_id) REFERENCES leagueTable(league_id)
    );
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'matchupStatsTable')
BEGIN
    CREATE TABLE matchupStatsTable (
        matchup_stats_id INT PRIMARY KEY DEFAULT NEXT VALUE FOR KeySequence,
        schedule_id INT NOT NULL,
        user_id INT NOT NULL,
        league_id INT NOT NULL,
        year_id INT NOT NULL,
        week_id INT NOT NULL,
        points DECIMAL(4, 2) NOT NULL,
        winner_correct BIT NOT NULL,
        correct_score BIT NOT NULL,
        FOREIGN KEY (schedule_id) REFERENCES nflScheduleTable(schedule_id),
        FOREIGN KEY (user_id) REFERENCES userTable(user_id),
        FOREIGN KEY (league_id) REFERENCES leagueTable(league_id)
    );
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'weeklyStatsTable')
BEGIN
    CREATE TABLE weeklyStatsTable (
        weekly_stats_id INT PRIMARY KEY DEFAULT NEXT VALUE FOR KeySequence,
        user_id INT NOT NULL,
        league_id INT NOT NULL,
        year_id INT NOT NULL,
        week_id INT NOT NULL,
        points DECIMAL(5, 2) NOT NULL,
        winner_correct INT NOT NULL,
        correct_score INT NOT NULL,
        win BIT NULL,
        FOREIGN KEY (user_id) REFERENCES userTable(user_id),
        FOREIGN KEY (league_id) REFERENCES leagueTable(league_id)
    );
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'seasonStatsTable')
BEGIN
    CREATE TABLE seasonStatsTable (
        season_stats_id INT PRIMARY KEY DEFAULT NEXT VALUE FOR KeySequence,
        user_id INT NOT NULL,
        league_id INT NOT NULL,
        year_id INT NOT NULL,
        points DECIMAL(6, 2) NOT NULL,
        winner_correct INT NOT NULL,
        correct_score INT NOT NULL,
        wins INT NULL,
        FOREIGN KEY (user_id) REFERENCES userTable(user_id),
        FOREIGN KEY (league_id) REFERENCES leagueTable(league_id)
    );
END

ALTER TABLE userLeagueRelationTable
DROP CONSTRAINT uc_league_manager;

CREATE UNIQUE INDEX idx_unique_league_manager
ON userLeagueRelationTable (league_id)
WHERE is_lm = 1;
