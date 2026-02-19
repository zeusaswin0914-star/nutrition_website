
import pandas as pd

# Replace with your actual file path
file_path = "C:\data\lab.dat"

# Try reading as space-separated first
try:
    df = pd.read_csv(file_path, delim_whitespace=True)
    print("Data loaded successfully as space-separated!")
except:
    # If error occurs, try as tab-separated
    try:
        df = pd.read_csv(file_path, sep="\t")
        print("Data loaded successfully as tab-separated!")
    except:
        # If still fails, try fixed-width
        df = pd.read_fwf(file_path)
        print("Data loaded successfully as fixed-width!")

# Show first 10 rows
print(df.head())

# Save to CSV
df.to_csv("dataset.csv", index=False)
print("CSV saved successfully!")

df.to_csv("C:/data/dataset.csv", index=False)

