"""
Model Inference V2 for Health Status Prediction
Backend-compatible inference matching existing Flask app expectations.
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Clinical reference ranges (matching V1 nutrition_engine.py format)
NORMAL_RANGES = {
    "HGP": (12, 16),      # Hemoglobin (g/dL)
    "HGB": (12, 16),      # Alias for Hemoglobin
    "SGP": (70, 140),     # Glucose (mg/dL)
    "TCP": (125, 200),    # Total Cholesterol (mg/dL)
    "HDP": (40, 60),      # HDL (mg/dL)
    "LCP": (0, 130),      # LDL (mg/dL)
    "TGP": (0, 150),      # Triglycerides (mg/dL)
    "VAP": (20, 60),      # Vitamin A (µg/dL)
    "VEP": (500, 1800),   # Vitamin E (µg/dL)
    "VCP": (0.2, 2.0),    # Vitamin C (mg/dL)
    "FEP": (12, 300),     # Ferritin (ng/mL)
    "FOP": (2.0, 20.0),   # Folate (ng/mL)
    "UAP": (2.5, 7.2),    # Uric Acid (mg/dL)
    "CEP": (0.6, 1.3),    # Creatinine (mg/dL)
}

# Food recommendations matching V1 format
FOOD_RECO = {
    "HGP": ["Spinach", "Beetroot", "Chicken", "Eggs", "Red meat", "Lentils"],
    "HGB": ["Spinach", "Beetroot", "Chicken", "Eggs", "Red meat", "Lentils"],
    "SGP": ["Whole grains", "Green vegetables", "Nuts", "Legumes", "Berries"],
    "TCP": ["Oats", "Almonds", "Avocado", "Olive oil", "Fatty fish"],
    "HDP": ["Olive oil", "Fish", "Walnuts", "Avocado", "Nuts"],
    "LCP": ["Green tea", "Oats", "Fruits", "Fiber-rich foods", "Legumes"],
    "TGP": ["Seeds", "Leafy greens", "Whole grains", "Fatty fish", "Nuts"],
    "VAP": ["Carrots", "Sweet potato", "Leafy greens", "Liver", "Eggs"],
    "VEP": ["Nuts", "Seeds", "Vegetable oils", "Avocados", "Spinach"],
    "VCP": ["Citrus fruits", "Strawberries", "Bell peppers", "Broccoli", "Kiwi"],
    "FEP": ["Spinach", "Beans", "Red meat", "Fortified cereals", "Liver"],
    "FOP": ["Leafy greens", "Legumes", "Fortified cereals", "Citrus fruits", "Asparagus"],
    "UAP": ["Cherries", "Low-fat dairy", "Complex carbs", "Vegetables", "Water"],
    "CEP": ["Low-protein foods", "Fiber", "Vegetables", "Water", "Herbs"],
}


class ModelInferenceV2:
    """
    Backend-compatible inference class for V2 health status prediction.
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize the inference engine.
        
        Args:
            model_path: Path to model_v2.pkl. If None, uses default location.
        """
        if model_path is None:
            model_path = Path(__file__).parent / 'model_v2.pkl'
        
        self.model_path = Path(model_path)
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.label_encoder = None
        self.medians = None
        
        self._load_model()
    
    def _load_model(self):
        """Load the trained model artifact."""
        if not self.model_path.exists():
            print(f"[WARN] V2 model not found at {self.model_path}")
            return False
        
        try:
            artifact = joblib.load(self.model_path)
            self.model = artifact['model']
            self.scaler = artifact['scaler']
            self.feature_columns = artifact['feature_columns']
            self.label_encoder = artifact['label_encoder']
            self.medians = artifact.get('medians', {})
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load V2 model: {e}")
            return False
    
    def is_ready(self) -> bool:
        """Check if model is loaded and ready."""
        return self.model is not None
    
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
        
        # Prepare feature vector
        features = []
        for col in self.feature_columns:
            if col in lab_values and lab_values[col] is not None:
                features.append(float(lab_values[col]))
            elif col in self.medians:
                features.append(self.medians[col])
            else:
                features.append(0.0)
        
        # Scale and predict
        X = np.array([features])
        X_scaled = self.scaler.transform(X)
        prediction = self.model.predict(X_scaled)[0]
        
        # Decode label
        return self.label_encoder.inverse_transform([prediction])[0]
    
    def predict_with_confidence(self, lab_values: Dict[str, float]) -> Tuple[str, float]:
        """
        Predict health status with confidence score.
        
        Returns:
            Tuple of (health_status, confidence_score)
        """
        if not self.is_ready():
            return 'Unknown', 0.0
        
        # Prepare feature vector
        features = []
        for col in self.feature_columns:
            if col in lab_values and lab_values[col] is not None:
                features.append(float(lab_values[col]))
            elif col in self.medians:
                features.append(self.medians[col])
            else:
                features.append(0.0)
        
        X = np.array([features])
        X_scaled = self.scaler.transform(X)
        
        prediction = self.model.predict(X_scaled)[0]
        
        # Get probability if available
        if hasattr(self.model, 'predict_proba'):
            proba = self.model.predict_proba(X_scaled)[0]
            confidence = float(max(proba))
        else:
            confidence = 1.0
        
        return self.label_encoder.inverse_transform([prediction])[0], confidence


# Global inference instance (lazy loaded)
_inference_instance = None


def _get_inference():
    """Get or create global inference instance."""
    global _inference_instance
    if _inference_instance is None:
        _inference_instance = ModelInferenceV2()
    return _inference_instance


def predict_health_status(lab_values: Dict[str, float]) -> str:
    """
    Convenience function for health status prediction.
    Compatible with Flask backend usage.
    
    Args:
        lab_values: Dict of biomarker values
    
    Returns:
        Health status string
    """
    inference = _get_inference()
    return inference.predict_health_status(lab_values)


def analyze_biomarkers_v2(values: Dict[str, float]) -> Tuple[List[str], List[str]]:
    """
    Analyze biomarkers and identify deficiencies.
    COMPATIBLE with existing nutrition_engine.analyze_biomarkers() format.
    
    Args:
        values: Dict of biomarker values, e.g., {"HGB": 12, "SGP": 90}
    
    Returns:
        Tuple of (report_lines, deficiencies_list)
    """
    report = []
    deficiencies = []
    
    for test, (low, high) in NORMAL_RANGES.items():
        if test not in values or values[test] is None:
            continue
        
        val = values[test]
        
        try:
            val = float(val)
        except (ValueError, TypeError):
            continue
        
        if val < low:
            report.append(f"{test}: LOW ({val:.1f}, normal: {low}-{high})")
            deficiencies.append(test)
        elif val > high:
            report.append(f"{test}: HIGH ({val:.1f}, normal: {low}-{high})")
            # Some high values are also concerning
            if test in ['SGP', 'TCP', 'LCP', 'TGP', 'UAP']:
                deficiencies.append(test)
        else:
            report.append(f"{test}: Normal ({val:.1f})")
    
    # Add V2 ML prediction if available
    inference = _get_inference()
    if inference.is_ready():
        health_status = inference.predict_health_status(values)
        report.insert(0, f"Overall Health Status: {health_status}")
    
    return report, deficiencies


def recommend_foods_v2(deficiencies: List[str]) -> List[str]:
    """
    Recommend foods based on deficiencies.
    COMPATIBLE with existing nutrition_engine.recommend_foods() format.
    
    Args:
        deficiencies: List of deficient biomarker codes
    
    Returns:
        List of food recommendations
    """
    recommendations = []
    
    for d in deficiencies:
        if d in FOOD_RECO:
            foods = FOOD_RECO[d]
            recommendations.append(f"{d}: Eat → {', '.join(foods[:4])}")
    
    return recommendations


# Export for backend compatibility
__all__ = [
    'ModelInferenceV2',
    'predict_health_status',
    'analyze_biomarkers_v2',
    'recommend_foods_v2',
    'NORMAL_RANGES',
    'FOOD_RECO'
]


if __name__ == '__main__':
    # Test inference
    print("Testing Model Inference V2...")
    
    test_values = {
        'HGP': 13.5,
        'SGP': 95,
        'TCP': 180,
        'VAP': 45,
        'VEP': 1000,
        'VCP': 0.8,
        'FEP': 80
    }
    
    inference = ModelInferenceV2()
    
    if inference.is_ready():
        status = inference.predict_health_status(test_values)
        print(f"Health Status: {status}")
        
        status, conf = inference.predict_with_confidence(test_values)
        print(f"Health Status: {status} (confidence: {conf:.2f})")
        
        report, deficiencies = analyze_biomarkers_v2(test_values)
        print(f"\nReport: {report}")
        print(f"Deficiencies: {deficiencies}")
        
        if deficiencies:
            recs = recommend_foods_v2(deficiencies)
            print(f"Recommendations: {recs}")
    else:
        print("Model not loaded. Run model_training_v2.py first.")
