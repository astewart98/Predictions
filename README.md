# ScoreCast

ScoreCast is a **Score Prediction** game where users guess NFL scores and earn points based on their accuracy. The application tracks game results and displays player rankings in real-time.

Check out the live application here: [ScoreCast](https://scorecast1-ehayckcugzaja0gh.eastus2-01.azurewebsites.net)

## Technologies Used

ScoreCast is a full-stack application built with:
- **Flask**
- **Python**
- **pymssql**
- **JavaScript**
- **Docker**
- **Microsoft Azure Cloud Services**

## Notable Features

- **Account Management**: Create an account to track your leagues and teams.
- **User Authentication**: Secure login and registration with validation checks.
- **Leagues**: Create or join private/public leagues with friends, up to 10 leagues per account.
- **Team Management**: Unique team creation per league, with real-time data updates.
- **Accurate NFL Schedule**: Displays the current season’s matchups and game results.
- **Prediction Logging**: Submit score predictions for upcoming games.
- **Live Updates**: NFL game scores and user rankings update in real-time.
- **Points System**: Earn points based on proximity to the actual game scores.
- **Comprehensive Database**: Stores all user data and live game information.
- **Responsive Design**: Optimized for both desktop and mobile devices.

## Instructions

Visit the live application through the provided link. Use these test credentials to explore:
- **Email**: `test@email.com`
- **Password**: `1234`

Once logged in, click on "Test Team" in the "Test League" to explore the app.

---

### Key Features to Explore

#### Account Page (First Page After Login)
- **League Information**: Each league is displayed with its name, ID, and join code for easy sharing with friends.
- **Season Stats**: View your team’s season stats for each league.
- **New League Creation**: Easily create a new league or join a friend’s league with validation checks to prevent invalid entries.
- **Join a League**: A built-in validation system ensures that only existing leagues can be joined.

#### League Page (After Selecting a League from the Account Page)
- **Opponent Stats**: View your opponents' season stats using the "Opponent Stats" dropdown menu.
- **Week Carousel**: Navigate through previous and future NFL weeks.
  - **Past Weeks**: See your predictions, actual scores, and points earned for each game and the week as a whole.
  - **Future Weeks**: Upcoming matchups are displayed, but predictions can only be made during the current week.
- **Week Recap**: Displays your win/loss status and weekly points, with a dropdown to view opponents' weekly stats.
- **Game Predictions**: 
  - Predicted score can be entered in the box right of the NFL team name.
    - Grayed scores represent the users prediction
    - Empty boxes are for future predictions.
  - Actual score is displayed below the NFL team name.
    - Only present during live or past games.
  - **Highlighting System**:
    - Team containers are highlighted based on users predicted winner.
    - **Blue**: Pending game result.
    - **Green**: Correctly predicted winner.
    - **Red**: Incorrectly predicted winner.
    - **Exact Scores**: Users predicted score highlighted in green if guessed correctly.
- **Submit Predictions**: Available on current weeks where predictions are yet to be made (hidden in presentation mode).
- **Navigation Menu**: Access your account page or sign out.

---

### Scoring System

Points are awarded based on the accuracy of your predictions:
- **Correct Winner**: 2 points
- **Exact Score**: 4 points
- **Proximity Points**:
  - **3 or 7 points away**: 2 points
  - **6 or 8 points away**: 1 point
  - **1-2 or 4-5 points away**: 0.5 points

---

### NOTE

- Some features may be limited due to current server capabilities
- All images, score data, and other elements are copyright of the NFL and ESPN and are used for educational purposes only. This project is not affiliated with or endorsed by the NFL or ESPN, and no financial gain is made from its use.

---

Thank you for your time!
