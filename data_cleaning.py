"""
Data Cleaning Script for lab_clean.csv
Removes sentinel error values (88888, 888, etc.) and handles missing values
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Configuration
INPUT_FILE = "lab_clean.csv"
OUTPUT_FILE = "lab_clean_processed.csv"
REPORT_FILE = "data_cleaning_report.txt"

# Sentinel error values to detect and remove
SENTINEL_VALUES = [88888, 888, 8888, 88, -88888, -888, -8888]

def detect_sentinel_values(df):
    """Identify all sentinel error values in the dataset"""
    sentinels_found = {}
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            for sentinel in SENTINEL_VALUES:
                count = (df[col] == sentinel).sum()
                if count > 0:
                    if col not in sentinels_found:
                        sentinels_found[col] = {}
                    sentinels_found[col][sentinel] = count
    return sentinels_found

def clean_data(df):
    """
    Clean the dataset:
    1. Replace sentinel values with NaN
    2. Handle missing values (imputation)
    3. Remove duplicate rows
    """
    df_clean = df.copy()
    
    # Step 1: Replace sentinel values with NaN
    print("\n[STEP 1] Removing sentinel error values...")
    for col in df_clean.columns:
        if df_clean[col].dtype in ['float64', 'int64']:
            for sentinel in SENTINEL_VALUES:
                mask = df_clean[col] == sentinel
                count = mask.sum()
                if count > 0:
                    df_clean.loc[mask, col] = np.nan
                    print(f"  ✓ {col}: Replaced {count} instances of {sentinel} with NaN")
    
    # Step 2: Handle missing values
    print("\n[STEP 2] Handling missing values...")
    missing_before = df_clean.isnull().sum()
    
    # For each column, fill NaN with median (robust to outliers)
    for col in df_clean.columns:
        if df_clean[col].dtype in ['float64', 'int64']:
            missing_count = df_clean[col].isnull().sum()
            if missing_count > 0:
                median_val = df_clean[col].median()
                df_clean[col].fillna(median_val, inplace=True)
                print(f"  ✓ {col}: Filled {missing_count} missing values with median ({median_val:.2f})")
    
    # Step 3: Remove duplicate rows
    print("\n[STEP 3] Removing duplicate rows...")
    duplicates_before = df_clean.duplicated().sum()
    if duplicates_before > 0:
        df_clean = df_clean.drop_duplicates()
        print(f"  ✓ Removed {duplicates_before} duplicate rows")
    else:
        print(f"  ✓ No duplicates found")
    
    return df_clean, missing_before

def generate_report(df_original, df_clean, sentinels_found, missing_before):
    """Generate before/after comparison report"""
    report_lines = []
    
    report_lines.append("=" * 80)
    report_lines.append("DATA CLEANING REPORT - lab_clean.csv")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Dataset overview
    report_lines.append("DATASET OVERVIEW")
    report_lines.append("-" * 80)
    report_lines.append(f"Original rows:  {len(df_original)}")
    report_lines.append(f"Cleaned rows:   {len(df_clean)}")
    report_lines.append(f"Rows removed:   {len(df_original) - len(df_clean)}")
    report_lines.append(f"Columns:        {df_clean.shape[1]}\n")
    
    # Sentinel values found and removed
    if sentinels_found:
        report_lines.append("SENTINEL ERROR VALUES DETECTED & REMOVED")
        report_lines.append("-" * 80)
        for col in sorted(sentinels_found.keys()):
            report_lines.append(f"\n{col}:")
            for sentinel, count in sorted(sentinels_found[col].items()):
                report_lines.append(f"  {sentinel}: {count} occurrences replaced with NaN → median imputation")
        report_lines.append("")
    
    # Missing values statistics
    report_lines.append("\nMISSING VALUES - BEFORE & AFTER")
    report_lines.append("-" * 80)
    report_lines.append(f"{'Column':<10} {'Before':<12} {'After':<12} {'Status':<20}")
    report_lines.append("-" * 80)
    
    for col in df_original.columns:
        before = missing_before[col]
        after = df_clean[col].isnull().sum()
        status = "✓ CLEAN" if after == 0 else f"⚠ Still {after} missing"
        report_lines.append(f"{col:<10} {before:<12} {after:<12} {status:<20}")
    
    # Data quality metrics
    report_lines.append("\nDATA QUALITY METRICS")
    report_lines.append("-" * 80)
    completeness_before = ((len(df_original) * len(df_original.columns) - missing_before.sum()) / 
                          (len(df_original) * len(df_original.columns)) * 100)
    completeness_after = ((len(df_clean) * len(df_clean.columns) - df_clean.isnull().sum().sum()) / 
                         (len(df_clean) * len(df_clean.columns)) * 100)
    
    report_lines.append(f"Data completeness before: {completeness_before:.2f}%")
    report_lines.append(f"Data completeness after:  {completeness_after:.2f}%")
    report_lines.append(f"Improvement: {completeness_after - completeness_before:.2f}%\n")
    
    # Statistical summary
    report_lines.append("STATISTICAL SUMMARY (CLEANED DATA)")
    report_lines.append("-" * 80)
    report_lines.append(df_clean.describe().to_string())
    
    report_lines.append("\n" + "=" * 80)
    report_lines.append("✅ CLEANING COMPLETE")
    report_lines.append("=" * 80)
    
    return "\n".join(report_lines)

def main():
    """Main cleaning pipeline"""
    print("\n" + "=" * 80)
    print("DATA CLEANING PIPELINE - lab_clean.csv")
    print("=" * 80)
    
    # Load original data
    print(f"\n[LOAD] Reading {INPUT_FILE}...")
    df_original = pd.read_csv(INPUT_FILE)
    print(f"✓ Loaded {len(df_original)} rows × {len(df_original.columns)} columns")
    
    # Detect sentinel values
    print("\n[DETECT] Scanning for sentinel error values...")
    sentinels_found = detect_sentinel_values(df_original)
    if sentinels_found:
        print(f"✓ Found {len(sentinels_found)} columns with sentinel values:")
        for col in sentinels_found.keys():
            total = sum(sentinels_found[col].values())
            print(f"  - {col}: {total} total sentinel occurrences")
    else:
        print("✓ No sentinel values found")
    
    # Clean data
    print("\n[CLEAN] Starting data cleaning process...")
    df_clean, missing_before = clean_data(df_original)
    
    # Save cleaned data
    print(f"\n[SAVE] Writing cleaned data to {OUTPUT_FILE}...")
    df_clean.to_csv(OUTPUT_FILE, index=False)
    print(f"✓ Saved {len(df_clean)} cleaned rows")
    
    # Generate report
    print(f"\n[REPORT] Generating cleaning report...")
    report = generate_report(df_original, df_clean, sentinels_found, missing_before)
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✓ Report saved to {REPORT_FILE}")
    
    # Print summary
    print("\n" + report)
    
    print(f"\n[SUMMARY]")
    print(f"  Input:  {INPUT_FILE} ({len(df_original)} rows)")
    print(f"  Output: {OUTPUT_FILE} ({len(df_clean)} rows)")
    print(f"  Report: {REPORT_FILE}")
    print("\n✅ Cleaning pipeline complete!\n")

if __name__ == "__main__":
    main()
