
import pandas as pd

# Read NHANES DAT file using fixed-width format (FWF)
df = pd.read_fwf(
    "C:\data\lab.dat" ,   # your file name
    widths=[8,2,2,4,1,1],   # example widths (change based on codebook)
    names=["SEQN","AGE","GENDER","RACE","etc"]  # column names (from codebook)
)

print(df.head())
