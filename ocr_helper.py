"""OCR text extraction from blood report PDFs and images."""

import os
import cv2
import pytesseract
from PIL import Image
import re
from datetime import datetime


def extract_text_from_image(image_path):
    """Extract text from an image file using pytesseract."""
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    Note: For simple PDF to text, we use a basic approach.
    For more complex PDFs, consider using pdfplumber or PyPDF2.
    """
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    except ImportError:
        # Fallback: treat PDF as image
        print("pdfplumber not installed. Attempting image-based extraction...")
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(pdf_path)
            text = ""
            for img in images:
                text += pytesseract.image_to_string(img) + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""


def extract_blood_report_text(file_path):
    """
    Extract text from a blood report file (PDF, PNG, JPG).
    
    Args:
        file_path: Path to the blood report file
        
    Returns:
        Extracted text as string
    """
    _, ext = os.path.splitext(file_path.lower())
    
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['.png', '.jpg', '.jpeg']:
        return extract_text_from_image(file_path)
    else:
        print(f"Unsupported file format: {ext}")
        return ""


def parse_lab_values(extracted_text):
    """
    Parse common lab values from extracted text.
    
    Returns a dict with detected lab values and their readings.
    """
    lab_values = {}
    
    # Common lab test patterns (simplified regex patterns)
    patterns = {
        'hemoglobin': r'hemoglobin|hb|hgb|hgh\s*[:=]?\s*([\d.]+)\s*(g/dl|g/dL)',
        'hematocrit': r'hematocrit|hct\s*[:=]?\s*([\d.]+)\s*(%)',
        'iron': r'iron|fe\s*[:=]?\s*([\d.]+)\s*(µg/dl|mcg/dl)',
        'ferritin': r'ferritin\s*[:=]?\s*([\d.]+)\s*(ng/ml|mcg/l)',
        'vitamin_d': r'vitamin\s*d|vit\s*d\s*[:=]?\s*([\d.]+)\s*(ng/ml|nmol/l)',
        'calcium': r'calcium|ca\s*[:=]?\s*([\d.]+)\s*(mg/dl)',
        'phosphorus': r'phosphorus|p\s*[:=]?\s*([\d.]+)\s*(mg/dl)',
        'glucose': r'glucose|fasting\s*glucose\s*[:=]?\s*([\d.]+)\s*(mg/dl)',
        'total_cholesterol': r'total\s*cholesterol\s*[:=]?\s*([\d.]+)\s*(mg/dl)',
        'ldl': r'ldl\s*[:=]?\s*([\d.]+)\s*(mg/dl)',
        'hdl': r'hdl\s*[:=]?\s*([\d.]+)\s*(mg/dl)',
        'triglycerides': r'triglycerides\s*[:=]?\s*([\d.]+)\s*(mg/dl)',
        'albumin': r'albumin\s*[:=]?\s*([\d.]+)\s*(g/dl)',
        'protein': r'total\s*protein|protein\s*[:=]?\s*([\d.]+)\s*(g/dl)',
        'bmi': r'bmi\s*[:=]?\s*([\d.]+)\s*(kg/m2)',
    }
    
    text_lower = extracted_text.lower()
    
    for test_name, pattern in patterns.items():
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            if len(match.groups()) >= 1:
                try:
                    value = float(match.group(1))
                    lab_values[test_name] = value
                except (ValueError, IndexError):
                    pass
    
    return lab_values


def get_lab_value_ranges(age_category):
    """
    Get normal lab value ranges for a specific age category.
    
    Returns a dict with normal ranges for common lab tests.
    """
    ranges = {
        'toddler': {
            'hemoglobin': {'min': 10.5, 'max': 13.5, 'unit': 'g/dL'},
            'hematocrit': {'min': 33, 'max': 39, 'unit': '%'},
            'iron': {'min': 30, 'max': 100, 'unit': 'µg/dL'},
            'calcium': {'min': 8.5, 'max': 10.2, 'unit': 'mg/dL'},
            'glucose': {'min': 70, 'max': 100, 'unit': 'mg/dL'},
            'albumin': {'min': 3.5, 'max': 5.5, 'unit': 'g/dL'},
        },
        'child': {
            'hemoglobin': {'min': 11.5, 'max': 15.5, 'unit': 'g/dL'},
            'hematocrit': {'min': 35, 'max': 45, 'unit': '%'},
            'iron': {'min': 40, 'max': 100, 'unit': 'µg/dL'},
            'calcium': {'min': 8.5, 'max': 10.2, 'unit': 'mg/dL'},
            'glucose': {'min': 70, 'max': 100, 'unit': 'mg/dL'},
            'albumin': {'min': 3.5, 'max': 5.5, 'unit': 'g/dL'},
        },
        'teen': {
            'hemoglobin': {'min': 12.0, 'max': 16.0, 'unit': 'g/dL'},  # Males
            'hematocrit': {'min': 36, 'max': 46, 'unit': '%'},
            'iron': {'min': 50, 'max': 120, 'unit': 'µg/dL'},
            'calcium': {'min': 8.5, 'max': 10.2, 'unit': 'mg/dL'},
            'glucose': {'min': 70, 'max': 100, 'unit': 'mg/dL'},
            'albumin': {'min': 3.5, 'max': 5.5, 'unit': 'g/dL'},
        },
        'adult': {
            'hemoglobin': {'min': 13.5, 'max': 17.5, 'unit': 'g/dL'},  # Males
            'hematocrit': {'min': 41, 'max': 53, 'unit': '%'},
            'iron': {'min': 60, 'max': 170, 'unit': 'µg/dL'},
            'ferritin': {'min': 30, 'max': 300, 'unit': 'ng/mL'},
            'vitamin_d': {'min': 30, 'max': 100, 'unit': 'ng/mL'},
            'calcium': {'min': 8.5, 'max': 10.2, 'unit': 'mg/dL'},
            'glucose': {'min': 70, 'max': 100, 'unit': 'mg/dL'},
            'total_cholesterol': {'min': 0, 'max': 200, 'unit': 'mg/dL'},
            'ldl': {'min': 0, 'max': 100, 'unit': 'mg/dL'},
            'hdl': {'min': 40, 'max': 999, 'unit': 'mg/dL'},  # Higher is better
            'triglycerides': {'min': 0, 'max': 150, 'unit': 'mg/dL'},
            'albumin': {'min': 3.5, 'max': 5.5, 'unit': 'g/dL'},
        },
        'senior': {
            'hemoglobin': {'min': 12.0, 'max': 17.5, 'unit': 'g/dL'},
            'hematocrit': {'min': 36, 'max': 50, 'unit': '%'},
            'iron': {'min': 40, 'max': 170, 'unit': 'µg/dL'},
            'ferritin': {'min': 30, 'max': 400, 'unit': 'ng/mL'},
            'vitamin_d': {'min': 30, 'max': 100, 'unit': 'ng/mL'},
            'calcium': {'min': 8.5, 'max': 10.2, 'unit': 'mg/dL'},
            'glucose': {'min': 70, 'max': 100, 'unit': 'mg/dL'},
            'total_cholesterol': {'min': 0, 'max': 200, 'unit': 'mg/dL'},
            'ldl': {'min': 0, 'max': 100, 'unit': 'mg/dL'},
            'hdl': {'min': 40, 'max': 999, 'unit': 'mg/dL'},
            'triglycerides': {'min': 0, 'max': 150, 'unit': 'mg/dL'},
            'albumin': {'min': 3.5, 'max': 5.5, 'unit': 'g/dL'},
        }
    }
    
    return ranges.get(age_category, ranges['adult'])


def assess_lab_values(lab_values, age_category):
    """
    Assess lab values against age-appropriate ranges.
    
    Returns a list of assessments with status (normal, low, high) and recommendations.
    """
    ranges = get_lab_value_ranges(age_category)
    assessments = []
    
    for test_name, value in lab_values.items():
        if test_name in ranges:
            range_info = ranges[test_name]
            min_val = range_info['min']
            max_val = range_info['max']
            unit = range_info['unit']
            
            if value < min_val:
                status = 'LOW'
                severity = 'concern'
            elif value > max_val:
                status = 'HIGH'
                severity = 'concern'
            else:
                status = 'NORMAL'
                severity = 'ok'
            
            assessments.append({
                'test': test_name.replace('_', ' ').title(),
                'value': value,
                'unit': unit,
                'normal_range': f"{min_val}-{max_val}",
                'status': status,
                'severity': severity
            })
    
    return assessments
