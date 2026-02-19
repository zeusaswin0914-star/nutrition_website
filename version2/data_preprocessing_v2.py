"""
Data Preprocessing V2 - Dual Dataset Merge

Merges lab_clean_processed.csv and nhanes_real_with_calories.csv.
Handles column mapping, missing value imputation, and health status labeling.
"""

import pandas as pd
import numpy as np
import os
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import joblib

# Paths
LAB_DATA_PATH = r"c:\Users\USER\project\lab_clean_processed.csv"
NHANES_DATA_PATH = r"c:\Users\USER\project\nhanes_real_with_calories.csv"
PROCESSED_DATA_PATH = r"c:\Users\USER\project\version2\processed_data_v2.csv"
PREPROCESSOR_PATH = r"c:\Users\USER\project\version2\preprocessor_v2.pkl"

# Column Mapping (NHANES -> Lab Schema)
# Lab Schema: HGP, SGP, UAP, CEP, NAPSI, SKPSI, CLPSI, TBP, VAP, VEP, VCP, VBP, FOP, FEP, TCP
# NHANES likely has real names. We need to map them to these codes or standard names.
# For V2, we will use comprehensive standard names and map the Lab codes to them.

LAB_CODE_MAP = {
    'HGP': 'hemoglobin',
    'SGP': 'glucose', 
    'UAP': 'uric_acid', 
    'CEP': 'creatinine',
    'NAPSI': 'sodium',
    'SKPSI': 'potassium',
    'CLPSI': 'chloride',
    'TBP': 'bilirubin', 
    'VAP': 'alp', 
    'VEP': 'sgpt', 
    'VCP': 'sgot', 
    'VBP': 'vitamin_b12',
    'FOP': 'calcium', 
    'FEP': 'iron', 
    'TCP': 'total_cholesterol'
}

def load_and_merge_data():
    """Load both datasets and merge them into a single schema."""
    
    print("Loading datasets...")
    try:
        lab_df = pd.read_csv(LAB_DATA_PATH)
        nhanes_df = pd.read_csv(NHANES_DATA_PATH)
        
        print(f"Lab data shape: {lab_df.shape}")
        print(f"NHANES data shape: {nhanes_df.shape}")
        
        # 1. Standardize Lab Data Columns
        # Invert the map if keys are codes
        lab_df_renamed = lab_df.rename(columns=LAB_CODE_MAP)
        
        # Mapping NHANES columns (based on common names, adjusting as needed)
        nhanes_map = {
            'sex': 'gender', # encode later
            'fasting_glucose': 'glucose',
            'total_chol': 'total_cholesterol',
            'b12': 'vitamin_b12',
            # Add others as found in the csv
        }
        nhanes_df_renamed = nhanes_df.rename(columns=nhanes_map)
        
        # 3. Create Unified DataFrame
        common_cols = set(lab_df_renamed.columns).intersection(set(nhanes_df_renamed.columns))
        print(f"Common columns: {common_cols}")
        
        # We will prioritize the union of important columns
        target_cols = [
            'age', 'gender', 'height', 'weight', # Demographics
            'hemoglobin', 'glucose', 'total_cholesterol', 'ldl', 'hdl', 'triglycerides', # Basic Panel
            'creatinine', 'uric_acid', # Kidney
            'sodium', 'potassium', 'chloride', # Electrolytes
            'bilirubin', 'sgpt', 'sgot', 'alp', # Liver
            'calcium', 'iron', 'vitamin_b12', # Micro
            'calories' # Target
        ]
        
        # Initialize merged df
        merged_df = pd.DataFrame(columns=target_cols)
        
        # Append NHANES (High quality, has demographics)
        nhanes_subset = pd.DataFrame()
        for col in target_cols:
            if col in nhanes_df_renamed.columns:
                nhanes_subset[col] = nhanes_df_renamed[col]
            else:
                nhanes_subset[col] = np.nan
        
        # Map gender in NHANES (usually 1=Male, 2=Female or similar) to 0/1
        if 'gender' in nhanes_subset.columns:
             nhanes_subset['gender'] = nhanes_subset['gender'].apply(lambda x: 1 if str(x).lower() in ['1', 'm', 'male'] else 0)

        # Append Lab Data
        lab_subset = pd.DataFrame()
        for col in target_cols:
            if col in lab_df_renamed.columns:
                lab_subset[col] = lab_df_renamed[col]
            else:
                lab_subset[col] = np.nan
                
        # Combine
        combined_df = pd.concat([nhanes_subset, lab_subset], axis=0, ignore_index=True)
        
        print(f"Combined shape before cleaning: {combined_df.shape}")
        
        return combined_df

    except Exception as e:
        print(f"Error merging data: {e}")
        return pd.DataFrame()

def preprocess_and_label(df):
    """Clean data, impute missing values, and generate health labels."""
    
    if df.empty:
        return df
    
    # 1. Handling Missing Values
    # Demographics: Impute median for age/height/weight
    
    imputer = SimpleImputer(strategy='median')
    
    # Columns to impute
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
    
    # 2. Feature Engineering
    # BMI
    if 'weight' in df.columns and 'height' in df.columns:
        # Ensure height is in meters (if huge values, assume cm)
        df['height_m'] = df['height'].apply(lambda x: x / 100 if x > 3 else x)
        df['bmi'] = df['weight'] / (df['height_m'] ** 2)
        df['bmi'] = df['bmi'].fillna(df['bmi'].median())
    
    # 3. Generate Health Labels (Target for Classification)
    # 0: Healthy, 1: At Risk, 2: Action Needed
    
    def get_health_status(row):
        score = 0
        
        # Diabetes Risk
        if row['glucose'] > 125: score += 2
        elif row['glucose'] > 100: score += 1
        
        # Anemia Risk
        if row['hemoglobin'] < 12: score += 2
        
        # Heart Risk
        if row['total_cholesterol'] > 240: score += 2
        elif row['total_cholesterol'] > 200: score += 1
        
        if row['ldl'] > 160: score += 2
        elif row['ldl'] > 130: score += 1
        
        # Kidney
        if row['creatinine'] > 1.4: score += 2
        
        # Final Classification
        if score == 0: return 0 # Normal
        elif score <= 2: return 1 # At Risk
        else: return 2 # Deficient/Action Needed

    df['health_status'] = df.apply(get_health_status, axis=1)
    
    print("Health Status Distribution:")
    print(df['health_status'].value_counts())
    
    return df

if __name__ == "__main__":
    combined_df = load_and_merge_data()
    
    if not combined_df.empty:
        processed_df = preprocess_and_label(combined_df)
        
        # Save processed data
        processed_df.to_csv(PROCESSED_DATA_PATH, index=False)
        print(f"Processed data saved to {PROCESSED_DATA_PATH}")
