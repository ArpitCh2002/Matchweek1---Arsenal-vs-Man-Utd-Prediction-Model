# step4_model_evaluation.py
# =========================
# This script evaluates the trained model to check how well it generalizes
# and to make sure it's not just memorizing old matches.

import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

# -------------------------
# 4.1 Load Prepared Features
# -------------------------
# Why: We want to use the processed dataset from Step 2 that contains all the features.
features_file = r"C:\Prediction_Models\ManArs\features.csv"
df = pd.read_csv(features_file)

# -------------------------
# 4.2 Define Target & Features
# -------------------------
# Why: 'match_winner' is our label, the rest are inputs for the model.
target_column = 'match_winner'

# Ensure target column exists
assert target_column in df.columns, f"Target column '{target_column}' not found in dataset."

# Remove non-numeric columns except the target
df = df.drop(columns=[col for col in df.columns if df[col].dtype == 'object' and col != target_column])

# Now separate features and target
X = df.drop(columns=[target_column])
y = df[target_column]

# -------------------------
# 4.3 Train/Test Split
# -------------------------
# Why: This allows us to test the model on unseen data to measure generalization.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# -------------------------
# 4.4 Train Model
# -------------------------
# Why: We train the model on training data only.
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# -------------------------
# 4.5 Predict on Test Data
# -------------------------
# Why: See how the model performs on new data it hasn't seen.
y_pred = model.predict(X_test)

# -------------------------
# 4.6 Evaluate Metrics
# -------------------------
# Why: Accuracy is one measure, but precision/recall/F1 give deeper insight.
print("🎯 Model Evaluation Results:")
print("-" * 40)
print("✅ Accuracy:", accuracy_score(y_test, y_pred))
print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred))
print("📌 Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# -------------------------
# 4.7 Cross-Validation
# -------------------------
# Why: Checks model performance stability across different splits of data.
cv_scores = cross_val_score(model, X, y, cv=5)
print("\n🔁 Cross-Validation Scores:", cv_scores)
print("📈 Average CV Score:", cv_scores.mean())

# -------------------------
# 4.8 Save the Trained Model
# -------------------------
# Why: To avoid retraining from scratch every time.
model_path = r"C:\Prediction_Models\ManArs\match_winner_model.pkl"
joblib.dump(model, model_path)
print(f"\n💾 Model saved to: {model_path}")

# -------------------------
# 4.9 Optional: Save Test Results
# -------------------------
# Why: Useful for reviewing which matches were predicted correctly/wrongly.
results_df = X_test.copy()
results_df['Actual'] = y_test
results_df['Predicted'] = y_pred
results_df.to_csv(r"C:\Prediction_Models\ManArs\model_test_results.csv", index=False)
print("📂 Test results saved to: C:\\Prediction_Models\\ManArs\\model_test_results.csv")


# -------------------------
# 4.10 Save Example Prediction Probabilities for Step 5
# -------------------------
# Pick one test match to demonstrate
if len(X_test) > 0:
    example_match_index = X_test.index[0]
    example_features = X_test.loc[example_match_index].values.reshape(1, -1)
    example_probabilities = model.predict_proba(example_features)[0] * 100  # Convert to %

    # Save to CSV so Step 5 can read it
    pd.DataFrame([example_probabilities], columns=["Away", "Draw", "Home"]).to_csv(
        r"C:\Prediction_Models\ManArs\step4_probabilities.csv",
        index=False
    )
    print("📂 Step 4 probabilities saved to: C:\\Prediction_Models\\ManArs\\step4_probabilities.csv")
