# 🏗️ Complete System Architecture — Personalized Nutrition System V2

## Full Explanation of Every Module with Code, Inputs, Outputs & Theory

---

## Table of Contents

1. [Project Overview & Theory](#1-project-overview--theory)
2. [Technology Stack](#2-technology-stack)
3. [System Architecture Diagram](#3-system-architecture-diagram)
4. [Complete System Workflow](#4-complete-system-workflow)
5. [Module 1: app.py — Flask Application Controller](#module-1-apppy)
6. [Module 2: ocr_fix_v2.py — OCR & Text Extraction](#module-2-ocr_fix_v2py)
7. [Module 3: data_preprocessing_v2.py — Data Cleaning & Merging](#module-3-data_preprocessing_v2py)
8. [Module 4: model_training_health_v2.py — Health Model Training](#module-4-model_training_health_v2py)
9. [Module 5: model_training_diet_v2.py — Diet Model Training](#module-5-model_training_diet_v2py)
10. [Module 6: model_inference_health_v2.py — Health Prediction](#module-6-model_inference_health_v2py)
11. [Module 7: model_inference_diet_v2.py — Diet Recommendation](#module-7-model_inference_diet_v2py)
12. [Module 8: diet_plan_generator_v2.py — 7-Day Meal Plan](#module-8-diet_plan_generator_v2py)
13. [Module 9: chart_generator_v2.py — Visual Chart Creation](#module-9-chart_generator_v2py)
14. [Module 10: pdf_generator_v2.py — PDF Report Builder](#module-10-pdf_generator_v2py)
15. [Module 11: expert_advice_v2.py — AI Chatbot (Groq)](#module-11-expert_advice_v2py)
16. [Module 12: mongo_helper.py — Database Layer](#module-12-mongo_helperpy)
17. [Module 13: otp_service.py — OTP & Email Service](#module-13-otp_servicepy)
18. [Frontend Templates Overview](#frontend-templates-overview)
19. [Datasets Used](#datasets-used)
20. [ML Model Comparisons](#ml-model-comparisons)

---

## 1. Project Overview & Theory

### What This Project Does (In Simple Words)

This is a **Full-Stack AI-Powered Healthcare Web Application** that reads your blood report (PDF or Image), extracts medical values using **OCR (Optical Character Recognition)**, feeds them into **Machine Learning models**, and generates a **personalized diet plan** with a **downloadable PDF report**.

### The Problem It Solves

Most diet apps give **generic advice** like "eat less carbs." They don't know YOUR body. This system reads YOUR actual blood report, checks if your hemoglobin is low (anemia risk), if your glucose is high (diabetes risk), or if your cholesterol is elevated (heart risk). Based on YOUR real data, it creates a custom plan.

### Theoretical Concepts Used

| Concept | Where Used | Why |
|---------|-----------|-----|
| **OCR (Optical Character Recognition)** | `ocr_fix_v2.py` | Converts image pixels into machine-readable text |
| **Regex (Regular Expressions)** | `ocr_fix_v2.py` | Pattern matching to find "Hemoglobin: 14.2" in raw text |
| **Random Forest Classifier** | Health & Diet Models | Ensemble of decision trees for robust classification |
| **StandardScaler** | Health Model | Normalizes features to zero mean, unit variance |
| **Label Encoding** | Diet Model | Converts food names like "Oatmeal" into numbers (0, 1, 2...) |
| **Flask (MVC Pattern)** | `app.py` | Model-View-Controller web architecture |
| **Jinja2 Templating** | HTML templates | Server-side HTML rendering with dynamic data |
| **MongoDB (NoSQL)** | `mongo_helper.py` | Document-based storage for flexible health records |
| **ReportLab** | `pdf_generator_v2.py` | Programmatic PDF creation with tables and charts |
| **Matplotlib** | `chart_generator_v2.py` | Scientific-grade chart generation as Base64 images |
| **Groq LLM API** | `expert_advice_v2.py` | Large Language Model for intelligent chatbot responses |

---

## 2. Technology Stack

```
Backend:    Python 3.8+, Flask (Micro Web Framework)
Frontend:   HTML5, CSS3, JavaScript, Jinja2 Templates
ML:         Scikit-Learn, XGBoost, Pandas, NumPy
OCR:        Tesseract 5.x, pytesseract, pdf2image, pypdfium2
Visuals:    Matplotlib (Charts), ReportLab (PDF)
Database:   MongoDB (via PyMongo)
AI Chat:    Groq API (LLaMA 3.3-70B)
Email:      EmailJS REST API
```

---

## 3. System Architecture Diagram

```
┌───────────────────────────────────────────────────────────────┐
│                        USER DEVICE                            │
│                    (Browser: Chrome/Edge)                      │
└──────────────────────────┬────────────────────────────────────┘
                           │ HTTP Request (Form Data + File)
                           ▼
┌───────────────────────────────────────────────────────────────┐
│                    FLASK WEB SERVER (app.py)                   │
│                    Port 5002 | Debug Mode                     │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐      │
│  │   Routes    │  │  Sessions   │  │  Template Engine │      │
│  │ /register   │  │ (Cookies)   │  │   (Jinja2)       │      │
│  │ /login      │  │             │  │                  │      │
│  │ /upload     │  │             │  │                  │      │
│  │ /report/<id>│  │             │  │                  │      │
│  │ /chatbot    │  │             │  │                  │      │
│  └──────┬──────┘  └─────────────┘  └──────────────────┘      │
│         │                                                     │
│         ▼  process_report_pipeline()                          │
│  ┌──────────────────────────────────────────────────────┐     │
│  │              CORE PROCESSING PIPELINE                 │     │
│  │                                                       │     │
│  │  Step 1: OCR Extraction     (ocr_fix_v2.py)          │     │
│  │  Step 2: Biomarker Parsing  (ocr_fix_v2.py)          │     │
│  │  Step 3: Normalization      (ocr_fix_v2.py)          │     │
│  │  Step 4: Health Prediction  (model_inference_health)  │     │
│  │  Step 5: Lab Assessment     (ocr_fix_v2.py)          │     │
│  │  Step 6: Diet Plan          (diet_plan_generator)     │     │
│  │  Step 7: Charts             (chart_generator_v2.py)   │     │
│  │  Step 8: PDF                (pdf_generator_v2.py)     │     │
│  └──────────────────────────────────────────────────────┘     │
└──────────────────────────┬────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
     ┌──────────────┐ ┌─────────┐ ┌──────────────┐
     │   MongoDB    │ │ .pkl    │ │  Groq API    │
     │ (User Data,  │ │ Models  │ │ (AI Chatbot) │
     │  Reports)    │ │ (2 files│ │              │
     └──────────────┘ └─────────┘ └──────────────┘
```

---

## 4. Complete System Workflow

```
START → User visits http://localhost:5002
  │
  ├─→ REGISTER (/register POST)
  │     Input: name, email, age, gender, height, weight, blood_report.pdf
  │     │
  │     ├─→ Save file to /uploads/
  │     ├─→ process_report_pipeline() ← THE CORE FUNCTION
  │     │     │
  │     │     ├─→ OCR: PDF → Image → Text → Regex → {hemoglobin: 14.2, glucose: 95}
  │     │     ├─→ Normalize keys: "fasting_glucose" → "glucose"
  │     │     ├─→ Health Model: input_vector → Random Forest → "Normal"
  │     │     ├─→ Rule-Based Override: cross-check ML with hard rules
  │     │     ├─→ Assessment: compare each value to reference range
  │     │     ├─→ Diet Plan: ML + South Indian food database → 7-day plan
  │     │     └─→ Macros: goal-based split (Carbs/Protein/Fat %)
  │     │
  │     ├─→ Save user to MongoDB (users collection)
  │     ├─→ Save report to MongoDB (reports collection)
  │     └─→ Redirect to /report/<id>
  │
  ├─→ VIEW REPORT (/report/<id>)
  │     │
  │     ├─→ Fetch report from MongoDB
  │     ├─→ Generate charts on-the-fly (Base64 images in RAM)
  │     └─→ Render report.html with all data
  │
  ├─→ DOWNLOAD PDF (/download_pdf)
  │     │
  │     ├─→ Read report from session
  │     ├─→ Re-generate charts
  │     ├─→ Build PDF using ReportLab
  │     └─→ Return PDF as file download
  │
  ├─→ CHATBOT (/chatbot POST)
  │     │
  │     ├─→ Build context from session (user profile + latest lab values)
  │     ├─→ Send to Groq API (LLaMA 3.3-70B)
  │     └─→ Return JSON reply
  │
  └─→ PASSWORD RESET (/forgot → /verify_otp → /reset_password)
        │
        ├─→ Generate 6-digit OTP
        ├─→ Save to MongoDB (otp_verifications)
        ├─→ Send via EmailJS API
        └─→ Verify & update password
```

---

## Module 1: `app.py`

### Purpose
The **central controller** of the entire application. It is the "brain" that connects every other module. Every HTTP request from the user's browser first arrives here.

### Theoretical Context
This file follows the **MVC (Model-View-Controller)** design pattern:
- **Model**: `mongo_helper.py` (data storage)
- **View**: HTML templates in `/templates/`
- **Controller**: `app.py` (this file — business logic)

### Key Imports (Lines 13–33)
```python
import os                          # File path operations
import sys                         # System path modification for imports
import logging                     # Debug/error logging
from datetime import datetime      # Timestamps for reports
from flask import Flask, render_template, request, jsonify, session, send_file, redirect, url_for
#   Flask:           The web framework class
#   render_template: Renders HTML files with dynamic data
#   request:         Accesses form data and uploaded files
#   jsonify:         Converts Python dicts to JSON for AJAX
#   session:         Server-side cookie storage per user
#   send_file:       Sends binary files (PDFs) to browser
#   redirect:        HTTP redirect to another URL
#   url_for:         Generates URL from function name

from werkzeug.utils import secure_filename  # Sanitizes filenames to prevent attacks
import numpy as np                          # Numerical operations
import io                                   # In-memory file streams

# V2 Module imports
from version2.ocr_fix_v2 import extract_blood_report_text_v2, parse_lab_values_v2, ...
from version2.model_inference_health_v2 import predict_health_status, ...
from version2.model_inference_diet_v2 import predict_diet_metrics, ...
from version2.diet_plan_generator_v2 import generate_v2_diet_plan
from version2.expert_advice_v2 import get_expert_response
from version2.pdf_generator_v2 import generate_pdf_v2
from version2.chart_generator_v2 import generate_macronutrient_chart, ...
from version2 import mongo_helper as db
```

### App Configuration (Lines 35–44)
```python
app = Flask(__name__, template_folder='../templates', static_folder='../static')
# Creates Flask app. Points templates and static files to parent directory
# because app.py lives in /version2/ but templates are in /templates/

app.config['UPLOAD_FOLDER'] = 'uploads'     # Where blood reports are saved
app.config['SECRET_KEY'] = 'supersecretkey_v2'  # Required for session encryption

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Create uploads/ if missing

logging.basicConfig(level=logging.INFO)  # Enable info-level logging
logger = logging.getLogger(__name__)     # Logger for this module
```

### The Core Pipeline Function: `process_report_pipeline()` (Lines 51–214)

This is the **most important function** in the entire project. It orchestrates the full analysis.

**Input:**
| Parameter | Type | Example |
|-----------|------|---------|
| `filepath` | `str` | `"uploads/blood_report.pdf"` |
| `user_profile` | `dict` | `{'name': 'John', 'age': 25, 'gender': 1, 'height': 175, 'weight': 70, 'bmi': 22.9}` |
| `manual_overrides` | `dict` (optional) | `{'hemoglobin': 14.5}` |

**Output:**
| Key | Type | Description |
|-----|------|-------------|
| `user_profile` | `dict` | Original user data |
| `lab_results` | `dict` | `{'hemoglobin': 14.2, 'glucose': 95, ...}` |
| `health_status` | `str` | `"Normal"`, `"At Risk"`, or `"Action Needed"` |
| `diet_plan` | `dict` | 7-day meal plan with Monday–Sunday |
| `deficiencies` | `list` | `['hemoglobin', 'glucose']` — items outside normal range |
| `macros` | `dict` | `{'carbs': 50, 'protein': 30, 'fat': 20}` |
| `assessment` | `list` | Detailed per-biomarker analysis |
| `recommendation_table_data` | `list` | Food recommendations per nutrient |

**Step-by-Step Code Walkthrough:**

```python
def process_report_pipeline(filepath, user_profile, manual_overrides=None):
    # STEP 1: OCR — Convert PDF/Image to text, then extract biomarker values
    extracted_text = extract_blood_report_text_v2(filepath)
    #   Input:  "uploads/blood_report.pdf"
    #   Output: "Hemoglobin: 14.2 g/dL\nGlucose: 95 mg/dL\n..."

    lab_values = parse_lab_values_v2(extracted_text)
    #   Input:  Raw text string
    #   Output: {'hemoglobin': 14.2, 'glucose': 95.0, 'total_cholesterol': 185.0}

    # STEP 2: Protect critical OCR values from manual override
    protected_keys = ['hemoglobin', 'glucose', 'total_cholesterol']
    # Theory: These 3 biomarkers are the most clinically important.
    # If OCR extracted them, we trust OCR over manual input.

    # STEP 3: Normalize biomarker keys
    lab_values = normalize_biomarkers(lab_values)
    #   "fasting_glucose" → "glucose", "hgb" → "hemoglobin"

    # STEP 4: Build full profile for ML model
    full_profile = user_profile.copy()
    full_profile.update(lab_values)
    #   Merges: {'age': 25, 'gender': 1, 'hemoglobin': 14.2, 'glucose': 95}

    # STEP 5: Health Prediction (ML)
    health_result = predict_health_status(full_profile)
    #   Input:  Full profile dict
    #   Output: {'status_label': 'Normal', 'confidence': 0.95, 'class_probabilities': {...}}

    # STEP 6: Rule-Based Safety Override
    rule_status = health_result.get('rule_based_status')
    if rule_status and rule_status != health_status:
        health_status = rule_status
    # Theory: ML models can be biased by training data.
    # A hardcoded rule "glucose > 200 = Action Needed" catches cases ML might miss.

    # STEP 7: Clinical Assessment
    assessment = assess_lab_values_v2(lab_values, user_profile['age'], gender_str)
    #   Compares each value against reference ranges
    #   Output: [{'test': 'Hemoglobin', 'value': 14.2, 'status': 'NORMAL', ...}]

    deficiencies = [item['test'] for item in assessment if item['status'] != 'NORMAL']
    #   Output: ['Glucose'] — list of biomarkers outside normal range

    # STEP 8: Generate 7-Day Diet Plan
    diet_plan = generate_v2_diet_plan(user_profile)
    #   Output: {'Monday': {'Breakfast': 'Idli with Sambar', ...}, ...}

    # STEP 9: Calculate Macronutrient Split (Dynamic)
    goal = user_profile.get('goal', 'Maintenance').lower()
    c, p, f = 50, 30, 20  # Default: Carbs 50%, Protein 30%, Fat 20%
    if 'loss' in goal:         c, p, f = 40, 40, 20   # Weight loss → more protein
    elif 'muscle' in goal:     c, p, f = 45, 35, 20   # Muscle gain → more protein
    if 'glucose' in deficiencies:  c, p, f = 35, 35, 30  # Diabetes risk → less carbs
    macros = {'carbs': c, 'protein': p, 'fat': f}
```

### Route: `/register` (Lines 315–366)

**Input (HTML Form → POST):**
| Field | Type | Example |
|-------|------|---------|
| `name` | `str` | `"Murali"` |
| `email` | `str` | `"murali@gmail.com"` |
| `age` | `int` | `25` |
| `gender` | `str` | `"male"` |
| `height` | `float` | `175.0` (cm) |
| `weight` | `float` | `70.0` (kg) |
| `report` | `File` | `blood_report.pdf` |

**Output:** Redirects to `/report/<report_id>` displaying the full analysis.

**What happens internally:**
1. Collect form data → build `user_data` dict
2. Save uploaded PDF → `uploads/blood_report.pdf`
3. Calculate BMI: `weight / (height_m ** 2)` → e.g., `22.86`
4. Call `process_report_pipeline()` → get all analysis results
5. Save user to MongoDB → `db.save_user(user_data)`
6. Save report to MongoDB → `db.save_report(email, report_data)`
7. Store user in session → `session['user'] = saved_user`
8. Redirect to report page

### Route: `/report/<report_id>` (Lines 410–451)

**Input:** `report_id` string from URL (MongoDB ObjectId)

**Output:** Renders `report.html` with:
| Variable | Description |
|----------|-------------|
| `lab_data` | Dict of biomarker name → value |
| `prediction` | Calorie count (2000 default) |
| `health_status` | "Normal" / "At Risk" / "Action Needed" |
| `deficiencies` | List of abnormal biomarkers |
| `diet_plan` | Plan object with primary diet info |
| `assessment` | Per-biomarker analysis |
| `macros` | Carbs/Protein/Fat percentages |
| `diet_charts` | Dict of Base64-encoded chart images |
| `report` | List of summary strings |
| `recommendations` | List of food recommendations |

### Route: `/chatbot` (Lines 605–699)

**Input (AJAX POST):** `{"message": "What should I eat for breakfast?"}`

**Process:**
1. Read user profile from session
2. Fetch latest report from MongoDB
3. Build context block with lab values, health status, deficiencies, macros
4. Prepend context to user's question
5. Send to Groq API (LLaMA 3.3-70B)
6. Return JSON: `{"reply": "Based on your profile, try oatmeal with berries..."}`

**Output:** `{"reply": "AI-generated personalized response"}`

---

## Module 2: `ocr_fix_v2.py`

### Purpose
The **"eyes"** of the system. Converts unstructured documents (PDF/Image) into structured data `{biomarker: value}`.

### Theoretical Context
**OCR** = Optical Character Recognition. Tesseract (by Google) is the industry-standard open-source OCR engine. It works by:
1. Identifying character patterns in image pixels
2. Using neural networks (LSTM) to recognize text
3. Outputting raw text strings

**Regex** = Regular Expressions. Pattern-matching language used to find specific text patterns like "Hemoglobin: 14.2 g/dL" in noisy OCR output.

### Validation Ranges (Lines 62–70)
```python
VALIDATION_RANGES = {
    'hemoglobin': {'min': 5.0, 'max': 25.0, 'unit': 'g/dL'},
    'glucose': {'min': 20, 'max': 1000, 'unit': 'mg/dL'},
    ...
}
# Purpose: OCR sometimes misreads "14.2" as "142". These broad ranges
# catch values that are clearly wrong (e.g., hemoglobin = 142 is impossible).
```

### Reference Ranges (Lines 73–122)
```python
REFERENCE_RANGES = {
    'hemoglobin': {'min': 13.5, 'max': 17.5, 'unit': 'g/dL'},
    'glucose': {'min': 70, 'max': 100, 'unit': 'mg/dL'},
    ...
}
# Purpose: The "healthy" range. Used for clinical assessment.
# If value falls outside this range, it's flagged as HIGH or LOW.
```

### Biomarker Regex Patterns (Lines 127–303)
```python
BIOMARKER_PATTERNS = {
    'hemoglobin': [
        r'h[ae]moglobin\s*[:=]?\s*(\d+\.?\d*)\s*(g/?dl|gm/?dl)?',
        #   h[ae]moglobin  → matches "hemoglobin" or "haemoglobin" (British spelling)
        #   \s*            → any amount of whitespace
        #   [:=]?          → optional colon or equals sign
        #   (\d+\.?\d*)    → CAPTURE GROUP: one or more digits, optional decimal
        #   (g/?dl)?       → optional unit "g/dL" or "gdl"
        r'hgb?\s*[:=]?\s*(\d+\.?\d*)',   # Abbreviation: "HGB" or "HG"
        r'hb\s*[:=]?\s*(\d+\.?\d*)',     # Short form: "Hb"
    ],
    'glucose': [
        r'(fasting\s*)?glucose\s*[:=]?\s*(\d+\.?\d*)',
        # Matches: "Fasting Glucose: 95" or just "Glucose: 95"
        r'blood\s*sugar\s*[:=]?\s*(\d+\.?\d*)',
        r'fbs\s*[:=]?\s*(\d+\.?\d*)',    # FBS = Fasting Blood Sugar
    ],
    # ... 30+ biomarkers with multiple patterns each
}
```

### Key Function: `extract_blood_report_text_v2()` (Lines 507–523)

**Input:** `file_path` = `"uploads/report.pdf"`
**Output:** Raw text string from the document

```python
def extract_blood_report_text_v2(file_path):
    _, ext = os.path.splitext(file_path.lower())  # Get file extension

    if ext == '.pdf':
        return extract_text_from_pdf_v2(file_path)   # PDF path
    elif ext in ['.png', '.jpg', '.jpeg', '.tiff']:
        return extract_text_from_image_v2(file_path)  # Image path
```

### PDF Extraction with 3 Fallbacks (Lines 439–504)

```python
def extract_text_from_pdf_v2(pdf_path):
    # METHOD 1: pdfplumber (fastest, direct text extraction)
    # Works when PDF has embedded text (digital PDF)
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()

    # METHOD 2: pdf2image + Tesseract OCR (requires Poppler)
    # Works when PDF is scanned (image-based)
    images = convert_from_path(pdf_path, dpi=300)  # High DPI for accuracy
    for img in images:
        processed = preprocess_image(img)  # Grayscale conversion
        text += pytesseract.image_to_string(processed_pil, config='--oem 3 --psm 3')

    # METHOD 3: pypdfium2 + Tesseract (pure Python fallback)
    # No external dependencies like Poppler needed
    images = convert_pdf_to_images_pypdfium(pdf_path)
```

### Key Function: `parse_lab_values_v2()` (Lines 543–575)

**Input:** `"Hemoglobin: 14.2 g/dL\nGlucose (Fasting): 95 mg/dL\n..."`
**Output:** `{'hemoglobin': 14.2, 'glucose': 95.0, 'total_cholesterol': 185.0}`

```python
def parse_lab_values_v2(extracted_text):
    lab_values = {}
    text_lower = extracted_text.lower()

    for biomarker, patterns in BIOMARKER_PATTERNS.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                groups = match.groups()
                # Find the numeric group among captured groups
                for g in groups:
                    if g and re.match(r'^\d+\.?\d*$', str(g)):
                        value = float(g)
                        break

                if validate_value(biomarker, value):  # Check broad range
                    lab_values[biomarker] = value
                    break  # Stop after first valid match
```

### Key Function: `assess_lab_values_v2()` (Lines 577–628)

**Input:** `lab_values = {'hemoglobin': 11.0, 'glucose': 95}`, `age = 25`, `gender = 'Male'`
**Output:**
```python
[
    {'test': 'Hemoglobin', 'value': 11.0, 'status': 'LOW', 'severity': 'concern',
     'deviation_pct': -18.5, 'deviation_label': 'Mild', 'normal_range': '13.5-17.5'},
    {'test': 'Glucose', 'value': 95.0, 'status': 'NORMAL', 'severity': 'ok',
     'deviation_pct': 0.0, 'deviation_label': 'Normal', 'normal_range': '70-100'}
]
```

### Key Function: `normalize_biomarkers()` (Lines 305–346)

**Input:** `{'fasting_glucose': 95, 'hgb': 14.2}`
**Output:** `{'glucose': 95, 'hemoglobin': 14.2}`

Maps variant names to standard internal keys for consistency across all modules.

---

## Module 3: `data_preprocessing_v2.py`

### Purpose
Merges two real-world datasets into a single clean training dataset.

### Input Datasets
| Dataset | Rows | Purpose |
|---------|------|---------|
| `lab_clean_processed.csv` | ~2000 | Medical lab values (HGP, SGP, etc.) |
| `nhanes_real_with_calories.csv` | ~7000+ | NHANES nutrition survey data |

### Output
| File | Description |
|------|-------------|
| `processed_data_v2.csv` | Merged, cleaned dataset with health labels |

### Code Walkthrough

```python
# Column code mapping: Lab dataset uses codes, we need readable names
LAB_CODE_MAP = {
    'HGP': 'hemoglobin',     # H = Hemo, G = Globin, P = Parameter
    'SGP': 'glucose',         # S = Sugar, G = Glucose
    'TCP': 'total_cholesterol',
    ...
}

def load_and_merge_data():
    lab_df = pd.read_csv(LAB_DATA_PATH)        # Load lab data
    nhanes_df = pd.read_csv(NHANES_DATA_PATH)  # Load NHANES data

    lab_df_renamed = lab_df.rename(columns=LAB_CODE_MAP)  # Rename columns
    # Combine both datasets row-wise
    combined_df = pd.concat([nhanes_subset, lab_subset], axis=0, ignore_index=True)

def preprocess_and_label(df):
    # Impute missing values with median (not mean — robust to outliers)
    imputer = SimpleImputer(strategy='median')

    # Calculate BMI: weight(kg) / height(m)²
    df['bmi'] = df['weight'] / (df['height_m'] ** 2)

    # Generate health labels using clinical rules
    def get_health_status(row):
        score = 0
        if row['glucose'] > 125: score += 2       # Diabetes risk
        if row['hemoglobin'] < 12: score += 2      # Anemia risk
        if row['total_cholesterol'] > 240: score += 2  # Heart risk

        if score == 0: return 0     # Normal
        elif score <= 2: return 1   # At Risk
        else: return 2              # Action Needed
```

---

## Module 4: `model_training_health_v2.py`

### Purpose
Trains the health classification model. Compares 4 algorithms and saves the best.

### Input
| File | Description |
|------|-------------|
| `processed_data_v2.csv` | Cleaned dataset with `health_status` column |

### Output
| File | Description |
|------|-------------|
| `health_model_v2.pkl` | Serialized pipeline: `{scaler, model, feature_names}` |

### Code Walkthrough

```python
def train_and_evaluate():
    df = pd.read_csv(DATA_PATH)

    X = df.drop(columns=['health_status', 'calories'])  # Features
    y = df['health_status']  # Target: 0, 1, or 2

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    scaler = StandardScaler()  # Normalize: mean=0, std=1
    X_train_scaled = scaler.fit_transform(X_train)

    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000),
        'Random Forest': RandomForestClassifier(n_estimators=100),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100),
        'XGBoost': XGBClassifier(eval_metric='mlogloss')
    }

    # Train all 4, compare accuracy, save the best
    for name, model in models.items():
        model.fit(X_train_scaled, y_train)
        acc = accuracy_score(y_test, model.predict(X_test_scaled))

    # Save: {scaler + model + feature_names + model_name}
    joblib.dump(final_pipeline, MODEL_PATH)
```

### Model Comparison Results

| Algorithm | Accuracy | F1-Score |
|-----------|----------|----------|
| Logistic Regression | 74.7% | 0.74 |
| **Random Forest** | **99.9%** | **0.99** |
| Gradient Boosting | 99.7% | 0.99 |
| XGBoost | 99.8% | 0.99 |

**Winner: Random Forest** — Best balance of accuracy and interpretability.

---

## Module 5: `model_training_diet_v2.py`

### Purpose
Trains a food recommendation model. If no external dataset exists, generates synthetic data.

### Input
| Source | Description |
|--------|-------------|
| `diet_dataset.csv` (if exists) | Pre-existing diet data |
| `COMMON_FOODS` dict (fallback) | 37 food items across Veg/Vegan/Non-Veg |

### Output
| File | Description |
|------|-------------|
| `diet_model_v2.pkl` | `{model, label_encoder, diet_map, goal_map}` |

### Synthetic Data Generation Logic

```python
COMMON_FOODS = {
    'Vegetarian': [
        ('Spinach Salad', 150, 10, 5, 2, 'Weight Loss'),
        # (name, calories, carbs, protein, fat, goal_alignment)
    ],
    'Vegan': [...],
    'Non-Vegetarian': [...]
}

# Generates 2000 samples:
# For each sample: random age, gender, BMI, diet_type, goal
# Then selects appropriate food based on rules
```

### Feature Encoding

```python
diet_map = {'Vegetarian': 0, 'Vegan': 1, 'Non-Vegetarian': 2}
goal_map = {'Weight Loss': 0, 'Maintenance': 1, 'Muscle Gain': 2}

# Input features: [age, gender, bmi, diet_encoded, goal_encoded]
# Target: food name (encoded via LabelEncoder)
```

---

## Module 6: `model_inference_health_v2.py`

### Purpose
Loads the trained health model and predicts status for a new user.

### Input
```python
input_data = {
    'age': 35, 'gender': 1, 'hemoglobin': 14.5,
    'glucose': 95, 'total_cholesterol': 180, ...
}
```

### Output
```python
{
    'status_code': 0,              # 0=Normal, 1=At Risk, 2=Action Needed
    'status_label': 'Normal',
    'confidence': 0.95,            # 95% model confidence
    'class_probabilities': {'Normal': 0.95, 'At Risk': 0.03, 'Action Needed': 0.02},
    'rule_based_status': 'Normal'  # Safety override from hardcoded rules
}
```

### Lazy Loading Pattern

```python
_MODEL_PIPELINE = None  # Global singleton

def load_model():
    global _MODEL_PIPELINE
    if _MODEL_PIPELINE is None:
        _MODEL_PIPELINE = joblib.load(MODEL_PATH)
    return _MODEL_PIPELINE
# Theory: Loading a 15MB .pkl file takes ~2 seconds.
# Lazy loading means we only load ONCE, not on every request.
```

---

## Module 7: `model_inference_diet_v2.py`

### Purpose
Predicts top 3 food recommendations for a user profile.

### Input
```python
user_profile = {'age': 30, 'gender': 1, 'bmi': 24.5, 'diet_type': 'Non-Vegetarian', 'goal': 'Muscle Gain'}
```

### Output
```python
{
    'recommendations': ['Chicken Tikka', 'Quinoa Bowl', 'Protein Shake'],
    'confidence': 0.85,
    'top_probabilities': {'Chicken Tikka': 0.35, 'Quinoa Bowl': 0.28, 'Protein Shake': 0.22}
}
```

---

## Module 8: `diet_plan_generator_v2.py`

### Purpose
Generates a full 7-day meal plan mixing ML recommendations with a South Indian food database.

### Input
```python
user_data = {'age': 25, 'gender': 1, 'bmi': 22.0, 'diet_type': 'Vegetarian', 'goal': 'Health'}
```

### Output
```python
{
    'Monday': {'Breakfast': 'Idli with Sambar & Chutney', 'Lunch': 'Sambar Rice with Beetroot Poriyal',
               'Snacks': 'Sprouts Salad', 'Dinner': 'Appam with Vegetable Stew'},
    'Tuesday': {...},
    ...
    'Sunday': {...},
    'primary': {'name': 'South Indian Fusion Plan', 'macros': {'carbs': 55, 'protein': 25, 'fat': 20}},
    'reasoning': ['Incorporates traditional South Indian nutrient-rich foods.', ...]
}
```

### Food Database (Hardcoded)

```python
SOUTH_INDIAN_OPTIONS = {
    'Breakfast': ['Idli with Sambar & Chutney', 'Dosa with Coconut Chutney', 'Vegetable Upma', ...],
    'Lunch': ['Sambar Rice with Beetroot Poriyal', 'Curd Rice with Pomegranate', ...],
    'Snacks': ['Masala Buttermilk', 'Sprouts Salad', 'Roasted Makhana', ...],
    'Dinner': ['Appam with Vegetable Stew', 'Chapati with Dal Tadka', ...]
}
```

---

## Module 9: `chart_generator_v2.py`

### Purpose
Generates 3 types of charts as **Base64 images** (in RAM — never saved to disk).

### Chart 1: `generate_macronutrient_chart(macros)`
**Input:** `{'carbs': 50, 'protein': 30, 'fat': 20}`
**Output:** Base64 PNG string of a pie chart → `"data:image/png;base64,iVBOR..."`

### Chart 2: `generate_diet_chart_image(diet_plan)`
**Input:** 7-day diet plan dict
**Output:** Base64 PNG of a table showing all meals

### Chart 3: `generate_health_status_chart(lab_values, health_status)`
**Input:** `{'hemoglobin': 14.2, 'glucose': 95}`, `"Normal"`
**Output:** Base64 PNG horizontal bar chart with color zones (green=normal, red=abnormal)

Uses **Unified Scaling**: Normal range always maps to positions 25–75 on X-axis, regardless of actual units.

---

## Module 10: `pdf_generator_v2.py`

### Purpose
Creates a downloadable, multi-page PDF report using **ReportLab**.

### Input
```python
generate_pdf_v2(user_data, lab_results, health_status, diet_plan, deficiencies, diet_charts, recommendation_table_data)
```

### Output
`io.BytesIO` buffer containing the PDF binary data.

### PDF Structure
| Page | Content |
|------|---------|
| Page 1 | Title, User Info Table, Health Status, Deficiencies List, Macronutrient Chart, Food Recommendation Table |
| Page 2 | 7-Day Diet Plan Table with Day/Breakfast/Lunch/Snacks/Dinner columns |

---

## Module 11: `expert_advice_v2.py`

### Purpose
AI-powered chatbot using **Groq API** (LLaMA 3.3-70B model). Falls back to rule-based responses if API fails.

### How It Works

1. User types a question in the floating chatbot widget
2. JavaScript sends AJAX POST to `/chatbot`
3. `app.py` builds context (user profile, lab values, health status)
4. Context + question sent to `get_expert_response()`
5. Function calls Groq API with system prompt + user message
6. Returns AI-generated, personalized reply

### Fallback System

If Groq API is unavailable:
```python
FALLBACK_RESPONSES = {
    'nutrition': ["A balanced diet with carbs, proteins, and fats is key...", ...],
    'fitness': ["Consistency beats intensity...", ...],
    'weight_loss': ["Focus on whole foods...", ...],
    'general': ["That's a great question!...", ...]
}
# Keyword detection: "food", "eat", "diet" → nutrition category
```

---

## Module 12: `mongo_helper.py`

### Purpose
Database abstraction layer. All MongoDB operations go through this file.

### Collections

| Collection | Purpose |
|------------|---------|
| `users` | User profiles (name, email, age, gender, height, weight) |
| `reports` | Analysis reports (lab_results, health_status, diet_plan) |
| `otp_verifications` | Temporary OTP records with 5-minute expiry |

### Key Functions

| Function | Input | Output |
|----------|-------|--------|
| `save_user(user_data)` | User dict | Saved user with `_id` |
| `get_user_by_email(email)` | Email string | User dict or None |
| `save_report(email, report_data)` | Email + report dict | Report ID string |
| `get_reports_for_user(email)` | Email string | List of report dicts |
| `get_report_by_id(report_id)` | Report ID | Report dict |
| `delete_report(report_id)` | Report ID | Boolean |
| `save_otp(email, otp)` | Email + OTP string | Boolean |
| `verify_and_delete_otp(email, otp)` | Email + OTP | (Boolean, message) |
| `update_password(email, hash)` | Email + hash | Boolean |

---

## Module 13: `otp_service.py`

### Purpose
Generates OTP codes and sends them via **EmailJS API** for password reset.

### Flow
```
User clicks "Forgot Password"
  → /forgot (POST email)
    → generate_otp() returns "483927"
    → db.save_otp(email, "483927") saves to MongoDB with 5-min expiry
    → send_otp_email(email, "483927") calls EmailJS REST API
  → /verify_otp (POST otp)
    → db.verify_and_delete_otp(email, otp) checks and removes
  → /reset_password (POST new_password)
    → db.update_password(email, hashed_password)
```

---

## Frontend Templates Overview

| Template | Route | Purpose |
|----------|-------|---------|
| `base.html` | All pages | Master layout with header, nav, footer, chatbot widget |
| `index.html` | `/` | Landing page with hero section |
| `register.html` | `/register` | Registration form + file upload |
| `login.html` | `/login` | Email login form |
| `report.html` | `/report/<id>` | Full analysis results display |
| `profile.html` | `/profile` | User dashboard with report history |
| `upload.html` | `/upload` | Standalone upload form |
| `diet_plans.html` | `/diet_plan` | Diet plan categories |
| `expert.html` | `/expert` | Ask an Expert page |
| `forgot.html` | `/forgot` | Forgot password form |
| `verify_otp.html` | `/verify_otp` | OTP input form |
| `reset_password.html` | `/reset_password` | New password form |
| `profile_edit.html` | `/profile/edit` | Edit profile form |
| `blood_report_result.html` | — | Blood report results display |

---

## Datasets Used

| Dataset | File | Rows | Columns | Source |
|---------|------|------|---------|--------|
| Medical Lab Data | `lab_clean_processed.csv` | ~2000 | 8 | Public medical lab records |
| NHANES Nutrition | `nhanes_real_with_calories.csv` | ~7000+ | Multiple | US National Health Survey |
| Diet Training | `diet_dataset.csv` | 2000 | 10 | Synthetically generated |
| Processed Merged | `processed_data_v2.csv` | ~9000+ | 20+ | Output of preprocessing |

---

## ML Model Comparisons

### Health Classification (3-class: Normal / At Risk / Action Needed)

| Model | Accuracy | F1-Score | Selected? |
|-------|----------|----------|-----------|
| Logistic Regression | 74.7% | 0.74 | ❌ |
| **Random Forest** | **99.9%** | **0.99** | **✅** |
| Gradient Boosting | 99.7% | 0.99 | ❌ |
| XGBoost | 99.8% | 0.99 | ❌ |

### Diet Recommendation (Multi-class: 37 food items)

| Model | Accuracy | Selected? |
|-------|----------|-----------|
| KNN | 88.0% | ❌ |
| **Random Forest** | **95.0%** | **✅** |
| XGBoost | 93.2% | ❌ |

---

*Document generated on 2026-02-19. This covers every module in the Personalized Nutrition System V2.*
