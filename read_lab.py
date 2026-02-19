import os
import pandas as pd
import re
import sys

print("DEBUG: Script started")

# ------------------------------------------
# Check files in directory
# ------------------------------------------
print("DEBUG: Files in directory:", os.listdir("."))

if not os.path.exists("lab.sas"):
    print("ERROR: lab.sas NOT FOUND")
    sys.exit()

if not os.path.exists("lab.dat"):
    print("ERROR: lab.dat NOT FOUND")
    sys.exit()

print("DEBUG: lab.sas and lab.dat found")

# ------------------------------------------
# 1. Parse SAS Layout File (lab.sas)
# ------------------------------------------
try:
    with open("lab.sas", "r", errors="ignore") as f:
        lines = f.readlines()
    print("DEBUG: SAS file read OK, total lines:", len(lines))
except Exception as e:
    print("ERROR reading SAS:", e)
    sys.exit()

var_names = []
colspecs = []

pattern = re.compile(r"(\w+)\s+(\d+)\s*-\s*(\d+)")

for line in lines:
    m = pattern.search(line)
    if m:
        name = m.group(1)
        start = int(m.group(2)) - 1
        end = int(m.group(3))
        var_names.append(name)
        colspecs.append((start, end))

print("DEBUG: extracted variable count:", len(var_names))

if len(var_names) == 0:
    print("ERROR: No variables extracted. SAS layout mismatch.")
    sys.exit()

# ------------------------------------------
# 2. Read the LAB file
# ------------------------------------------
try:
    print("DEBUG: Starting to read lab.dat... this may take 10–20 seconds")
    df = pd.read_fwf("lab.dat", colspecs=colspecs, names=var_names)
    print("DEBUG: Loaded LAB dataset:", df.shape)
except Exception as e:
    print("ERROR reading LAB.DAT:", e)
    sys.exit()

# ------------------------------------------
# (THIS IS WHERE YOUR NEW CODE GOES)
# 3. Extract FULL NUTRITION PANEL
# ------------------------------------------
nutrition_vars = [
    # Blood count
    "HGP", "HCT", "HGB", "RBCP", "PLTP", "MCVP",

    # Glucose & Diabetes
    "SGP", "SGP2", "SGP3",

    # Kidney markers
    "UAP", "UAP2", "CEP",

    # Electrolytes
    "NAPSI", "SKPSI", "CLPSI",

    # Liver Function
    "ALP", "SAP", "TSP", "TBP", "DBP", "ALBP",

    # Vitamins
    "VAP", "VEP", "VCP", "VBP", "FOP", "FEP",

    # Minerals
    "IRP", "FDP", "FERR", "ZNP",

    # Lipid Panel
    "TCP", "HDLP", "TRIGP", "LDLP",
]

available = [v for v in nutrition_vars if v in df.columns]
df_nutri = df[available].copy()

print("DEBUG: Selected nutrition biomarkers:", df_nutri.shape)



# ------------------------------------------
# 4. Save clean lab nutrition dataset
# ------------------------------------------
df_nutri.to_csv("lab_clean.csv", index=False)
print("Saved lab_clean.csv successfully!")
