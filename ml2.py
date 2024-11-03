import pandas as pd

# Load only the first 20 rows (including header)
file_path = 'accepted_2007_to_2018Q4.csv'
df = pd.read_csv(file_path, nrows=20)

# Save these rows to a new CSV file
df.to_csv('sample_data.csv', index=False)

print("Saved header and first 20 rows to sample_data.csv.")
