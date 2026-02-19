"""
Diet Model Inference V2

Loads the trained diet model and provides recommendation logic.
"""

import joblib
import pandas as pd
import numpy as np
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MODEL_PATH = r"c:\Users\USER\project\version2\diet_model_v2.pkl"

_DIET_PIPELINE = None

def load_model():
    """Lazy load the diet model pipeline."""
    global _DIET_PIPELINE
    if _DIET_PIPELINE is None:
        try:
            _DIET_PIPELINE = joblib.load(MODEL_PATH)
            logger.info(f"Loaded Diet Model: {_DIET_PIPELINE.get('model_name', 'Unknown')}")
        except Exception as e:
            logger.error(f"Failed to load diet model: {e}")
            return None
    return _DIET_PIPELINE

import json
import os

METRICS_JSON_PATH = r"c:\Users\USER\project\version2\model_metrics_diet.json"

def get_dataset_metrics():
    """Load dataset-level metrics from JSON."""
    if os.path.exists(METRICS_JSON_PATH):
        try:
            with open(METRICS_JSON_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading diet metrics: {e}")
    return {}

def predict_diet_metrics(user_profile: dict) -> dict:
    """
    Predict diet recommendations with confidence metrics.
    
    Returns:
        dict: {
            'recommendations': list,
            'confidence': float,
            'top_probabilities': dict
        }
    """
    pipeline = load_model()
    if not pipeline:
        return {'recommendations': [], 'confidence': 0.0, 'top_probabilities': {}}
    
    model = pipeline['model']
    le = pipeline['label_encoder']
    diet_map = pipeline['diet_map']
    goal_map = pipeline['goal_map']
    
    try:
        age = user_profile.get('age', 30)
        gender = user_profile.get('gender', 1)
        bmi = user_profile.get('bmi', 22.0)
        diet_str = user_profile.get('diet_type', 'Vegetarian')
        goal_str = user_profile.get('goal', 'Maintenance')
        
        diet_val = diet_map.get(diet_str, 0)
        goal_val = goal_map.get(goal_str, 1)
        
        X = pd.DataFrame([[age, gender, bmi, diet_val, goal_val]], 
                         columns=['age', 'gender', 'bmi', 'diet_encoded', 'goal_encoded'])
        
        recommendations = []
        confidence = 0.0
        top_probs = {}
        
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(X)[0]
            confidence = float(probs.max())
            
            # Get top 3
            top_3_idx = probs.argsort()[-3:][::-1]
            top_3_foods = le.inverse_transform(top_3_idx)
            recommendations = list(top_3_foods)
            
            for idx in top_3_idx:
                food = le.inverse_transform([idx])[0]
                top_probs[food] = float(probs[idx])
        else:
            pred = model.predict(X)[0]
            food = le.inverse_transform([pred])[0]
            recommendations = [food]
            confidence = 1.0
            top_probs = {food: 1.0}
            
        return {
            'recommendations': recommendations,
            'confidence': confidence,
            'top_probabilities': top_probs
        }

    except Exception as e:
        logger.error(f"Diet prediction failed: {e}")
        return {'recommendations': [], 'confidence': 0.0, 'top_probabilities': {}}

def predict_food_recommendation(user_profile: dict) -> list:
    """
    Predict recommended foods based on user profile.
    Returns a list of top 3 food recommendations.
    """
    result = predict_diet_metrics(user_profile)
    if result['recommendations']:
        return result['recommendations']
    return ["Healthy Salad", "Mixed Fruit", "Oatmeal"] # Fallback

if __name__ == "__main__":
    profile = {
        'age': 30,
        'gender': 1,
        'bmi': 24.5,
        'diet_type': 'Non-Vegetarian',
        'goal': 'Muscle Gain'
    }
    print(predict_diet_metrics(profile))
    print("Metrics:", get_dataset_metrics())
