"""
Health Status Model Training V2

Trains multiple models to predict health status (Normal, At Risk, Action Needed).
Comparisons: LogisticRegression, RandomForest, GradientBoosting, XGBoost.
Selects best model based on accuracy and F1 score.
"""

import pandas as pd
import numpy as np
import joblib
import logging
import os
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from xgboost import XGBClassifier

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
DATA_PATH = r"c:\Users\USER\project\version2\processed_data_v2.csv"
MODEL_PATH = r"c:\Users\USER\project\version2\health_model_v2.pkl"
METRICS_PATH = r"c:\Users\USER\project\version2\health_model_metrics.txt"

def train_and_evaluate():
    """Train multiple models and select the best one."""
    
    # 1. Load Data
    if not os.path.exists(DATA_PATH):
        logger.error(f"Data file not found: {DATA_PATH}")
        return

    logger.info("Loading processed data...")
    df = pd.read_csv(DATA_PATH)
    
    # Features and Target
    # Exclude target 'health_status' and potentially 'calories' (if not used for health status)
    # We use all bio-markers + demographics
    X = df.drop(columns=['health_status', 'calories'], errors='ignore')
    y = df['health_status']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 2. Define Models
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
        'XGBoost': XGBClassifier(eval_metric='mlogloss', use_label_encoder=False)
    }
    
    results = {}
    best_model_name = None
    best_score = 0
    best_model_obj = None
    
    logger.info(f"Training {len(models)} models...")
    
    # 3. Train and Evaluate
    for name, model in models.items():
        logger.info(f"Training {name}...")
        try:
            model.fit(X_train_scaled, y_train)
            
            y_pred = model.predict(X_test_scaled)
            acc = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted')
            
            logger.info(f"{name} Results - Accuracy: {acc:.4f}, F1: {f1:.4f}")
            
            results[name] = {'accuracy': acc, 'f1': f1, 'model': model}
            
            if acc > best_score:
                best_score = acc
                best_model_name = name
                best_model_obj = model
        except Exception as e:
            logger.error(f"Failed to train {name}: {e}")
            
    # 4. Save Best Model
    if best_model_obj:
        logger.info(f"Best Model: {best_model_name} with Accuracy: {best_score:.4f}")
        
        # Save pipeline (Scaler + Model)
        # We need a wrapper to handle scaling during inference easily
        final_pipeline = {
            'scaler': scaler,
            'model': best_model_obj,
            'feature_names': X.columns.tolist(),
            'model_name': best_model_name,
            'metrics': results[best_model_name]
        }
        
        joblib.dump(final_pipeline, MODEL_PATH)
        logger.info(f"Model saved to {MODEL_PATH}")
        
        # Save detailed metrics to text file
        with open(METRICS_PATH, 'w') as f:
            f.write(f"Health Model Evaluation V2\n")
            f.write("==========================\n")
            f.write(f"Best Model: {best_model_name}\n")
            f.write(f"Accuracy: {best_score:.4f}\n\n")
            f.write("All Model Results:\n")
            for name, res in results.items():
                f.write(f"{name}: Acc={res['accuracy']:.4f}, F1={res['f1']:.4f}\n")
            
            f.write("\nProcess completed successfully.\n")

if __name__ == "__main__":
    train_and_evaluate()
