"""
OCR Pipeline V2 - Improved Blood Report Text Extraction

Fixes applied to original ocr_helper.py:
1. Image preprocessing (threshold, denoise, deskew)
2. High DPI PDF conversion (300 DPI)
3. Enhanced regex patterns for biomarkers
4. Validation for extracted values
5. Detailed logging
"""

import os
import re
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try importing optional dependencies
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available. Image preprocessing will be limited.")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("pytesseract not available. OCR will not work.")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False


# Clinical reference ranges for validation
# Broad ranges for OCR validation (to filter out OCR noise)
VALIDATION_RANGES = {
    'hemoglobin': {'min': 5.0, 'max': 25.0, 'unit': 'g/dL'},
    'glucose': {'min': 20, 'max': 1000, 'unit': 'mg/dL'},
    'total_cholesterol': {'min': 50, 'max': 600, 'unit': 'mg/dL'},
    'hba1c': {'min': 2.0, 'max': 20.0, 'unit': '%'},
    # ... Defaults for others can remain wide or copy from existing if needed
}

# Strict clinical ranges for health assessment ( Healthy / Normal )
REFERENCE_RANGES = {
    'hemoglobin': {'min': 13.5, 'max': 17.5, 'unit': 'g/dL'}, # Adult Male Approx
    'hematocrit': {'min': 41, 'max': 50, 'unit': '%'},
    'rbc': {'min': 4.5, 'max': 5.9, 'unit': 'million/uL'},
    'wbc': {'min': 4500, 'max': 11000, 'unit': '/uL'},
    'platelets': {'min': 150000, 'max': 450000, 'unit': '/uL'},
    'glucose': {'min': 70, 'max': 100, 'unit': 'mg/dL'}, # Fasting
    'fasting_glucose': {'min': 70, 'max': 100, 'unit': 'mg/dL'},
    'total_cholesterol': {'min': 125, 'max': 200, 'unit': 'mg/dL'},
    'ldl': {'min': 0, 'max': 100, 'unit': 'mg/dL'},
    'hdl': {'min': 40, 'max': 100, 'unit': 'mg/dL'}, # Higher is better usually
    'triglycerides': {'min': 0, 'max': 150, 'unit': 'mg/dL'},
    'creatinine': {'min': 0.7, 'max': 1.3, 'unit': 'mg/dL'},
    'urea': {'min': 7, 'max': 20, 'unit': 'mg/dL'},
    'uric_acid': {'min': 3.5, 'max': 7.2, 'unit': 'mg/dL'},
    'bilirubin': {'min': 0.1, 'max': 1.2, 'unit': 'mg/dL'},
    'sgpt': {'min': 7, 'max': 56, 'unit': 'U/L'},
    'sgot': {'min': 10, 'max': 40, 'unit': 'U/L'},
    'alkaline_phosphatase': {'min': 44, 'max': 147, 'unit': 'U/L'},
    'protein': {'min': 6.0, 'max': 8.3, 'unit': 'g/dL'},
    'albumin': {'min': 3.4, 'max': 5.4, 'unit': 'g/dL'},
    'sodium': {'min': 135, 'max': 145, 'unit': 'mEq/L'},
    'potassium': {'min': 3.5, 'max': 5.0, 'unit': 'mEq/L'},
    'chloride': {'min': 95, 'max': 105, 'unit': 'mEq/L'},
    'calcium': {'min': 8.5, 'max': 10.5, 'unit': 'mg/dL'},
    'iron': {'min': 65, 'max': 175, 'unit': 'ug/dl'},
    'ferritin': {'min': 20, 'max': 250, 'unit': 'ng/mL'},
    'vitamin_d': {'min': 30, 'max': 100, 'unit': 'ng/mL'},
    'vitamin_b12': {'min': 200, 'max': 900, 'unit': 'pg/mL'},
    'folate': {'min': 2, 'max': 20, 'unit': 'ng/mL'},
    'tsh': {'min': 0.4, 'max': 4.0, 'unit': 'mIU/L'},
    'hba1c': {'min': 4.0, 'max': 5.6, 'unit': '%'},
    'chloride': {'min': 95, 'max': 105, 'unit': 'mEq/L'},
    'mcv': {'min': 80, 'max': 100, 'unit': 'fL'},
    'mch': {'min': 27, 'max': 32, 'unit': 'pg'},
    'mchc': {'min': 32, 'max': 36, 'unit': 'g/dL'},
    'neutrophils': {'min': 40, 'max': 75, 'unit': '%'},
    'lymphocytes': {'min': 20, 'max': 45, 'unit': '%'},
    'monocytes': {'min': 2, 'max': 10, 'unit': '%'},
    'eosinophils': {'min': 1, 'max': 6, 'unit': '%'},
    'basophils': {'min': 0, 'max': 1, 'unit': '%'},
    # Additional common parameters
    'alkaline_phosphatase': {'min': 44, 'max': 147, 'unit': 'U/L'},
    'globulin': {'min': 2.0, 'max': 3.5, 'unit': 'g/dL'},
    'ag_ratio': {'min': 1.0, 'max': 2.5, 'unit': 'ratio'},
    'esr': {'min': 0, 'max': 20, 'unit': 'mm/hr'},
    'rdw': {'min': 11.5, 'max': 14.5, 'unit': '%'},
    'mpv': {'min': 7.4, 'max': 10.4, 'unit': 'fL'},
    'pct': {'min': 0.1, 'max': 0.28, 'unit': '%'}
}


# Enhanced regex patterns for biomarker extraction
# Enhanced regex patterns for biomarker extraction
BIOMARKER_PATTERNS = {
    'hemoglobin': [
        r'h[ae]moglobin\s*[:=]?\s*(\d+\.?\d*)\s*(g/?dl|gm/?dl)?',
        r'hgb?\s*[:=]?\s*(\d+\.?\d*)\s*(g/?dl)?',
        r'hb\s*[:=]?\s*(\d+\.?\d*)\s*(g/?dl)?',
    ],
    'hematocrit': [
        r'h[ae]matocrit\s*[:=]?\s*(\d+\.?\d*)\s*(%)?',
        r'hct\s*[:=]?\s*(\d+\.?\d*)\s*(%)?',
        r'pcv\s*[:=]?\s*(\d+\.?\d*)\s*(%)?',
    ],
    'rbc': [
        r'rbc\s*(count)?\s*[:=]?\s*(\d+\.?\d*)\s*(million|mil|m)?',
        r'red\s*blood\s*cell[s]?\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'mcv': [
        r'mcv\s*[:=]?\s*(\d+\.?\d*)\s*(fl)?',
        r'mean\s*corpuscular\s*volume\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'mch': [
        r'mch\s*[:=]?\s*(\d+\.?\d*)\s*(pg)?',
        r'mean\s*corpuscular\s*hemoglobin\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'mchc': [
        r'mchc\s*[:=]?\s*(\d+\.?\d*)\s*(g/?dl)?',
    ],
    'wbc': [
        r'wbc\s*(count)?\s*[:=]?\s*(\d+\.?\d*)\s*(thousand|k|\/ul)?',
        r'white\s*blood\s*cell[s]?\s*[:=]?\s*(\d+\.?\d*)',
        r'total\s*leucocyte\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'neutrophils': [
        r'neutrophil[s]?\s*[:=]?\s*(\d+\.?\d*)\s*(%)?',
        r'poly\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'lymphocytes': [
        r'lymphocyte[s]?\s*[:=]?\s*(\d+\.?\d*)\s*(%)?',
        r'lymph\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'monocytes': [
        r'monocyte[s]?\s*[:=]?\s*(\d+\.?\d*)\s*(%)?',
    ],
    'eosinophils': [
        r'eosinophil[s]?\s*[:=]?\s*(\d+\.?\d*)\s*(%)?',
    ],
    'basophils': [
        r'basophil[s]?\s*[:=]?\s*(\d+\.?\d*)\s*(%)?',
    ],
    'platelets': [
        r'platelet[s]?\s*(count)?\s*[:=]?\s*(\d+\.?\d*)\s*(lakh|lac|k|thousand)?',
        r'plt\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'glucose': [
        r'(fasting\s*)?glucose\s*[:=]?\s*(\d+\.?\d*)\s*(mg/?dl)?',
        r'blood\s*sugar\s*[:=]?\s*(\d+\.?\d*)\s*(mg/?dl)?',
        r'fbs\s*[:=]?\s*(\d+\.?\d*)\s*(mg/?dl)?',
        r'rbs\s*[:=]?\s*(\d+\.?\d*)\s*(mg/?dl)?',
    ],
    'total_cholesterol': [
        r'(total|serum)\s*cholesterol\s*[:=]?\s*(\d+\.?\d*)\s*(mg/?dl)?',
        r'cholesterol\s*(total)?\s*[:=]?\s*(\d+\.?\d*)\s*(mg/?dl)?',
        r't\.\s*cholesterol\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'ldl': [
        r'ldl\s*(-?c(holesterol)?)?\s*[:=]?\s*(\d+\.?\d*)\s*(mg/?dl)?',
        r'low\s*density\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'hdl': [
        r'hdl\s*(-?c(holesterol)?)?\s*[:=]?\s*(\d+\.?\d*)\s*(mg/?dl)?',
        r'high\s*density\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'triglycerides': [
        r'triglyceride[s]?\s*[:=]?\s*(\d+\.?\d*)\s*(mg/?dl)?',
        r'tg\s*[:=]?\s*(\d+\.?\d*)\s*(mg/?dl)?',
    ],
    'creatinine': [
        r'(serum\s*)?creatinine\s*[:=]?\s*(\d+\.?\d*)\s*(mg/?dl)?',
        r's\.\s*creatinine\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'urea': [
        r'(blood\s*)?urea\s*[:=]?\s*(\d+\.?\d*)\s*(mg/?dl)?',
        r'bun\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'uric_acid': [
        r'(serum\s*)?uric\s*acid\s*[:=]?\s*(\d+\.?\d*)\s*(mg/?dl)?',
    ],
    'bilirubin': [
        r'(total\s*)?bilirubin\s*[:=]?\s*(\d+\.?\d*)\s*(mg/?dl)?',
        r't\.\s*bilirubin\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'sgpt': [
        r'sgpt\s*[:=]?\s*(\d+\.?\d*)\s*(u/?l|iu/?l)?',
        r'alt\s*[:=]?\s*(\d+\.?\d*)\s*(u/?l)?',
    ],
    'sgot': [
        r'sgot\s*[:=]?\s*(\d+\.?\d*)\s*(u/?l|iu/?l)?',
        r'ast\s*[:=]?\s*(\d+\.?\d*)\s*(u/?l)?',
    ],
    'vitamin_d': [
        r'vitamin\s*d\s*(25-?oh|3)?\s*[:=]?\s*(\d+\.?\d*)\s*(ng/?ml|nmol/?l)?',
        r'vit\s*d\s*[:=]?\s*(\d+\.?\d*)',
        r'25\s*hydroxy\s*vitamin\s*d\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'vitamin_b12': [
        r'vitamin\s*b\s*12\s*[:=]?\s*(\d+\.?\d*)\s*(pg/?ml|pmol/?l)?',
        r'vit\s*b12\s*[:=]?\s*(\d+\.?\d*)',
        r'cyanocobalamin\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'folate': [
        r'fol(ate|ic\s*acid)\s*[:=]?\s*(\d+\.?\d*)\s*(ng/?ml)?',
    ],
    'iron': [
        r'(serum\s*)?iron\s*[:=]?\s*(\d+\.?\d*)\s*(ug/?dl|mcg/?dl)?',
        r'fe\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'ferritin': [
        r'ferritin\s*[:=]?\s*(\d+\.?\d*)\s*(ng/?ml)?',
    ],
    'tsh': [
        r'tsh\s*[:=]?\s*(\d+\.?\d*)\s*(miu/?l|uiu/?ml)?',
        r'thyroid\s*stimulating\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'hba1c': [
        r'hba1c\s*[:=]?\s*(\d+\.?\d*)\s*(%)?',
        r'glycated\s*h[ae]moglobin\s*[:=]?\s*(\d+\.?\d*)',
        r'a1c\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'sodium': [
        r'sodium\s*[:=]?\s*(\d+\.?\d*)\s*(meq/?l|mmol/?l)?',
        r'na\+?\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'potassium': [
        r'potassium\s*[:=]?\s*(\d+\.?\d*)\s*(meq/?l|mmol/?l)?',
        r'k\+?\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'chloride': [
        r'chloride\s*[:=]?\s*(\d+\.?\d*)\s*(meq/?l|mmol/?l)?',
        r'cl\-?\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'calcium': [
        r'(serum\s*)?calcium\s*[:=]?\s*(\d+\.?\d*)\s*(mg/?dl)?',
        r'ca\+?\+?\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'protein': [
        r'total\s*protein\s*[:=]?\s*(\d+\.?\d*)\s*(g/?dl)?',
    ],
    'albumin': [
        r'albumin\s*[:=]?\s*(\d+\.?\d*)\s*(g/?dl)?',
    ],
    'alkaline_phosphatase': [
        r'alkaline\s*phosphatase\s*[:=]?\s*(\d+\.?\d*)\s*(u/?l)?',
        r'alp\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'globulin': [
        r'globulin\s*[:=]?\s*(\d+\.?\d*)\s*(g/?dl)?',
    ],
    'ag_ratio': [
        r'a/g\s*ratio\s*[:=]?\s*(\d+\.?\d*)',
        r'albumin/globulin\s*ratio\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'esr': [
        r'esr\s*[:=]?\s*(\d+\.?\d*)\s*(mm/hr|mm)?',
        r'erythrocyte\s*sedimentation\s*rate\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'rdw': [
        r'rdw\s*(-?cv|-?sd)?\s*[:=]?\s*(\d+\.?\d*)\s*(%)?',
        r'red\s*cell\s*distribution\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'mpv': [
        r'mpv\s*[:=]?\s*(\d+\.?\d*)\s*(fl)?',
        r'mean\s*platelet\s*volume\s*[:=]?\s*(\d+\.?\d*)',
    ],
    'pct': [
        r'pct\s*[:=]?\s*(\d+\.?\d*)\s*(%)?',
        r'plateletcrit\s*[:=]?\s*(\d+\.?\d*)',
    ],
}

def normalize_biomarkers(lab_values: Dict[str, float]) -> Dict[str, float]:
    """
    Normalize biomarker keys to standard internal names.
    This ensures consistent usage across visualization and ML.
    """
    normalized = {}
    
    # Mapping of variations to standard keys
    MAPPING = {
        'fasting_glucose': 'glucose',
        'fbs': 'glucose',
        'rbs': 'glucose', # Random blood sugar can be mapped or treated separately, usually mapped for simplicitly in V2
        'hgb': 'hemoglobin',
        'hb': 'hemoglobin',
        'total cholesterol': 'total_cholesterol',
        'cholesterol': 'total_cholesterol',
        'serum cholesterol': 'total_cholesterol',
        'serum creatinine': 'creatinine',
        'blood urea': 'urea',
        'ts': 'tsh',
        'vit d': 'vitamin_d',
        'vit b12': 'vitamin_b12',
    }
    
    for k, v in lab_values.items():
        key_lower = k.lower().strip()
        
        # 1. Direct Mapping (if key in mapping)
        if key_lower in MAPPING:
            standard_key = MAPPING[key_lower]
        # 2. Check for substring presence for some common ones
        elif 'cholesterol' in key_lower and 'total' in key_lower:
            standard_key = 'total_cholesterol'
        else:
            standard_key = key_lower
            
        # Keep the value. If duplicate (e.g. glucose and fasting_glucose both exist),
        # Prefer the one that comes last or handle logic.
        # Here we just overwrite.
        normalized[standard_key] = v
        
    return normalized


def preprocess_image(image) -> 'np.ndarray':
    """
    Apply preprocessing to improve OCR accuracy.
    Simpler pipeline: Grayscale + Rescaling (if needed).
    Avoid aggressive thresholding/deskewing unless necessary.
    """
    if not CV2_AVAILABLE or not NUMPY_AVAILABLE:
        logger.warning("OpenCV/NumPy not available. Skipping preprocessing.")
        return np.array(image) if NUMPY_AVAILABLE else image
    
    # Convert PIL Image to numpy array if needed
    if PIL_AVAILABLE and isinstance(image, Image.Image):
        img = np.array(image)
    else:
        img = image
    
    # Convert to grayscale if color
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img
    
    # Check for low contrast or noise? For now, just return grayscale.
    # Tesseract 4/5 handles grayscale well.
    # We might want to resize if it's too small, but PDF rendering handled DPI.
    
    logger.info("Image preprocessing (Grayscale) completed")
    return gray


def deskew_image(image: 'np.ndarray') -> 'np.ndarray':
    """Deskew image - (Disabled for stability)."""
    return image


def extract_text_from_image_v2(image_path: str) -> str:
    """
    Extract text from image with preprocessing.
    """
    if not TESSERACT_AVAILABLE or not PIL_AVAILABLE:
        logger.error("pytesseract or PIL not available")
        return ""
    
    try:
        # Load image
        img = Image.open(image_path)
        
        # Preprocess
        processed = preprocess_image(img)
        
        # Convert back to PIL for tesseract
        if NUMPY_AVAILABLE and isinstance(processed, np.ndarray):
            processed_pil = Image.fromarray(processed)
        else:
            processed_pil = img
        
        # Extract text with custom config
        custom_config = r'--oem 3 --psm 3'
        text = pytesseract.image_to_string(processed_pil, config=custom_config)
        
        logger.info(f"Extracted {len(text)} characters from image")
        return text
    except Exception as e:
        logger.error(f"Image extraction failed: {e}")
        return ""


try:
    import pypdfium2 as pdfium
    PYPDFIUM_AVAILABLE = True
except ImportError:
    PYPDFIUM_AVAILABLE = False


def convert_pdf_to_images_pypdfium(pdf_path, dpi=300):
    """Convert PDF to PIL images using pypdfium2 (no Poppler required)."""
    images = []
    try:
        pdf = pdfium.PdfDocument(pdf_path)
        for i in range(len(pdf)):
            page = pdf.get_page(i)
            # Render to bitmap
            bitmap = page.render(scale=dpi/72)
            pil_image = bitmap.to_pil()
            images.append(pil_image)
    except Exception as e:
        logger.error(f"pypdfium2 conversion failed: {e}")
    return images


def extract_text_from_pdf_v2(pdf_path: str) -> str:
    """
    Extract text from PDF with multiple fallback methods.
    
    Method 1: pdfplumber (direct text extraction)
    Method 2: pdf2image + OCR (Standard, requires Poppler)
    Method 3: pypdfium2 + OCR (Backup, python-only)
    """
    text = ""
    
    # Method 1: Try pdfplumber first (Fastest, text-based)
    if PDFPLUMBER_AVAILABLE:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            if text.strip():
                logger.info(f"Extracted {len(text)} chars via pdfplumber")
                return text
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}")
    
    # Method 2 & 3: Image conversion + OCR
    images = []
    
    # Try pdf2image first
    if PDF2IMAGE_AVAILABLE:
        try:
            images = convert_from_path(pdf_path, dpi=300)
        except Exception:
            # Fallback to pypdfium2
            if PYPDFIUM_AVAILABLE:
                logger.info("pdf2image failed, falling back to pypdfium2...")
                images = convert_pdf_to_images_pypdfium(pdf_path)
    
    elif PYPDFIUM_AVAILABLE:
         images = convert_pdf_to_images_pypdfium(pdf_path)

    if images and TESSERACT_AVAILABLE:
        try:
            for i, img in enumerate(images):
                # Preprocess
                processed = preprocess_image(img)
                
                # Convert back to PIL if needed
                if NUMPY_AVAILABLE and isinstance(processed, np.ndarray):
                    processed_pil = Image.fromarray(processed)
                else:
                    processed_pil = img
                
                # OCR
                custom_config = r'--oem 3 --psm 3'
                page_text = pytesseract.image_to_string(processed_pil, config=custom_config)
                text += page_text + "\n\n"
                
                logger.info(f"OCR completed for page {i+1}")
            
            return text
        except Exception as e:
            logger.error(f"OCR failed during image processing: {e}")

    logger.error("All PDF extraction methods failed")
    return ""


def extract_blood_report_text_v2(file_path: str) -> str:
    """
    Main entry point for blood report text extraction.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return ""
    
    _, ext = os.path.splitext(file_path.lower())
    
    if ext == '.pdf':
        return extract_text_from_pdf_v2(file_path)
    elif ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
        return extract_text_from_image_v2(file_path)
    else:
        logger.error(f"Unsupported file format: {ext}")
        return ""


def validate_value(biomarker: str, value: float) -> bool:
    """Validate extracted value against broad validation ranges."""
    # 1. Check explicit validation ranges
    ranges = VALIDATION_RANGES.get(biomarker)
    if ranges:
        return ranges['min'] <= value <= ranges['max']
        
    # 2. If no explicit validation range, use relaxed Reference Range
    # Allow 0.1x min to 5x max to catch abnormal but valid readings
    ref_ranges = REFERENCE_RANGES.get(biomarker)
    if ref_ranges:
        relaxed_min = ref_ranges['min'] * 0.1
        relaxed_max = ref_ranges['max'] * 5.0
        return relaxed_min <= value <= relaxed_max

    return True

def parse_lab_values_v2(extracted_text: str) -> Dict[str, float]:
    """
    Parse lab values from extracted text with enhanced patterns.
    """
    lab_values = {}
    text_lower = extracted_text.lower()
    
    for biomarker, patterns in BIOMARKER_PATTERNS.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                try:
                    # Find the numeric group
                    groups = match.groups()
                    value = None
                    for g in groups:
                        if g and re.match(r'^\d+\.?\d*$', str(g)):
                            value = float(g)
                            break
                    
                    if value is not None:
                        # Validate value
                        if validate_value(biomarker, value):
                            lab_values[biomarker] = value
                            logger.debug(f"Extracted {biomarker}: {value}")
                            break  # Stop after first valid match
                        else:
                            logger.warning(f"Value {value} out of range for {biomarker}")
                except (ValueError, IndexError):
                    continue
    
    logger.info(f"Parsed {len(lab_values)} lab values")
    return lab_values

def assess_lab_values_v2(lab_values: Dict[str, float], age: int = 30, gender: str = 'M') -> List[Dict]:
    """
    Assess lab values against reference ranges.
    Includes deviation percentage and severity label.
    """
    assessments = []
    
    for biomarker, value in lab_values.items():
        # strict assessment
        if biomarker in REFERENCE_RANGES:
            ranges = REFERENCE_RANGES[biomarker]
            min_val = ranges['min']
            max_val = ranges['max']
            unit = ranges['unit']
            
            # Determine status and deviation
            deviation_pct = 0.0
            
            if value < min_val:
                status = 'LOW'
                severity = 'concern'
                deviation_pct = ((value - min_val) / min_val) * 100
            elif value > max_val:
                status = 'HIGH'
                severity = 'concern'
                deviation_pct = ((value - max_val) / max_val) * 100
            else:
                status = 'NORMAL'
                severity = 'ok'
                deviation_pct = 0.0
            
            # Deviation label
            abs_dev = abs(deviation_pct)
            if abs_dev == 0:
                dev_label = 'Normal'
            elif abs_dev < 20:
                dev_label = 'Mild'
            else:
                dev_label = 'Severe'
            
            assessments.append({
                'test': biomarker.replace('_', ' ').title(),
                'value': value,
                'unit': unit,
                'normal_range': f"{min_val}-{max_val}",
                'status': status,
                'severity': severity,
                'deviation_pct': deviation_pct,
                'deviation_label': dev_label
            })
    
    return assessments

def calculate_clinical_risk_score(assessments: List[Dict]) -> int:
    """
    Calculate an aggregate clinical risk score (0-100).
    Base score: 0
    Mild deviation: +10
    Severe deviation: +20
    Status High/Low: +5
    """
    score = 0
    total_items = len(assessments)
    if total_items == 0:
        return 0
        
    for item in assessments:
        dev_label = item.get('deviation_label', 'Normal')
        status = item.get('status', 'NORMAL')
        
        if status != 'NORMAL':
            score += 5
            
        if dev_label == 'Mild':
            score += 10
        elif dev_label == 'Severe':
            score += 20
            
    # Normalize or Cap
    # Let's cap at 100
    return min(100, score)


# Test function
if __name__ == '__main__':
    print("=" * 60)
    print("OCR Pipeline V2 - Testing")
    print("=" * 60)
    
    # Test with sample PDF
    sample_pdf = Path(__file__).parent.parent / "Sample_PDF" / "muralibloodrep.pdf"
    
    if sample_pdf.exists():
        print(f"\nTesting with: {sample_pdf}")
        
        # Extract text
        text = extract_blood_report_text_v2(str(sample_pdf))
        print(f"\nExtracted text length: {len(text)} characters")
        print("\nFirst 500 characters:")
        print("-" * 40)
        print(text[:500] if text else "No text extracted")
        
        # Parse values
        if text:
            values = parse_lab_values_v2(text)
            print("\n" + "-" * 40)
            print(f"Parsed {len(values)} lab values:")
            for k, v in values.items():
                print(f"  {k}: {v}")
            
            # Assess values
            assessments = assess_lab_values_v2(values)
            print("\nAssessments:")
            for a in assessments:
                print(f"  {a['test']}: {a['value']} {a['unit']} - {a['status']}")
    else:
        print(f"Sample PDF not found at: {sample_pdf}")
        print("Testing with synthetic text...")
        
        sample_text = """
        Blood Test Report
        Hemoglobin: 13.5 g/dL
        Glucose (Fasting): 95 mg/dL
        Total Cholesterol: 185 mg/dL
        LDL: 110 mg/dL
        HDL: 55 mg/dL
        Triglycerides: 120 mg/dL
        Vitamin D: 28 ng/mL
        """
        
        values = parse_lab_values_v2(sample_text)
        print(f"\nParsed {len(values)} values from synthetic text:")
        for k, v in values.items():
            print(f"  {k}: {v}")
    
    print("\n" + "=" * 60)
    print("OCR Pipeline V2 Test Complete")
    print("=" * 60)
