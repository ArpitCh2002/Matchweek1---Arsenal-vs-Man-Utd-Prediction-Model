"""
Step 3: Model Building & Tuning
Goal: Train a model to predict the winner of Arsenal vs Man United game
      and output win probability breakdown.
"""

# 3.1 Import Libraries
# Why: We need pandas for data handling, sklearn for model building, numpy for numerical operations
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# 3.2 Load Data
# Why: We use the cleaned 'features.csv' from Step 2 as our prepared dataset
df = pd.read_csv("features.csv")
print(f"✅ Data loaded successfully with shape: {df.shape}")

def get_winner(row):
    if row['FTHG'] > row['FTAG']:
        return "Home"
    elif row['FTHG'] < row['FTAG']:
        return "Away"
    else:
        return "Draw"

df['match_winner'] = df.apply(get_winner, axis=1)

df.to_csv("features.csv", index=False)
print("✅ match_winner column added successfully!")

# 3.3 Define Target & Features
# Why: We separate the column we want to predict (target) from input features
# Assuming 'match_winner' column exists: 'Home', 'Away', 'Draw'
target_column = "match_winner"
# Include ELO & bookmaker probs in the training set
feature_cols = [col for col in df.columns if col not in [target_column, 'home_team', 'away_team', 'date']]
X = df[feature_cols]
y = df[target_column]

# Optional: Drop non-numeric columns or encode them
X = pd.get_dummies(X, drop_first=True)

# 3.4 Split into Train/Test Sets
# Why: To evaluate how well our model works on unseen data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"📊 Training size: {X_train.shape}, Test size: {X_test.shape}")

# 3.5 Initialize Base Model
# Why: RandomForest works well for tabular sports data without heavy preprocessing
rf = RandomForestClassifier(random_state=42)

# 3.6 Hyperparameter Tuning
# Why: To find the best combination of parameters for higher accuracy
param_grid = {
    "n_estimators": [100, 200, 300],
    "max_depth": [None, 10, 20],
    "min_samples_split": [2, 5],
    "min_samples_leaf": [1, 2]
}
grid_search = GridSearchCV(rf, param_grid, cv=3, scoring="accuracy", n_jobs=-1, verbose=2)
grid_search.fit(X_train, y_train)
best_model = grid_search.best_estimator_
print(f"🏆 Best Parameters: {grid_search.best_params_}")

# 3.7 Evaluate Model
# Why: To see how well the tuned model predicts results on new data
y_pred = best_model.predict(X_test)
y_pred_proba = best_model.predict_proba(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Model Accuracy: {accuracy:.2%}")
print("\n📄 Classification Report:\n", classification_report(y_test, y_pred))

# 3.8 Example Prediction for Arsenal vs Man United
# Why: Final goal — predict this match result with win probability
# NOTE: Replace the values below with actual match-specific features
example_match = X_test.iloc[[0]]  # Using a sample row for now
predicted_winner = best_model.predict(example_match)[0]
predicted_proba = best_model.predict_proba(example_match)[0]

# Map probabilities to classes
class_probabilities = dict(zip(best_model.classes_, predicted_proba))

print("\n🎯 Prediction for Arsenal vs Man United:")
print(f"Predicted Winner: {predicted_winner}")
print("Win Probability Breakdown:")
for outcome, prob in class_probabilities.items():
    print(f"{outcome}: {prob:.2%}")
