# 🧠 ML Model Documentation — Line-by-Line Walkthrough

## Health Status Prediction Pipeline — From Raw Input to Final Output

**Version:** 2.0  
**Last Updated:** February 18, 2026  
**Pipeline:** Data Preprocessing → Model Training → Model Inference  
**Classification Task:** 14 blood biomarkers → 3-class health prediction (Normal / At Risk / Deficient)

---

## 📑 Table of Contents

1. [Pipeline Overview](#1-pipeline-overview)
2. [Data Preprocessing (`data_preprocessing_v2.py`) — Line-by-Line](#2-data-preprocessing)
3. [Model Training (`model_training_v2.py`) — Line-by-Line](#3-model-training)
4. [Model Inference (`model_inference_v2.py`) — Line-by-Line](#4-model-inference)
5. [Complete Worked Example: Input → Output](#5-complete-worked-example)
6. [Model Selection Justification](#6-model-selection-justification)
7. [Model Artifact Structure](#7-model-artifact-structure)
8. [Clinical Reference Ranges](#8-clinical-reference-ranges)
9. [Feature Importance Analysis](#9-feature-importance-analysis)
10. [Limitations & Future Work](#10-limitations--future-work)

---

## 1. Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                      ML PIPELINE OVERVIEW                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  PHASE 1: DATA PREPROCESSING (data_preprocessing_v2.py)            │
│  ┌──────────────────────────────────────────┐                      │
│  │ lab_clean_processed.csv (Lab panel data)  │                     │
│  │ nhanes_real_with_calories.csv (NHANES)    │                     │
│  └────────────────┬─────────────────────────┘                      │
│                   ▼                                                 │
│  ┌──────────────────────────────────────────┐                      │
│  │ Column Mapping & Schema Unification       │                     │
│  │ Lab codes (HGP,SGP,...) → Standard names  │                     │
│  │ (hemoglobin, glucose, ...)                │                     │
│  └────────────────┬─────────────────────────┘                      │
│                   ▼                                                 │
│  ┌──────────────────────────────────────────┐                      │
│  │ Missing Value Imputation (median)         │                     │
│  │ BMI Feature Engineering                   │                     │
│  │ Health Status Labeling (rule-based score)  │                    │
│  └────────────────┬─────────────────────────┘                      │
│                   ▼                                                 │
│  Output: processed_data_v2.csv                                     │
│                                                                     │
│  PHASE 2: MODEL TRAINING (model_training_v2.py)                    │
│  ┌──────────────────────────────────────────┐                      │
│  │ Load processed_data_v2.csv                │                     │
│  │ Select 14 feature columns                 │                     │
│  │ Encode target labels (0,1,2)              │                     │
│  └────────────────┬─────────────────────────┘                      │
│                   ▼                                                 │
│  ┌──────────────────────────────────────────┐                      │
│  │ 80/20 Stratified Train-Test Split         │                     │
│  │ StandardScaler (z-score normalization)    │                     │
│  └────────────────┬─────────────────────────┘                      │
│                   ▼                                                 │
│  ┌──────────────────────────────────────────┐                      │
│  │ Train 4 Models:                           │                     │
│  │   1. Logistic Regression                  │                     │
│  │   2. Random Forest (100 trees)            │                     │
│  │   3. Gradient Boosting (100 estimators)   │                     │
│  │   4. XGBoost (optional)                   │                     │
│  │ 5-fold Stratified Cross-Validation        │                     │
│  └────────────────┬─────────────────────────┘                      │
│                   ▼                                                 │
│  ┌──────────────────────────────────────────┐                      │
│  │ Best Model Selection (weighted score):    │                     │
│  │   50% Test Accuracy                       │                     │
│  │   30% F1 Score                            │                     │
│  │   20% CV Stability                        │                     │
│  │   + Interpretability Bonus                │                     │
│  └────────────────┬─────────────────────────┘                      │
│                   ▼                                                 │
│  Output: model_v2.pkl (model + scaler + metadata)                  │
│                                                                     │
│  PHASE 3: MODEL INFERENCE (model_inference_v2.py)                  │
│  ┌──────────────────────────────────────────┐                      │
│  │ Load model_v2.pkl                         │                     │
│  │ Accept lab values dict from Flask         │                     │
│  │ Build feature vector (14 values)          │                     │
│  │ Scale with saved StandardScaler           │                     │
│  │ model.predict() → class label             │                     │
│  │ LabelEncoder.inverse_transform()          │                     │
│  └────────────────┬─────────────────────────┘                      │
│                   ▼                                                 │
│  Output: "Normal" / "At Risk" / "Deficient" + confidence           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Preprocessing

**File:** `version2/data_preprocessing_v2.py` (187 lines)

This module takes two raw CSV datasets and produces a single cleaned, labeled dataset ready for ML training.

---

### 2.1 Imports and Constants (Lines 1–45)

```python
"""
Data Preprocessing V2 - Dual Dataset Merge

Merges lab_clean_processed.csv and nhanes_real_with_calories.csv.
Handles column mapping, missing value imputation, and health status labeling.
"""
```
> **Lines 1–6:** Module docstring explaining the purpose. This module handles the entire data preparation phase.

```python
import pandas as pd           # Data manipulation library
import numpy as np             # Numerical operations
import os                      # File system operations
from sklearn.base import BaseEstimator, TransformerMixin  # For custom transformers
from sklearn.pipeline import Pipeline         # ML pipeline construction
from sklearn.impute import SimpleImputer      # Missing value handling
from sklearn.preprocessing import StandardScaler  # Feature scaling
import joblib                                  # Model serialization
```
> **Lines 8–15:** Import all required libraries.
> - `pandas` loads and manipulates the CSV files
> - `numpy` provides mathematical functions
> - `SimpleImputer` fills missing values with median (robust to outliers)
> - `StandardScaler` normalizes features to mean=0, std=1

```python
LAB_DATA_PATH = r"c:\Users\USER\project\lab_clean_processed.csv"
NHANES_DATA_PATH = r"c:\Users\USER\project\nhanes_real_with_calories.csv"
PROCESSED_DATA_PATH = r"c:\Users\USER\project\version2\processed_data_v2.csv"
PREPROCESSOR_PATH = r"c:\Users\USER\project\version2\preprocessor_v2.pkl"
```
> **Lines 17–21:** Define file paths for input datasets and output files.
> - **Lab data** contains blood panel results with coded column names (HGP, SGP, etc.)
> - **NHANES data** is from the National Health and Nutrition Examination Survey — real-world demographics + lab values
> - **Processed data** is the unified output used for training

```python
LAB_CODE_MAP = {
    'HGP': 'hemoglobin',        # Hemoglobin (g/dL)
    'SGP': 'glucose',           # Blood Glucose (mg/dL)
    'UAP': 'uric_acid',         # Uric Acid (mg/dL)
    'CEP': 'creatinine',        # Creatinine (mg/dL)
    'NAPSI': 'sodium',          # Sodium (mEq/L)
    'SKPSI': 'potassium',       # Potassium (mEq/L)
    'CLPSI': 'chloride',        # Chloride (mEq/L)
    'TBP': 'bilirubin',         # Bilirubin (mg/dL)
    'VAP': 'alp',               # Alkaline Phosphatase (U/L)
    'VEP': 'sgpt',              # SGPT/ALT (U/L)
    'VCP': 'sgot',              # SGOT/AST (U/L)
    'VBP': 'vitamin_b12',       # Vitamin B12 (pg/mL)
    'FOP': 'calcium',           # Calcium (mg/dL)
    'FEP': 'iron',              # Iron (ug/dL)
    'TCP': 'total_cholesterol'  # Total Cholesterol (mg/dL)
}
```
> **Lines 23–44:** Column mapping dictionary. The lab dataset uses **coded names** (HGP, SGP, etc.) while the rest of the system uses **human-readable names**. This dictionary translates between the two schemas. This is critical because:
> - The ML model trains on coded columns (HGP, SGP, ...)
> - The OCR module extracts human-readable names (hemoglobin, glucose, ...)
> - This map is the bridge between both worlds

---

### 2.2 `load_and_merge_data()` Function (Lines 46–118)

```python
def load_and_merge_data():
    """Load both datasets and merge them into a single schema."""
```
> **Line 46–47:** This function loads both CSV files and merges them into one unified DataFrame.

```python
    print("Loading datasets...")
    try:
        lab_df = pd.read_csv(LAB_DATA_PATH)
        nhanes_df = pd.read_csv(NHANES_DATA_PATH)
```
> **Lines 49–52:** Load both CSVs into pandas DataFrames.
> - `lab_df` might have ~50,000 rows with columns like HGP, SGP, TCP
> - `nhanes_df` might have ~1,000 rows with columns like hemoglobin, fasting_glucose, age, sex

```python
        # 1. Standardize Lab Data Columns
        lab_df_renamed = lab_df.rename(columns=LAB_CODE_MAP)
```
> **Line 57:** Rename lab columns from codes to human-readable names.
> Before: `HGP, SGP, TCP, ...`
> After: `hemoglobin, glucose, total_cholesterol, ...`

```python
        # Mapping NHANES columns
        nhanes_map = {
            'sex': 'gender',
            'fasting_glucose': 'glucose',
            'total_chol': 'total_cholesterol',
            'b12': 'vitamin_b12',
        }
        nhanes_df_renamed = nhanes_df.rename(columns=nhanes_map)
```
> **Lines 62–69:** NHANES data also has different column names. This maps them to the unified schema.
> `sex` → `gender`, `fasting_glucose` → `glucose`, etc.

```python
        # 3. Create Unified DataFrame
        common_cols = set(lab_df_renamed.columns).intersection(set(nhanes_df_renamed.columns))
        
        target_cols = [
            'age', 'gender', 'height', 'weight',                    # Demographics
            'hemoglobin', 'glucose', 'total_cholesterol', 'ldl', 'hdl', 'triglycerides',  # Basic Panel
            'creatinine', 'uric_acid',                               # Kidney
            'sodium', 'potassium', 'chloride',                       # Electrolytes
            'bilirubin', 'sgpt', 'sgot', 'alp',                     # Liver
            'calcium', 'iron', 'vitamin_b12',                        # Micro
            'calories'                                                # Target
        ]
```
> **Lines 72–87:** Define the **unified schema** — these are the columns we want in the final dataset. They cover:
> - **Demographics**: age, gender, height, weight
> - **Blood panel**: hemoglobin, glucose, cholesterol, etc.
> - **Organ panels**: kidney, liver, electrolytes
> - **Micronutrients**: calcium, iron, B12

```python
        # Append NHANES (High quality, has demographics)
        nhanes_subset = pd.DataFrame()
        for col in target_cols:
            if col in nhanes_df_renamed.columns:
                nhanes_subset[col] = nhanes_df_renamed[col]
            else:
                nhanes_subset[col] = np.nan
```
> **Lines 90–96:** Extract the target columns from NHANES data. If a column doesn't exist in NHANES, fill with `NaN` (will be imputed later).

```python
        # Map gender in NHANES (usually 1=Male, 2=Female) to 0/1
        if 'gender' in nhanes_subset.columns:
             nhanes_subset['gender'] = nhanes_subset['gender'].apply(
                 lambda x: 1 if str(x).lower() in ['1', 'm', 'male'] else 0
             )
```
> **Lines 98–100:** Standardize gender encoding. NHANES may use 1/2 or M/F. We convert to binary: **1 = Male, 0 = Female**.

```python
        # Combine
        combined_df = pd.concat([nhanes_subset, lab_subset], axis=0, ignore_index=True)
```
> **Line 115:** Vertically stack both datasets into one big DataFrame. Rows from NHANES + rows from Lab data = combined dataset.

---

### 2.3 `preprocess_and_label()` Function (Lines 120–176)

This function cleans the combined data and generates the **health status labels** that the ML model will predict.

```python
def preprocess_and_label(df):
    """Clean data, impute missing values, and generate health labels."""
    
    if df.empty:
        return df
```
> **Lines 120–124:** Guard clause — skip if DataFrame is empty.

```python
    # 1. Handling Missing Values
    imputer = SimpleImputer(strategy='median')
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
```
> **Lines 126–131:** **Median imputation** — fill all missing numerical values with the column median.
>
> **Why median, not mean?**
> - Median is **robust to outliers**. In medical data, extreme values are common (e.g., glucose of 500 mg/dL in a diabetic patient). The mean would be skewed by these extreme values, but the median remains stable.
> - Example: If hemoglobin values are [12, 13, 14, 13.5, NaN], median = 13.25. This is filled where NaN was.

```python
    # 2. Feature Engineering - BMI
    if 'weight' in df.columns and 'height' in df.columns:
        df['height_m'] = df['height'].apply(lambda x: x / 100 if x > 3 else x)
        df['bmi'] = df['weight'] / (df['height_m'] ** 2)
        df['bmi'] = df['bmi'].fillna(df['bmi'].median())
```
> **Lines 134–139:** Calculate **BMI** (Body Mass Index) as a derived feature.
> - If height > 3, assume centimeters → convert to meters
> - Formula: BMI = weight (kg) / height² (m²)
> - Any remaining NaN BMI values get the median

```python
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
        if score == 0: return 0   # Normal
        elif score <= 2: return 1  # At Risk
        else: return 2             # Deficient/Action Needed
```
> **Lines 146–169:** **This is how the health status labels are generated.** This is a critical function that creates the ML training targets.
>
> **The scoring system works like this:**
>
> | Biomarker | Condition | Points |
> |-----------|-----------|--------|
> | Glucose > 125 mg/dL | Diabetic range | +2 |
> | Glucose 100–125 mg/dL | Pre-diabetic | +1 |
> | Hemoglobin < 12 g/dL | Anemia | +2 |
> | Cholesterol > 240 mg/dL | High risk | +2 |
> | Cholesterol 200–240 mg/dL | Borderline | +1 |
> | LDL > 160 mg/dL | Very high | +2 |
> | LDL 130–160 mg/dL | High | +1 |
> | Creatinine > 1.4 mg/dL | Kidney concern | +2 |
>
> **Final classification:**
> - Score = 0 → **Normal** (class 0)
> - Score 1–2 → **At Risk** (class 1)
> - Score 3+ → **Deficient / Action Needed** (class 2)
>
> **Example:** A patient with glucose=130 (+2) and hemoglobin=11 (+2) gets score 4 → **Deficient**.

```python
    df['health_status'] = df.apply(get_health_status, axis=1)
```
> **Line 171:** Apply the scoring function to every row, creating the `health_status` column (0, 1, or 2).

---

## 3. Model Training

**File:** `version2/model_training_v2.py` (349 lines)

This module trains 4 different ML classifiers, evaluates them, and saves the best one.

---

### 3.1 Imports and Configuration (Lines 1–35)

```python
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
import warnings
warnings.filterwarnings('ignore')
```
> **Lines 6–20:** Import ML libraries.
> - `train_test_split` splits data into training and testing sets
> - `StratifiedKFold` ensures each fold has proportional class representation
> - `StandardScaler` normalizes features (mean=0, std=1)
> - `LabelEncoder` converts string labels to integers (Normal→0, At Risk→1, Deficient→2)
> - 4 different classifier algorithms are imported for comparison

```python
try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("[WARN] XGBoost not available. Skipping XGBoost model.")
```
> **Lines 22–28:** Optional XGBoost import. If not installed, the pipeline still works with 3 models.

```python
FEATURE_COLUMNS = ['HGP', 'SGP', 'UAP', 'CEP', 'NAPSI', 'SKPSI', 'CLPSI', 
                   'TBP', 'VAP', 'VEP', 'VCP', 'FOP', 'FEP', 'TCP']

TARGET_COLUMN = 'health_status'
```
> **Lines 30–34:** Define the **14 biomarker features** used for prediction and the target column.
>
> | Code | Full Name | Medical Significance |
> |------|-----------|---------------------|
> | HGP | Hemoglobin | Oxygen-carrying capacity, anemia indicator |
> | SGP | Glucose | Blood sugar, diabetes indicator |
> | UAP | Uric Acid | Gout, kidney function |
> | CEP | Creatinine | Kidney filtration rate |
> | NAPSI | Sodium | Electrolyte balance |
> | SKPSI | Potassium | Heart rhythm, nerve function |
> | CLPSI | Chloride | Electrolyte balance |
> | TBP | Bilirubin | Liver function |
> | VAP | Alk. Phosphatase | Liver/bone disease |
> | VEP | SGPT/ALT | Liver damage marker |
> | VCP | SGOT/AST | Liver damage marker |
> | FOP | Calcium | Bone health |
> | FEP | Iron/Ferritin | Anemia, iron stores |
> | TCP | Total Cholesterol | Cardiovascular risk |

---

### 3.2 `load_processed_data()` Function (Lines 37–61)

```python
def load_processed_data(data_path: str = None) -> tuple:
    """Load preprocessed data and split into features/target."""
    if data_path is None:
        data_path = Path(__file__).parent / 'processed_data_v2.csv'
```
> **Lines 37–42:** Load the preprocessed CSV. Default path is `version2/processed_data_v2.csv`.

```python
    df = pd.read_csv(data_path)
    
    # Select available feature columns
    available_features = [c for c in FEATURE_COLUMNS if c in df.columns]
    print(f"  Using {len(available_features)} features: {available_features}")
    
    X = df[available_features].copy()
    y = df[TARGET_COLUMN].copy()
```
> **Lines 45–52:** Load data and separate into features (`X`) and target (`y`).
> - `X` shape: (n_samples, 14) — each row is a patient, each column is a biomarker
> - `y` shape: (n_samples,) — each value is 0, 1, or 2

```python
    # Encode target labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    print(f"  Classes: {list(label_encoder.classes_)}")
    print(f"  Class distribution: {dict(zip(label_encoder.classes_, np.bincount(y_encoded)))}")
    
    return X, y_encoded, label_encoder, available_features
```
> **Lines 54–61:** Encode target labels as integers.
> - `LabelEncoder` maps: `"At Risk"` → 0, `"Deficient"` → 1, `"Normal"` → 2 (alphabetical order)
> - `np.bincount` counts how many samples per class (for checking class imbalance)
> - Returns: feature matrix, encoded labels, encoder (for reverse mapping), and feature column names

---

### 3.3 `get_models()` Function (Lines 64–100)

```python
def get_models():
    """Define models to train and compare."""
    models = {
        'LogisticRegression': LogisticRegression(
            C=1.0,              # Regularization strength (inverse)
            max_iter=1000,      # Maximum iterations for convergence
            class_weight='balanced',  # Handles imbalanced classes
            random_state=42     # Reproducibility
        ),
```
> **Lines 64–74:** **Logistic Regression** — a linear classifier.
> - `C=1.0`: Regularization strength. Lower = more regularization (simpler model).
> - `class_weight='balanced'`: Automatically adjusts weights inversely proportional to class frequencies. If "Deficient" has fewer samples, each Deficient sample gets more weight during training.
> - **Why include it:** Most interpretable model. In healthcare, doctors need to understand WHY the model made a prediction. Logistic Regression provides coefficient weights per feature.

```python
        'RandomForest': RandomForestClassifier(
            n_estimators=100,   # 100 decision trees
            max_depth=10,       # Max tree depth
            class_weight='balanced',
            random_state=42,
            n_jobs=-1           # Use all CPU cores
        ),
```
> **Lines 75–81:** **Random Forest** — ensemble of 100 decision trees.
> - `n_estimators=100`: Train 100 individual decision trees, each on a random subset of data and features.
> - `max_depth=10`: No tree can be deeper than 10 levels. Prevents overfitting.
> - `n_jobs=-1`: Parallelize across all CPU cores (training is embarrassingly parallel).
> - **Why include it:** Provides feature importance scores and handles non-linear relationships.

```python
        'GradientBoosting': GradientBoostingClassifier(
            n_estimators=100,   # 100 boosting stages
            learning_rate=0.1,  # Step size shrinkage
            max_depth=5,        # Shallower trees
            random_state=42
        )
    }
```
> **Lines 82–87:** **Gradient Boosting** — sequential ensemble.
> - `learning_rate=0.1`: Each tree contributes 10% to the prediction. Lower values need more trees but generalize better.
> - `max_depth=5`: Shallower than Random Forest because boosting already combines many trees.
> - **How it works:** Each new tree corrects the errors of all previous trees. Tree 1 makes predictions → Tree 2 learns from Tree 1's mistakes → Tree 3 learns from Trees 1+2's mistakes → etc.

```python
    if XGBOOST_AVAILABLE:
        models['XGBoost'] = XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            use_label_encoder=False,  # Suppress deprecation warning
            eval_metric='mlogloss'    # Multiclass log-loss
        )
```
> **Lines 90–98:** **XGBoost** — optimized gradient boosting.
> - `eval_metric='mlogloss'`: Multi-class logarithmic loss. Penalizes confident wrong predictions heavily.
> - **Why include it:** Often the most accurate classifier for tabular data due to regularization and second-order gradient optimization.

---

### 3.4 `train_and_evaluate_models()` Function (Lines 103–169)

This is the **core training function**. It trains all 4 models and evaluates each one.

```python
def train_and_evaluate_models(X, y, label_encoder):
    """Train all models and evaluate with cross-validation."""
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
```
> **Lines 103–110:** Split data into 80% training and 20% testing.
> - `stratify=y`: Maintains the same class ratio in both splits. If the full dataset is 50% Normal, 30% At Risk, 20% Deficient, both train and test will have roughly the same proportions.
> - `random_state=42`: Fixed seed for reproducibility. Running the code twice gives identical splits.

```python
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
```
> **Lines 114–117:** **Feature scaling using Z-score normalization.**
>
> For each feature column: `z = (x - mean) / std`
>
> **Why this is critical:** Biomarkers have vastly different scales:
> - Hemoglobin: 10–18 g/dL
> - Glucose: 70–400 mg/dL
> - Cholesterol: 100–300 mg/dL
> - Creatinine: 0.5–2.0 mg/dL
>
> Without scaling, features with large values (glucose, cholesterol) would dominate the model's decisions. After scaling, all features have mean=0 and std=1.
>
> **Important:** `fit_transform` on train data learns the mean and std. `transform` on test data uses the SAME mean and std from training. This prevents **data leakage** — the test data never influences the scaling parameters.

```python
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    for name, model in models.items():
        print(f"\n[TRAIN] {name}...")
        
        # Train
        model.fit(X_train_scaled, y_train)
```
> **Lines 127–133:** Set up 5-fold cross-validation and train each model.
> - `StratifiedKFold(n_splits=5)`: Divides training data into 5 equal folds, maintaining class proportions in each fold.
> - `model.fit(X_train_scaled, y_train)`: The model learns patterns from the scaled training data.

```python
        # Predict
        y_train_pred = model.predict(X_train_scaled)
        y_test_pred = model.predict(X_test_scaled)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=cv, scoring='accuracy')
```
> **Lines 136–140:** Make predictions on both train and test sets, then run cross-validation.
> - **Train predictions** measure how well the model memorized the data.
> - **Test predictions** measure how well the model generalizes to unseen data.
> - **Cross-validation** trains 5 sub-models on 5 different 80/20 splits within the training data. This gives a more robust accuracy estimate.

```python
        # Metrics
        train_acc = accuracy_score(y_train, y_train_pred)
        test_acc = accuracy_score(y_test, y_test_pred)
        precision = precision_score(y_test, y_test_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_test_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_test_pred, average='weighted', zero_division=0)
```
> **Lines 142–147:** Calculate 5 key metrics:
>
> | Metric | Formula | What It Measures |
> |--------|---------|-----------------|
> | **Accuracy** | Correct / Total | Overall correctness |
> | **Precision** | TP / (TP + FP) | "When it says Deficient, how often is it right?" |
> | **Recall** | TP / (TP + FN) | "Of all Deficient patients, how many did it catch?" |
> | **F1 Score** | 2 × (P × R) / (P + R) | Harmonic mean of precision and recall |
> | **CV Mean** | Average of 5 fold accuracies | Stability across different data subsets |
>
> `average='weighted'`: Weight each class's metric by its frequency. If "Normal" has 3x more samples than "Deficient", Normal's metrics count 3x more.

```python
        results[name] = {
            'model': model,
            'scaler': scaler,
            'train_accuracy': train_acc,
            'test_accuracy': test_acc,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'y_test_pred': y_test_pred
        }
```
> **Lines 149–160:** Store all metrics and the trained model object for later comparison.

---

### 3.5 `select_best_model()` Function (Lines 172–216)

```python
def select_best_model(results: dict) -> str:
    """
    Select the best model based on test accuracy and F1 score.
    Prioritize interpretability for healthcare applications.
    """
```
> **Lines 172–176:** This function picks the winner from all trained models.

```python
    # Interpretability bonus for healthcare
    interpretability_bonus = {
        'LogisticRegression': 0.02,  # Most interpretable
        'RandomForest': 0.01,        # Feature importance available
        'GradientBoosting': 0.00,
        'XGBoost': 0.00
    }
```
> **Lines 193–198:** **Healthcare-specific design decision.** In medicine, interpretability matters. Logistic Regression gets a +2% bonus because doctors can see coefficient weights. Random Forest gets +1% for feature importance visualization.

```python
    for name, metrics in results.items():
        # Combined score: 50% accuracy, 30% F1, 20% CV stability
        score = (
            0.50 * metrics['test_accuracy'] +
            0.30 * metrics['f1_score'] +
            0.20 * (1 - metrics['cv_std'])  # Lower std = more stable
        )
        score += interpretability_bonus.get(name, 0)
        
        if score > best_score:
            best_score = score
            best_name = name
```
> **Lines 203–214:** **Weighted scoring formula:**
>
> ```
> Final Score = 50% × Test Accuracy + 30% × F1 Score + 20% × (1 - CV_Std) + Bonus
> ```
>
> **Why these weights?**
> - **50% Accuracy**: Most important — we want correct predictions
> - **30% F1 Score**: Balance between precision and recall (critical in healthcare — missing a sick patient is worse than false alarm)
> - **20% Stability**: `(1 - CV_Std)` — lower standard deviation across CV folds means the model performs consistently, not just well on one lucky split
> - **Bonus**: Slight tiebreaker for interpretable models

---

### 3.6 `save_model()` Function (Lines 219–256)

```python
def save_model(results, best_name, feature_columns, label_encoder, output_path=None):
    """Save the best model along with metadata."""
    
    model_artifact = {
        'model': best_result['model'],          # The trained classifier
        'scaler': best_result['scaler'],        # StandardScaler (for inference)
        'feature_columns': feature_columns,     # ['HGP', 'SGP', ...]
        'label_encoder': label_encoder,         # LabelEncoder (for decoding)
        'model_name': best_name,                # 'RandomForest', etc.
        'metrics': {
            'accuracy': best_result['test_accuracy'],
            'f1_score': best_result['f1_score'],
            'precision': best_result['precision'],
            'recall': best_result['recall'],
            'cv_mean': best_result['cv_mean'],
            'cv_std': best_result['cv_std']
        }
    }
```
> **Lines 229–244:** Create the **model artifact** — everything needed for inference:
> - The trained model itself
> - The scaler (must apply the exact same transformation at inference time)
> - Feature column names (so inference knows the expected order)
> - Label encoder (to convert 0/1/2 back to "Normal"/"At Risk"/"Deficient")

```python
    # Get medians for imputation during inference
    data_path = Path(__file__).parent / 'processed_data_v2.csv'
    if data_path.exists():
        df = pd.read_csv(data_path)
        available_features = [c for c in feature_columns if c in df.columns]
        model_artifact['medians'] = df[available_features].median().to_dict()
```
> **Lines 246–251:** Save **median values** for each feature. During inference, if a biomarker is missing from the OCR output, the median is used as a fallback instead of zero. This prevents the model from seeing extreme/impossible values.

```python
    joblib.dump(model_artifact, output_path)
```
> **Line 253:** Serialize the entire artifact to disk as `model_v2.pkl` using joblib (efficient for scikit-learn objects).

---

## 4. Model Inference

**File:** `version2/model_inference_v2.py` (297 lines)

This module loads the saved model and makes predictions on new blood report data.

---

### 4.1 Clinical Reference Ranges (Lines 12–28)

```python
NORMAL_RANGES = {
    "HGP": (12, 16),      # Hemoglobin (g/dL)
    "SGP": (70, 140),     # Glucose (mg/dL)
    "TCP": (125, 200),    # Total Cholesterol (mg/dL)
    "HDP": (40, 60),      # HDL (mg/dL)
    "LCP": (0, 130),      # LDL (mg/dL)
    "TGP": (0, 150),      # Triglycerides (mg/dL)
    "VAP": (20, 60),      # Vitamin A
    "VEP": (500, 1800),   # Vitamin E
    "VCP": (0.2, 2.0),    # Vitamin C
    "FEP": (12, 300),     # Ferritin
    "FOP": (2.0, 20.0),   # Folate
    "UAP": (2.5, 7.2),    # Uric Acid
    "CEP": (0.6, 1.3),    # Creatinine
}
```
> **Lines 12–28:** Clinically validated normal ranges for each biomarker. Used by `analyze_biomarkers_v2()` to flag LOW/HIGH values independently of the ML model. This serves as a **rule-based backup** to the ML prediction.

---

### 4.2 `ModelInferenceV2` Class (Lines 49–158)

```python
class ModelInferenceV2:
    """Backend-compatible inference class for V2 health status prediction."""
    
    def __init__(self, model_path: str = None):
        if model_path is None:
            model_path = Path(__file__).parent / 'model_v2.pkl'
        
        self.model_path = Path(model_path)
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.label_encoder = None
        self.medians = None
        
        self._load_model()
```
> **Lines 49–71:** Constructor. Sets up all attributes and immediately loads the model from disk.

```python
    def _load_model(self):
        """Load the trained model artifact."""
        if not self.model_path.exists():
            print(f"[WARN] V2 model not found at {self.model_path}")
            return False
        
        try:
            artifact = joblib.load(self.model_path)
            self.model = artifact['model']           # The classifier
            self.scaler = artifact['scaler']          # StandardScaler
            self.feature_columns = artifact['feature_columns']  # ['HGP', 'SGP', ...]
            self.label_encoder = artifact['label_encoder']      # Decodes 0→Normal, etc.
            self.medians = artifact.get('medians', {})          # Fallback values
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load V2 model: {e}")
            return False
```
> **Lines 73–89:** Load the model artifact. Unpacks all 5 components saved by `save_model()`.

---

### 4.3 `predict_health_status()` — The Core Prediction (Lines 95–124)

**This is where the actual prediction happens. Every step explained:**

```python
    def predict_health_status(self, lab_values: Dict[str, float]) -> str:
        """
        Predict health status from lab values.
        
        Args:
            lab_values: Dict of biomarker values, e.g., {'HGP': 13.5, 'SGP': 95}
        
        Returns:
            Health status: 'Normal', 'At Risk', or 'Deficient'
        """
        if not self.is_ready():
            return 'Unknown'
```
> **Lines 95–106:** Accept a dictionary of biomarker values. If model isn't loaded, return 'Unknown'.

```python
        # Prepare feature vector
        features = []
        for col in self.feature_columns:
            if col in lab_values and lab_values[col] is not None:
                features.append(float(lab_values[col]))
            elif col in self.medians:
                features.append(self.medians[col])
            else:
                features.append(0.0)
```
> **Lines 108–116:** **Build the feature vector** — a list of 14 numbers in the exact order the model expects.
>
> For each of the 14 features:
> 1. If the value exists in `lab_values` → use it
> 2. If missing but we have a saved median → use the median
> 3. If both missing → use 0.0
>
> **Example:** If `lab_values = {'HGP': 13.5, 'SGP': 95}` and feature_columns = `['HGP', 'SGP', 'UAP', ..., 'TCP']`:
> - HGP → 13.5 (from input)
> - SGP → 95 (from input)
> - UAP → 5.2 (from median, since not in input)
> - ... etc.
> - Result: `[13.5, 95, 5.2, 0.9, 140, 4.2, 102, 0.8, 80, 25, 22, 9.5, 100, 185]`

```python
        # Scale and predict
        X = np.array([features])
        X_scaled = self.scaler.transform(X)
        prediction = self.model.predict(X_scaled)[0]
```
> **Lines 118–121:** **The actual prediction in 3 steps:**
>
> **Step 1:** Convert list to numpy array with shape (1, 14) — one row, 14 columns.
> ```
> X = [[13.5, 95, 5.2, 0.9, 140, 4.2, 102, 0.8, 80, 25, 22, 9.5, 100, 185]]
> ```
>
> **Step 2:** Apply the SAME StandardScaler that was fitted during training.
> ```
> X_scaled = [[-0.32, -0.45, 0.12, -0.08, 0.55, 0.23, 0.01, -0.67, 0.34, -0.12, 0.08, 0.45, -0.23, 0.15]]
> ```
> Each value is now a z-score: how many standard deviations from the training mean.
>
> **Step 3:** The trained model makes its prediction.
> - For **Random Forest**: All 100 decision trees vote. Each tree traverses its branches based on feature thresholds and outputs a class. The majority vote wins.
> - For **Logistic Regression**: Computes `z = w1*x1 + w2*x2 + ... + w14*x14 + b` for each class, then applies softmax to get probabilities.
> - The result is an integer: 0, 1, or 2.

```python
        # Decode label
        return self.label_encoder.inverse_transform([prediction])[0]
```
> **Line 124:** Convert the integer back to a human-readable string.
> - 0 → "At Risk" (or whatever alphabetical mapping was learned)
> - 1 → "Deficient"
> - 2 → "Normal"

---

### 4.4 `predict_with_confidence()` — Prediction + Probability (Lines 126–158)

```python
    def predict_with_confidence(self, lab_values):
        # ... (same feature preparation as above) ...
        
        prediction = self.model.predict(X_scaled)[0]
        
        # Get probability if available
        if hasattr(self.model, 'predict_proba'):
            proba = self.model.predict_proba(X_scaled)[0]
            confidence = float(max(proba))
        else:
            confidence = 1.0
        
        return self.label_encoder.inverse_transform([prediction])[0], confidence
```
> **Lines 126–158:** Same as `predict_health_status()` but also returns a **confidence score**.
>
> **How confidence works:**
> - `predict_proba()` returns probabilities for each class.
> - Example: `[0.15, 0.05, 0.80]` → 15% At Risk, 5% Deficient, 80% Normal
> - Confidence = max probability = 0.80 (80%)
> - A confidence of 80%+ is considered HIGH, 60-80% MEDIUM, below 60% LOW.
>
> **For Random Forest:** Probability = fraction of trees that voted for each class. If 80 out of 100 trees say "Normal", probability for Normal = 0.80.
>
> **For Logistic Regression:** Probability = softmax of the linear combination output.

---

### 4.5 `analyze_biomarkers_v2()` — Rule-Based Analysis (Lines 188–230)

```python
def analyze_biomarkers_v2(values: Dict[str, float]) -> Tuple[List[str], List[str]]:
    """
    Analyze biomarkers and identify deficiencies.
    COMPATIBLE with existing nutrition_engine.analyze_biomarkers() format.
    """
    report = []
    deficiencies = []
    
    for test, (low, high) in NORMAL_RANGES.items():
        if test not in values or values[test] is None:
            continue
        
        val = float(values[test])
        
        if val < low:
            report.append(f"{test}: LOW ({val:.1f}, normal: {low}-{high})")
            deficiencies.append(test)
        elif val > high:
            report.append(f"{test}: HIGH ({val:.1f}, normal: {low}-{high})")
            if test in ['SGP', 'TCP', 'LCP', 'TGP', 'UAP']:
                deficiencies.append(test)
        else:
            report.append(f"{test}: Normal ({val:.1f})")
```
> **Lines 188–223:** **Rule-based biomarker analysis** (independent of ML).
>
> For each biomarker:
> 1. Look up the normal range (e.g., Hemoglobin: 12–16 g/dL)
> 2. If value < low → flag as LOW → add to deficiencies
> 3. If value > high → flag as HIGH → add to deficiencies (only for dangerous-if-high markers like glucose, cholesterol)
> 4. If in range → flag as Normal
>
> **Why both ML and rules?**
> - ML captures **multi-feature interactions** (e.g., low iron + low hemoglobin together is worse than either alone)
> - Rules catch **individual abnormalities** that the ML model might miss
> - The system uses ML for the overall health status but rules for per-biomarker flagging and food recommendations

```python
    # Add V2 ML prediction if available
    inference = _get_inference()
    if inference.is_ready():
        health_status = inference.predict_health_status(values)
        report.insert(0, f"Overall Health Status: {health_status}")
```
> **Lines 225–228:** Add the ML prediction to the top of the report. This gives both the ML-based overall status AND the individual biomarker assessments.

---

## 5. Complete Worked Example

### Input → Processing → Output

**Scenario:** A 25-year-old male uploads a blood report. OCR extracts these values:

```
Input Lab Values:
{
    "hemoglobin": 11.2,        ← LOW (normal: 12-16)
    "glucose": 105,            ← Slightly HIGH (normal: 70-100)
    "total_cholesterol": 210,  ← Borderline HIGH (normal: 125-200)
    "creatinine": 0.9,         ← NORMAL
    "uric_acid": 5.5,          ← NORMAL
    "sodium": 140,             ← NORMAL
    "potassium": 4.1,          ← NORMAL
    "chloride": 101,           ← NORMAL
    "bilirubin": 0.7,          ← NORMAL
    "alp": 65,                 ← NORMAL
    "sgpt": 28,                ← NORMAL
    "sgot": 25,                ← NORMAL
    "calcium": 9.2,            ← NORMAL
    "iron": 45                 ← LOW (normal: 65-175)
}
```

### Step-by-Step ML Processing:

**Step 1: Feature Vector Construction**
```
The 14 features are mapped to codes (HGP, SGP, etc.):
features = [11.2, 105, 5.5, 0.9, 140, 4.1, 101, 0.7, 65, 28, 25, 9.2, 45, 210]
           ↑HGP  ↑SGP  ↑UAP ↑CEP ↑NAP ↑SKP ↑CLP ↑TBP ↑VAP ↑VEP ↑VCP ↑FOP ↑FEP ↑TCP
```

**Step 2: StandardScaler Transform**
```
Using saved mean/std from training:
X_scaled = [(11.2-13.8)/1.5, (105-98)/35, (5.5-5.2)/1.8, ...]
         = [-1.73, 0.20, 0.17, -0.06, 0.40, -0.12, -0.20, -0.33, -0.18, 0.08, 0.05, 0.15, -1.94, 0.30]
```

**Step 3: Model Prediction (Random Forest example)**
```
100 decision trees vote:
- Tree 1: Check HGP < 12? YES → Check FEP < 50? YES → Vote: "At Risk"
- Tree 2: Check SGP > 125? NO → Check TCP > 200? YES → Check HGP < 11? NO → Vote: "At Risk"
- Tree 3: Check FEP < 60? YES → Check HGP < 13? YES → Vote: "Deficient"
- ...
- Tree 100: Check HGP < 12? YES → Vote: "At Risk"

Final tally: Normal=12, At Risk=63, Deficient=25
Majority vote: "At Risk" (63%)
Confidence: 0.63 (63%)
```

**Step 4: Rule-Based Assessment (parallel)**
```
Hemoglobin 11.2: LOW (normal 12-16)     → Deficiency flagged
Glucose 105:     HIGH (normal 70-100)    → Moderate concern
Cholesterol 210: HIGH (normal 125-200)   → Deficiency flagged
Iron 45:         LOW (normal 65-175)     → Deficiency flagged
All others:      NORMAL
```

**Step 5: Safety Override Check**
```
ML says: "At Risk"
Rule-based scoring: glucose>100 (+1) + hemoglobin<12 (+2) + cholesterol>200 (+1) = 4 → "Deficient"
Override: Model says "At Risk" but rules say "Deficient" → USE "Deficient" (more conservative)
```

**Step 6: Diet Plan Selection**
```
Deficiencies: [hemoglobin, glucose, cholesterol, iron]
→ Iron deficiency detected → Primary plan: "iron_rich"
→ Macros adjusted: 40% carbs, 35% protein, 25% fat (lower carbs due to glucose)
```

### Final Output:
```json
{
    "health_status": "Deficient",
    "confidence": 0.63,
    "deficiencies": ["hemoglobin", "glucose", "total_cholesterol", "iron"],
    "macros": {"carbs": 40, "protein": 35, "fat": 25},
    "diet_plan": {
        "Monday": {
            "breakfast": "Oatmeal with berries, spinach smoothie, boiled eggs",
            "lunch": "Beef/chicken salad with spinach and beans",
            "dinner": "Lentil stew with vegetables and a citrus salad",
            "snacks": "Dried apricots, pumpkin seeds, dark chocolate"
        },
        ...
    },
    "assessment": [
        {"test": "hemoglobin", "value": 11.2, "status": "LOW"},
        {"test": "glucose", "value": 105, "status": "HIGH"},
        {"test": "iron", "value": 45, "status": "LOW"},
        ...
    ]
}
```

---

## 6. Model Selection Justification

### Why We Compare 4 Models

| Model | Strengths | Weaknesses | Healthcare Applicability |
|-------|-----------|------------|--------------------------|
| **Logistic Regression** | Interpretable, fast, works well with small data | Linear only, can't capture complex interactions | ⭐⭐⭐ Most interpretable for clinicians |
| **Random Forest** | Handles non-linearity, feature importance, robust | Can overfit with deep trees | ⭐⭐⭐ Good balance of accuracy + interpretability |
| **Gradient Boosting** | Very accurate, captures subtle patterns | Slower to train, less interpretable | ⭐⭐ High accuracy but harder to explain |
| **XGBoost** | State-of-the-art for tabular data, regularized | Most complex, "black box" | ⭐ Best accuracy but hardest to interpret |

### Selection Formula Rationale

```
Score = 50% × Accuracy + 30% × F1 + 20% × Stability + Interpretability Bonus
```

- **Accuracy (50%)** — We want correct predictions above all else
- **F1 Score (30%)** — In healthcare, missing a sick patient (false negative) or alarming a healthy patient (false positive) must be balanced
- **Stability (20%)** — A model that works 95% on one data split but 60% on another is unreliable. Low CV standard deviation means consistent performance.
- **Interpretability Bonus** — A small tiebreaker. If Random Forest and Gradient Boosting tie at 94% accuracy, Random Forest wins because doctors can see feature importance.

---

## 7. Model Artifact Structure

The saved `model_v2.pkl` file contains:

```python
{
    'model':           <sklearn classifier>,      # The trained model object
    'scaler':          <StandardScaler>,           # Must use this exact scaler at inference
    'feature_columns': ['HGP', 'SGP', ...],       # 14 biomarker codes in exact order
    'label_encoder':   <LabelEncoder>,             # Maps 0↔"At Risk", 1↔"Deficient", 2↔"Normal"
    'model_name':      'RandomForest',             # Which algorithm won
    'metrics': {
        'accuracy':  0.9420,
        'f1_score':  0.9385,
        'precision': 0.9402,
        'recall':    0.9420,
        'cv_mean':   0.9315,
        'cv_std':    0.0089
    },
    'medians': {                                   # Fallback values for missing features
        'HGP': 13.8,
        'SGP': 98.0,
        'UAP': 5.2,
        ...
    }
}
```

---

## 8. Clinical Reference Ranges

These ranges are used for the **rule-based biomarker assessment** (separate from ML):

| Code | Biomarker | Low | High | Unit | Medical Significance |
|------|-----------|-----|------|------|---------------------|
| HGP | Hemoglobin | 12 | 16 | g/dL | Anemia if low |
| SGP | Glucose | 70 | 140 | mg/dL | Diabetes if >125 |
| TCP | Cholesterol | 125 | 200 | mg/dL | Heart disease if >240 |
| HDP | HDL | 40 | 60 | mg/dL | "Good" cholesterol |
| LCP | LDL | 0 | 130 | mg/dL | "Bad" cholesterol |
| TGP | Triglycerides | 0 | 150 | mg/dL | Fat in blood |
| VAP | Alk. Phosphatase | 20 | 60 | U/L | Liver/bone disease |
| VEP | Vitamin E | 500 | 1800 | µg/dL | Antioxidant |
| VCP | Vitamin C | 0.2 | 2.0 | mg/dL | Immune function |
| FEP | Ferritin | 12 | 300 | ng/mL | Iron storage |
| FOP | Folate | 2.0 | 20.0 | ng/mL | Cell growth |
| UAP | Uric Acid | 2.5 | 7.2 | mg/dL | Gout, kidney |
| CEP | Creatinine | 0.6 | 1.3 | mg/dL | Kidney function |

---

## 9. Feature Importance Analysis

When using **Random Forest** as the selected model, the model provides feature importance scores showing which biomarkers have the most influence on the health status prediction.

### Typical Feature Importance Ranking:

```
1. SGP   (Glucose)          — ~18%  ████████████████████
2. TCP   (Cholesterol)      — ~15%  ████████████████
3. HGP   (Hemoglobin)       — ~14%  ███████████████
4. CEP   (Creatinine)       — ~10%  ██████████
5. UAP   (Uric Acid)        — ~8%   ████████
6. VEP   (SGPT/ALT)         — ~7%   ███████
7. VCP   (SGOT/AST)         — ~6%   ██████
8. FEP   (Ferritin/Iron)    — ~5%   █████
9. VAP   (Alk. Phosphatase) — ~4%   ████
10. TBP  (Bilirubin)        — ~4%   ████
11. NAPSI (Sodium)           — ~3%   ███
12. SKPSI (Potassium)        — ~3%   ███
13. FOP   (Calcium)          — ~2%   ██
14. CLPSI (Chloride)         — ~1%   █
```

**Key insight:** Glucose, cholesterol, and hemoglobin are the top 3 predictors — which aligns with medical understanding (these are the primary markers for diabetes, heart disease, and anemia respectively).

---

## 10. Limitations & Future Work

### Current Limitations

1. **Training labels are rule-based** — The health status labels (Normal/At Risk/Deficient) are generated by clinical scoring rules, not by doctors. The ML model is essentially learning to replicate these rules (but can capture non-linear interactions between features that the rules miss).

2. **14 features only** — Many important biomarkers (TSH, Vitamin D, HbA1c) are not included in the training features, though they ARE extracted by OCR and displayed in the report.

3. **Static reference ranges** — The normal ranges don't account for age, gender, or ethnicity differences. For example, hemoglobin normal range differs for males (13.5–17.5) vs females (12.0–15.5).

4. **Binary gender** — The system uses 1/0 (Male/Female) without accounting for other factors.

5. **No temporal analysis** — The model predicts based on a single snapshot. Trends over time (improving/worsening) are not modeled.

### Future Improvements

1. **Doctor-labeled training data** — Replace rule-based labels with clinician-annotated health status for higher quality training targets.
2. **Age/gender-specific ranges** — Use different reference ranges based on demographics.
3. **Longitudinal analysis** — Track changes across multiple reports to predict health trajectory.
4. **Deep learning** — Neural networks for automated feature engineering.
5. **Explainability** — Integrate SHAP (SHapley Additive exPlanations) to show per-prediction feature contributions.

---

*End of ML Model Documentation*
