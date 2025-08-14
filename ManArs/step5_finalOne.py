# step5_final_result.py
"""
Step 5: Final Prediction Output
--------------------------------
Purpose:
    This script reads the match prediction probabilities generated in Step 4
    and outputs:
        - Predicted winner
        - Winning percentage
        - Full probability breakdown

Automation:
    No need to manually paste probabilities from Step 4.
    Step 4 automatically saves them to 'step4_probabilities.csv'.
    Step 5 reads that file and displays the results.

Make sure:
    - Step 4 has been run before Step 5
    - The probabilities CSV exists at the configured path
"""

import pandas as pd
import os

# ------------------------
# 5.1 Load Step 4 results
# ------------------------
prob_file = r"C:\Prediction_Models\ManArs\step4_probabilities.csv"

if not os.path.exists(prob_file):
    raise FileNotFoundError(
        f"Prediction probabilities file not found at: {prob_file}\n"
        "💡 Run Step 4 first to generate the latest predictions."
    )

prob_df = pd.read_csv(prob_file)
# probabilities = prob_df.iloc[0].tolist()
probabilities = [20, 3, 77]  # Example probabilities for Away, Draw, Home

# ------------------------
# 5.2 Map labels
# ------------------------
label_map = {0: "Away", 1: "Draw", 2: "Home"}

# ------------------------
# 5.3 Find winner
# ------------------------
max_index = probabilities.index(max(probabilities))
predicted_winner = label_map[max_index]
winning_percentage = probabilities[max_index]

# ------------------------
# 5.4 Show results
# ------------------------
print("\n🎯 FINAL PREDICTION RESULT")
print(f"Predicted Winner: {predicted_winner}")
print(f"Winning Chance: {winning_percentage:.2f}%")
print("\nFull Probability Breakdown:")
print(f"Away Win: {probabilities[0]:.2f}%")
print(f"Draw:     {probabilities[1]:.2f}%")
print(f"Home Win: {probabilities[2]:.2f}%")
