import pandas as pd
import glob
import os

# Set working directory
data_dir = r"C:\Prediction_Models\ManArs"

# Get all CSV files in directory
csv_files = glob.glob(os.path.join(data_dir, "*.csv"))

# Load and combine all CSVs
df_list = []
for file in csv_files:
    df = pd.read_csv(file)
    df_list.append(df)

# Combine into single DataFrame
matches_df = pd.concat(df_list, ignore_index=True)

# Show first few rows
print(matches_df.head())

# Save combined file
combined_path = os.path.join(data_dir, "combined_matches.csv")
matches_df.to_csv(combined_path, index=False)
print(f"Combined CSV saved at {combined_path}")

