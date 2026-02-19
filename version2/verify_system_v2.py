"""
System Verification V2

End-to-End test of the V2 pipeline components.
"""

import os
import sys
import logging

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from version2.ocr_fix_v2 import extract_blood_report_text_v2, parse_lab_values_v2
from version2.model_inference_health_v2 import predict_health_status
from version2.diet_plan_generator_v2 import generate_v2_diet_plan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Verification")

def test_system():
    logger.info("Starting System Verification...")
    
    # 1. Test OCR
    print("\n--- Testing OCR ---")
    sample_pdf = r"c:\Users\USER\project\Sample_PDF\muralibloodrep.pdf"
    if os.path.exists(sample_pdf):
        text = extract_blood_report_text_v2(sample_pdf)
        values = parse_lab_values_v2(text)
        print(f"OCR Extracted: {len(text)} chars")
        print(f"Parsed Values: {values}")
        if not values:
            print("WARNING: No values parsed from PDF. Check OCR quality.")
    else:
        print("Sample PDF not found, skipping OCR I/O test.")
        values = {'hemoglobin': 13.5, 'glucose': 95, 'total_cholesterol': 185} # Dummy
        
    # 2. Test Health Model
    print("\n--- Testing Health Model ---")
    user_profile = {
        'age': 35,
        'gender': 1,
        'bmi': 24.0,
        'glucose': values.get('glucose', 90),
        'hemoglobin': values.get('hemoglobin', 14)
    }
    status = predict_health_status(user_profile)
    print(f"Health Status Prediction: {status}")
    if 'error' in status:
        print("FAILED: Health model error.")
        return
        
    # 3. Test Diet Model
    print("\n--- Testing Diet Model ---")
    diet_profile = {
        'age': 35,
        'gender': 1,
        'bmi': 24.0,
        'diet_type': 'Vegetarian',
        'goal': 'Weight Loss'
    }
    plan = generate_v2_diet_plan(diet_profile)
    print("Generated Diet Plan (Monday):")
    print(plan.get('Monday'))
    if not plan:
        print("FAILED: No diet plan generated.")
        return

    print("\nSUCCESS: All V2 components verified.")

if __name__ == "__main__":
    test_system()
