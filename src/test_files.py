import pandas as pd 
import os

csv_path = "data/emergency_department_data.csv"

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    print("CSV Loaded Successfully")
    print("-" * 30)
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print("-" * 30)
    print(df.head())
else:
    print(f"Error: {csv_path} missing. Run the generator script first.")
