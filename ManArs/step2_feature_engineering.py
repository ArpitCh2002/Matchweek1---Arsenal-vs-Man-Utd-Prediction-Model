import pandas as pd
import numpy as np

# New: For ELO ratings
def initialize_elo(df, base_rating=1500):
    teams = pd.unique(df[['HomeTeam', 'AwayTeam']].values.ravel('K'))
    elo_dict = {team: base_rating for team in teams}
    return elo_dict

def update_elo(elo_dict, home, away, home_score, away_score, k=20):
    expected_home = 1 / (1 + 10 ** ((elo_dict[away] - elo_dict[home]) / 400))
    expected_away = 1 - expected_home

    if home_score > away_score:
        result_home = 1
        result_away = 0
    elif home_score < away_score:
        result_home = 0
        result_away = 1
    else:
        result_home = 0.5
        result_away = 0.5

    elo_dict[home] += k * (result_home - expected_home)
    elo_dict[away] += k * (result_away - expected_away)

def add_elo_ratings(df):
    elo_dict = initialize_elo(df)
    home_elo_list = []
    away_elo_list = []

    for _, row in df.iterrows():
        home = row['HomeTeam']
        away = row['AwayTeam']

        home_elo_list.append(elo_dict[home])
        away_elo_list.append(elo_dict[away])

        update_elo(elo_dict, home, away, row['FTHG'], row['FTAG'])

    df['home_elo'] = home_elo_list
    df['away_elo'] = away_elo_list
    return df

data_path = r"C:\Prediction_Models\ManArs\combined_matches.csv"
output_path = r"C:\Prediction_Models\ManArs\features.csv"

# 2.1 Load data
# What: Read combined_matches.csv into a pandas DataFrame, check for missing values and data types.
#Why: To ensure data is clean and ready for feature creation, and identify any issues early.

df = pd.read_csv(data_path, parse_dates=["Date"])

# Explicit date conversion to avoid string issues
df['Date'] = pd.to_datetime(df['Date'], errors='coerce', dayfirst=True)

# 2.2 Standardize columns (rename if needed)
#What:
# Rename columns if needed (to consistent names)
# Convert date columns to datetime objects
# Fill or remove missing values logically (e.g., fill missing shots with 0)
# Why: Models require consistent column names and correct data types to work without errors and interpret features correctly.

rename_map = {
    'HomeGoals': 'FTHG',
    'AwayGoals': 'FTAG',
    'Result': 'FTR'
}
df = df.rename(columns=rename_map)

# Fill missing numeric columns with 0 (for shots, fouls etc.)
numeric_cols = ['FTHG','FTAG','ShotsHome','ShotsAway','ShotsOnTargetHome','ShotsOnTargetAway']
for col in numeric_cols:
    if col in df.columns:
        df[col] = df[col].fillna(0)

# 2.3 Create target label (0=Home Win,1=Draw,2=Away Win)
#What: Add a numeric target variable result_label based on match result:
# Home Win = 0
# Draw = 1
# Away Win = 2
# Why: ML models need numeric labels to learn classification.

def result_to_label(r):
    if r == 'H': return 0
    if r == 'D': return 1
    if r == 'A': return 2
    return np.nan

# If your Result column uses strings like 'H', 'D', 'A'
if 'FTR' in df.columns:
    df['result_label'] = df['FTR'].map(result_to_label)
else:
    raise ValueError("Result column (FTR) missing")

# Sort by date for rolling calculations
df = df.sort_values("Date").reset_index(drop=True)

# 2.4 Rolling form features (last 5 matches per team)
#What: For each team, calculate recent form statistics using the last 5 matches before the current game:
#Average points
#Average goals scored and conceded
#Average shots and shots on target
#Why: Recent performance (form) is predictive of future results — this captures momentum and current strength.

def add_rolling_features(df, window=5):
    df = df.copy()
    teams = pd.unique(df[['HomeTeam', 'AwayTeam']].values.ravel())

    # Initialize rolling stats dictionaries for each team
    rolling_stats = {team: {'points': [], 'goals_for': [], 'goals_against': [], 'shots': [], 'shots_on_target': []} for team in teams}

    # Prepare lists to store features for each row
    home_points_avg, away_points_avg = [], []
    home_goals_avg, away_goals_avg = [], []
    home_shots_avg, away_shots_avg = [], []
    home_sot_avg, away_sot_avg = [], []

    # Helper to compute points from result
    def get_points(result, is_home):
        if result == 'H':
            return 3 if is_home else 0
        elif result == 'A':
            return 0 if is_home else 3
        elif result == 'D':
            return 1
        else:
            return 0

    for idx, row in df.iterrows():
        home = row['HomeTeam']
        away = row['AwayTeam']

        # Compute rolling averages for home team
        home_stats = rolling_stats[home]
        if len(home_stats['points']) >= window:
            home_points_avg.append(np.mean(home_stats['points'][-window:]))
            home_goals_avg.append(np.mean(home_stats['goals_for'][-window:]))
            home_shots_avg.append(np.mean(home_stats['shots'][-window:]))
            home_sot_avg.append(np.mean(home_stats['shots_on_target'][-window:]))
        else:
            home_points_avg.append(np.nan)
            home_goals_avg.append(np.nan)
            home_shots_avg.append(np.nan)
            home_sot_avg.append(np.nan)

        # Compute rolling averages for away team
        away_stats = rolling_stats[away]
        if len(away_stats['points']) >= window:
            away_points_avg.append(np.mean(away_stats['points'][-window:]))
            away_goals_avg.append(np.mean(away_stats['goals_for'][-window:]))
            away_shots_avg.append(np.mean(away_stats['shots'][-window:]))
            away_sot_avg.append(np.mean(away_stats['shots_on_target'][-window:]))
        else:
            away_points_avg.append(np.nan)
            away_goals_avg.append(np.nan)
            away_shots_avg.append(np.nan)
            away_sot_avg.append(np.nan)

        # Update rolling stats with current match
        home_points = get_points(row['FTR'], True)
        away_points = get_points(row['FTR'], False)
        rolling_stats[home]['points'].append(home_points)
        rolling_stats[home]['goals_for'].append(row['FTHG'])
        rolling_stats[home]['goals_against'].append(row['FTAG'])
        rolling_stats[home]['shots'].append(row.get('ShotsHome', 0))
        rolling_stats[home]['shots_on_target'].append(row.get('ShotsOnTargetHome', 0))

        rolling_stats[away]['points'].append(away_points)
        rolling_stats[away]['goals_for'].append(row['FTAG'])
        rolling_stats[away]['goals_against'].append(row['FTHG'])
        rolling_stats[away]['shots'].append(row.get('ShotsAway', 0))
        rolling_stats[away]['shots_on_target'].append(row.get('ShotsOnTargetAway', 0))

    df['home_points_last5'] = home_points_avg
    df['away_points_last5'] = away_points_avg
    df['home_goals_last5'] = home_goals_avg
    df['away_goals_last5'] = away_goals_avg
    df['home_shots_last5'] = home_shots_avg
    df['away_shots_last5'] = away_shots_avg
    df['home_sot_last5'] = home_sot_avg
    df['away_sot_last5'] = away_sot_avg

    return df

df = add_rolling_features(df)

# 2.5 Compute Elo ratings (simple version)
# What: Compute an Elo rating per team iteratively through the dataset, updating after every match.
# Why: Elo ratings are a strong way to represent team strength relative to opponents, accounting for match importance and margin.

def compute_elo(df, k=20, base_elo=1500):
    teams = pd.unique(df[['HomeTeam', 'AwayTeam']].values.ravel())
    elo = {team: base_elo for team in teams}

    elo_home, elo_away = [], []

    for _, row in df.iterrows():
        th = row['HomeTeam']
        ta = row['AwayTeam']

        # Calculate expected result for home
        Eh = 1 / (1 + 10 ** ((elo[ta] - elo[th]) / 400))

        # Actual result score for home team
        if row['FTR'] == 'H':
            Sh = 1
        elif row['FTR'] == 'D':
            Sh = 0.5
        else:
            Sh = 0

        # Update elo
        elo[th] += k * (Sh - Eh)
        elo[ta] += k * ((1 - Sh) - (1 - Eh))

        elo_home.append(elo[th])
        elo_away.append(elo[ta])

    df['elo_home'] = elo_home
    df['elo_away'] = elo_away
    df['elo_diff'] = df['elo_home'] - df['elo_away']

    return df

df = compute_elo(df)

# 2.6 Calculate rest days
#What: Compute the number of days since each team’s last match.
#Why: Rest and fatigue impact performance; teams with more rest tend to perform better.

def add_rest_days(df):
    df = df.copy()
    df['days_rest_home'] = np.nan
    df['days_rest_away'] = np.nan

    last_game_date = {}

    for idx, row in df.iterrows():
        home = row['HomeTeam']
        away = row['AwayTeam']
        date = row['Date']

        # Calculate rest days for home
        if home in last_game_date:
            df.at[idx, 'days_rest_home'] = (date - last_game_date[home]).days
        else:
            df.at[idx, 'days_rest_home'] = np.nan
        last_game_date[home] = date

        # Calculate rest days for away
        if away in last_game_date:
            df.at[idx, 'days_rest_away'] = (date - last_game_date[away]).days
        else:
            df.at[idx, 'days_rest_away'] = np.nan
        last_game_date[away] = date

    # Difference in rest days
    df['rest_days_diff'] = df['days_rest_home'] - df['days_rest_away']

    return df

df = add_rest_days(df)

# 2.7 Odds implied probabilities (if odds columns exist)
#What: If you have betting odds (e.g., from B365H, B365D, B365A), convert them to implied probabilities.
#Why: Odds reflect expert and market expectations; including them helps improve predictions.

if set(['B365H', 'B365D', 'B365A']).issubset(df.columns):
    df['odds_home_prob'] = 1 / df['B365H']
    df['odds_draw_prob'] = 1 / df['B365D']
    df['odds_away_prob'] = 1 / df['B365A']
    # Normalize probabilities to sum to 1 (remove bookmaker margin)
    total_prob = df['odds_home_prob'] + df['odds_draw_prob'] + df['odds_away_prob']
    df['odds_home_prob'] /= total_prob
    df['odds_draw_prob'] /= total_prob
    df['odds_away_prob'] /= total_prob

def add_bookmaker_probs(df):
    for col in ['B365H', 'B365D', 'B365A']:
        if col in df.columns:
            prob_col = col + '_prob'
            df[prob_col] = 1 / df[col]
    return df

# Apply new features
features_df = add_elo_ratings(df)
features_df = add_bookmaker_probs(features_df)


# Save processed features
features_df.to_csv(output_path, index=False)
print(f"Feature engineered data saved to {output_path}")

