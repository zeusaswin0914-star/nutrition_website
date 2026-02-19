"""
Health Model Inference V2

Loads the trained pipeline (scaler + model) and provides prediction functions.
"""

import joblib
import pandas as pd
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MODEL_PATH = r"c:\Users\USER\project\version2\health_model_v2.pkl"

_MODEL_PIPELINE = None

def load_model():
    """Lazy load the model pipeline."""
    global _MODEL_PIPELINE
    if _MODEL_PIPELINE is None:
        try:
            _MODEL_PIPELINE = joblib.load(MODEL_PATH)
            logger.info(f"Loaded Health Model: {_MODEL_PIPELINE.get('model_name', 'Unknown')}")
        except Exception as e:
            logger.error(f"Failed to load health model: {e}")
            return None
    return _MODEL_PIPELINE

import json
import os

METRICS_JSON_PATH = r"c:\Users\USER\project\version2\model_metrics_health.json"

def get_dataset_metrics():
    """Load dataset-level metrics from JSON."""
    if os.path.exists(METRICS_JSON_PATH):
        try:
            with open(METRICS_JSON_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading metrics: {e}")
    return {}

def predict_health_status(input_data: dict) -> dict:
    """
    Predict health status from input dictionary.
    
    Args:
        input_data (dict): Dictionary with keys matching feature names.
                           Missing keys will be filled with 0.
    
    Returns:
        dict: {
            'status_code': int, 
            'status_label': str, 
            'confidence': float,
            'class_probabilities': dict
        }
    """
    pipeline = load_model()
    if not pipeline:
        return {'error': 'Model not loaded'}
    
    scaler = pipeline['scaler']
    model = pipeline['model']
    feature_names = pipeline['feature_names']
    
    # Prepare input vector
    vector = []
    
    for feature in feature_names:
        val = input_data.get(feature, 0)
        vector.append(val)
        
    X_input = pd.DataFrame([vector], columns=feature_names)
    
    # Scale
    X_scaled = scaler.transform(X_input)
    
    # Predict
    pred = model.predict(X_scaled)[0]
    
    STATUS_MAP = {0: 'Normal', 1: 'At Risk', 2: 'Action Needed'}
    status_label = STATUS_MAP.get(int(pred), 'Unknown')

    # Probabilities
    probs_dict = {}
    confidence = 0.0
    
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X_scaled)[0]
        confidence = float(probs.max())
        
        classes = getattr(model, 'classes_', [0, 1, 2])
        for cls, prob in zip(classes, probs):
            label = STATUS_MAP.get(int(cls), f"Class {cls}")
            probs_dict[label] = float(prob)
    else:
        confidence = 1.0
        probs_dict = {status_label: 1.0}
    
    # --- DYNAMIC RULE-BASED OVERRIDE (Fix for Static Output) ---
    # The trained model might be biased towards 'At Risk' due to dataset imbalance.
    # We apply a rule-based check to ensure status matches actual lab values.
    
    # We need to access assess_lab_values_v2 to check deviations, but circular import risk.
    # Instead, we implement a lightweight check here or assume caller handles it.
    # Actually, let's implement a heuristic here based on typical abnormal counts if available.
    # Since we don't have the full assessment here easily, we will rely on the app.py to finalize status
    # BUT, we can make this function accept an optional 'deviations' count if we change signature.
    # A better approach without changing signature:
    # Use the input_data to check for obvious outliers.
    
    # However, app.py calls this. Let's make app.py responsible for the final override 
    # based on the `assessment` result which it calculates anyway.
    # BUT the prompt asks to "Recalculate health classification per report".
    # So we will add a flag in the return dict suggesting the rule-based recommendation.
    
    # Let's perform a simple check here:
    # If any value is significantly out of normal bounds (hardcoded approx for fallback logic)
    # This ensures "Action Needed" is triggered for severe cases.
    
    # Quick checks (approximate adult ranges for override logic)
    severe_flags = 0
    mild_flags = 0
    
    if input_data.get('hemoglobin', 14) < 10 or input_data.get('hemoglobin', 14) > 18: severe_flags += 1
    if input_data.get('glucose', 90) > 140: mild_flags += 1
    if input_data.get('glucose', 90) > 200: severe_flags += 1 # Diabetic
    if input_data.get('total_cholesterol', 180) > 240: severe_flags += 1
    elif input_data.get('total_cholesterol', 180) > 200: mild_flags += 1
    
    if severe_flags > 0:
        rule_status = 'Action Needed'
    elif mild_flags > 0:
        rule_status = 'At Risk'
    else:
        rule_status = 'Normal'
        
    # If model is confident (>80%), trust model. Else if bias is suspected, potential hybrid approach.
    # For this critical bug fix, we will return the rule_recommendation so app.py can decide.
    
    return {
        'status_code': int(pred),
        'status_label': status_label,
        'confidence': confidence,
        'class_probabilities': probs_dict,
        'rule_based_status': rule_status
    }

if __name__ == "__main__":
    # Test
    sample_input = {
        'age': 35,
        'glucose': 95,
        'total_cholesterol': 180,
        'hemoglobin': 14.5
    }
    print(predict_health_status(sample_input))
    print("Metrics:", get_dataset_metrics())
