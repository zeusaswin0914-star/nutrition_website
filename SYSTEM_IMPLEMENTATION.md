# 📘 System Implementation & Architecture Guide

## Personalized Nutrition System — Complete Technical Documentation

**Version:** 2.0  
**Last Updated:** February 18, 2026  
**Tech Stack:** Python · Flask · MongoDB · Scikit-Learn · Groq AI · HTML/CSS/JS

---

## 📑 Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Installation & Setup](#3-installation--setup)
4. [Folder Structure](#4-folder-structure)
5. [Module Reference](#5-module-reference)
6. [System Workflow](#6-system-workflow)
7. [Database Schema](#7-database-schema)
8. [API Endpoints](#8-api-endpoints)
9. [Frontend Templates](#9-frontend-templates)
10. [AI Chatbot Integration](#10-ai-chatbot-integration)
11. [PDF Report Generation](#11-pdf-report-generation)
12. [Password Reset Flow (EmailJS)](#12-password-reset-flow-emailjs)
13. [Execution Commands](#13-execution-commands)
14. [Error Handling & Logging](#14-error-handling--logging)
15. [Environment & Dependencies](#15-environment--dependencies)

---

## 1. Project Overview

The **Personalized Nutrition System** is a full-stack web application that analyzes uploaded blood reports using OCR and Machine Learning to provide:

- **Health Status Prediction** — Classifies users as _Normal_, _At Risk_, or _Deficient_ based on 14 biomarkers
- **Personalized Diet Plans** — 7-day meal plans tailored to deficiencies, age, gender, and health goals
- **Macronutrient Recommendations** — Dynamic carbs/protein/fat splits based on lab results
- **Visual Charts** — Health status comparison bars, macronutrient pie charts, diet summary tables
- **PDF Reports** — Downloadable comprehensive health reports
- **AI Chatbot (NutriBot)** — Context-aware nutrition assistant powered by Groq AI (Llama 3.3 70B)
- **User Authentication** — Registration, login, password reset via OTP (EmailJS)
- **Report History** — MongoDB-backed multi-report storage and retrieval

### Key Features
| Feature | Technology |
|---------|-----------|
| Blood Report OCR | Tesseract + EasyOCR + pdfplumber |
| Health Prediction | Random Forest / Gradient Boosting / XGBoost |
| Diet Recommendations | Rule-based + ML-assisted |
| Chatbot | Groq API (Llama 3.3 70B) |
| Database | MongoDB (PyMongo) |
| PDF Generation | ReportLab |
| Charts | Matplotlib |
| Password Reset | EmailJS + OTP |
| Frontend | Jinja2 + HTML/CSS/JS |

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                       FRONTEND                          │
│   HTML/CSS/JS Templates (Jinja2)                        │
│   ┌─────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐  │
│   │ Login/  │ │ Profile  │ │  Report   │ │ Chatbot  │  │
│   │Register │ │  Page    │ │  Viewer   │ │ Widget   │  │
│   └────┬────┘ └────┬─────┘ └─────┬─────┘ └────┬─────┘  │
│        │           │             │             │        │
├────────┼───────────┼─────────────┼─────────────┼────────┤
│        ▼           ▼             ▼             ▼        │
│                    FLASK BACKEND (app.py)                │
│   ┌──────────────────────────────────────────────────┐  │
│   │  Routes: /, /login, /register, /profile,         │  │
│   │  /analyze, /chatbot, /forgot, /verify_otp, etc.  │  │
│   └──────────┬───────────┬───────────┬───────────────┘  │
│              │           │           │                   │
│     ┌────────▼──┐  ┌─────▼─────┐  ┌─▼───────────────┐  │
│     │ OCR V2    │  │ ML Models │  │ Groq AI (Chat)  │  │
│     │(Tesseract │  │ (Health   │  │ Llama 3.3 70B   │  │
│     │ EasyOCR)  │  │  Status)  │  │ via REST API    │  │
│     └────┬──────┘  └─────┬─────┘  └─────────────────┘  │
│          │               │                               │
│     ┌────▼───────────────▼──────────────────────────┐   │
│     │           SUPPORTING MODULES                   │   │
│     │  diet_plan_v2.py  │  chart_generator_v2.py     │   │
│     │  pdf_generator_v2.py  │  mongo_helper.py       │   │
│     │  otp_service.py  │  expert_advice_v2.py        │   │
│     └────────────────────┬───────────────────────────┘   │
│                          │                               │
├──────────────────────────┼───────────────────────────────┤
│                          ▼                               │
│                     MongoDB                              │
│        ┌──────────┬──────────┬──────────────────┐        │
│        │  users   │ reports  │ otp_verifications │        │
│        └──────────┘──────────┘──────────────────┘        │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Installation & Setup

### 3.1 Prerequisites

| Requirement | Version |
|------------|---------|
| Python | 3.10+ |
| MongoDB | 6.0+ (running on `localhost:27017`) |
| Tesseract OCR | 5.x (installed and in PATH) |
| pip | Latest |

### 3.2 Installation Steps

```bash
# 1. Clone or navigate to the project
cd c:\Users\USER\project

# 2. Create virtual environment (optional but recommended)
python -m venv env1
env1\Scripts\activate        # Windows
# source env1/bin/activate   # Linux/Mac

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install additional packages for V2
pip install werkzeug easyocr pdfplumber pypdfium2 xgboost requests

# 5. Install Groq AI dependency (chatbot)
# No extra install needed — uses `requests` (already installed)

# 6. Ensure MongoDB is running
mongod --dbpath "C:\data\db"
# OR if MongoDB is a Windows service, it starts automatically

# 7. Train the ML model (first time only)
python -c "from version2.model_training_v2 import train_model_v2; train_model_v2()"

# 8. Run the application
python -m version2.app
# Server starts at http://127.0.0.1:5002/
```

### 3.3 Requirements File (`requirements.txt`)

```
flask==2.2.5
pandas==2.2.2
numpy==1.25.0
scikit-learn==1.3.2
joblib==1.3.2
reportlab==3.5.68
pillow==10.2.0
pytesseract==0.3.10
opencv-python==4.9.0.80
easyocr==1.7.2
matplotlib==3.10.7
pymongo==4.7.1
requests>=2.28.0
werkzeug>=2.2.0
pdfplumber>=0.9.0
pypdfium2>=4.0.0
```

---

## 4. Folder Structure

```
c:\Users\USER\project\
│
├── version2/                          # ⭐ Main V2 Application Code
│   ├── app.py                         # Flask backend (all routes)
│   ├── ocr_fix_v2.py                  # OCR pipeline (Tesseract + EasyOCR)
│   ├── model_training_v2.py           # ML model training pipeline
│   ├── model_inference_v2.py          # ML model inference (prediction)
│   ├── data_preprocessing_v2.py       # Dataset merging & preprocessing
│   ├── diet_plan_v2.py                # Diet plan generation logic
│   ├── chart_generator_v2.py          # Matplotlib chart generation
│   ├── pdf_generator_v2.py            # ReportLab PDF generation
│   ├── expert_advice_v2.py            # AI Chatbot (Groq/Llama 3.3)
│   ├── mongo_helper.py                # MongoDB CRUD operations
│   ├── otp_service.py                 # EmailJS OTP service
│   ├── model_v2.pkl                   # Trained ML model artifact
│   ├── processed_data_v2.csv          # Preprocessed training data
│   └── uploads/                       # Uploaded blood reports
│
├── templates/                         # Jinja2 HTML Templates
│   ├── base.html                      # Base template (includes chatbot)
│   ├── index.html                     # Landing page
│   ├── login.html                     # Login page
│   ├── register.html                  # Registration page
│   ├── profile.html                   # User profile & report history
│   ├── report.html                    # Report result display
│   ├── blood_report_result.html       # Analysis results
│   ├── check_report.html              # Upload new report
│   ├── expert.html                    # Ask Expert page
│   ├── diet_plans.html                # Diet plan viewer
│   ├── forgot.html                    # Forgot password
│   ├── verify_otp.html                # OTP verification
│   └── reset_password.html            # Password reset
│
├── static/                            # Static Assets
│   ├── css/styles.css                 # Main stylesheet
│   ├── js/                            # JavaScript files
│   └── images/                        # Static images
│
├── lab_clean_processed.csv            # Dataset 1 (Lab data)
├── nhanes_real_with_calories.csv      # Dataset 2 (NHANES)
└── requirements.txt                   # Python dependencies
```

---

## 5. Module Reference

### 5.1 `app.py` — Flask Backend (717 lines)
The central hub connecting all modules. Key responsibilities:
- **Route handling** for all 20+ endpoints
- **`process_report_pipeline()`** — The core pipeline: OCR → ML Prediction → Diet Plan → Charts
- **Session management** for user authentication
- **Context-aware chatbot endpoint** (`/chatbot`)

### 5.2 `ocr_fix_v2.py` — OCR Pipeline (715 lines)
Multi-strategy text extraction from blood report PDFs/images:
1. **pdfplumber** — Direct text extraction (fastest, for text-based PDFs)
2. **pdf2image + Tesseract** — Image-based OCR (requires Poppler)
3. **pypdfium2 + Tesseract** — Python-only fallback (no Poppler needed)
4. **EasyOCR** — Deep learning fallback for difficult images
- Contains 40+ biomarker regex patterns for comprehensive extraction

### 5.3 `model_training_v2.py` — ML Training (349 lines)
Trains 4 ML classifiers and selects the best:
- Logistic Regression, Random Forest, Gradient Boosting, XGBoost
- Uses 14 biomarker features → 3-class health status prediction
- 5-fold stratified cross-validation
- Saves model artifact as `model_v2.pkl`

### 5.4 `model_inference_v2.py` — ML Inference (297 lines)
Loads `model_v2.pkl` and provides:
- `predict_health_status()` — Returns "Normal", "At Risk", or "Deficient"
- `predict_with_confidence()` — Returns status + confidence score
- `analyze_biomarkers_v2()` — Compares values against clinical ranges
- `recommend_foods_v2()` — Food recommendations per deficiency

### 5.5 `data_preprocessing_v2.py` — Data Pipeline (187 lines)
Merges two datasets into unified training data:
- `lab_clean_processed.csv` (Lab panel data)
- `nhanes_real_with_calories.csv` (NHANES demographics data)
- Handles column mapping, missing value imputation, BMI calculation
- Generates health status labels using clinical scoring rules

### 5.6 `diet_plan_v2.py` — Diet Planning (332 lines)
Generates personalized 7-day diet plans:
- 6 diet templates: balanced, iron-rich, low-carb, heart-healthy, vitamin-boost, kidney-friendly
- Age-specific modifications (child, adult, senior)
- Gender-aware adjustments (iron needs, calcium)
- Selects primary plan based on deficiencies

### 5.7 `chart_generator_v2.py` — Visualization (217 lines)
Generates 3 chart types as base64 images:
- **Macronutrient Pie Chart** — Carbs/Protein/Fat split
- **7-Day Diet Table** — Visual meal plan summary
- **Health Status Bar Chart** — Biomarker comparison with normal ranges

### 5.8 `pdf_generator_v2.py` — PDF Reports (224 lines)
Creates downloadable PDF reports using ReportLab:
- Patient details, health status, BMI
- Lab analysis summary table
- 7-day diet chart
- Food recommendations

### 5.9 `expert_advice_v2.py` — AI Chatbot (180 lines)
Powers the NutriBot floating widget:
- **Primary:** Groq AI (Llama 3.3 70B) via REST API
- **Fallback:** Rule-based keyword responses
- System prompt designed for concise nutrition/health answers
- Context-aware: receives user profile + lab data from session

### 5.10 `mongo_helper.py` — Database Layer (183 lines)
All MongoDB CRUD operations:
- `save_user()` / `get_user_by_email()`
- `save_report()` / `get_reports_for_user()` / `get_report_by_id()`
- `save_otp()` / `verify_and_delete_otp()`
- `update_password()`

### 5.11 `otp_service.py` — Email OTP (77 lines)
Password reset via EmailJS:
- Generates 6-digit OTP
- Sends via EmailJS REST API
- OTP stored in MongoDB with 5-minute TTL

---

## 6. System Workflow

### 6.1 Complete User Journey Workflow

```
┌──────────────────────────────────────────────────────────────┐
│                    USER JOURNEY WORKFLOW                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ①  USER REGISTERS                                           │
│      │                                                        │
│      ├── Enter: name, email, password, age, gender,           │
│      │          height, weight, goal                          │
│      ├── Upload: Blood report (PDF/Image)                     │
│      ├── Backend: Password hashed → Saved to MongoDB          │
│      │                                                        │
│  ②  REPORT PROCESSING PIPELINE                               │
│      │                                                        │
│      ├── Step 1: OCR EXTRACTION                               │
│      │   ├── pdfplumber (text PDFs) OR                        │
│      │   ├── Tesseract + OpenCV preprocessing OR              │
│      │   └── EasyOCR (deep learning fallback)                 │
│      │   └── Output: Raw text string                          │
│      │                                                        │
│      ├── Step 2: BIOMARKER PARSING                            │
│      │   ├── 40+ regex patterns match biomarker names/values  │
│      │   ├── Validation against clinical ranges               │
│      │   └── Output: Dict {hemoglobin: 13.5, glucose: 95...}  │
│      │                                                        │
│      ├── Step 3: BIOMARKER NORMALIZATION                      │
│      │   ├── Map synonyms (HGB→hemoglobin, FBS→glucose)       │
│      │   └── Output: Unified biomarker dictionary              │
│      │                                                        │
│      ├── Step 4: ML HEALTH PREDICTION                         │
│      │   ├── Load model_v2.pkl (trained classifier)           │
│      │   ├── Scale features with StandardScaler               │
│      │   ├── Predict: Normal / At Risk / Deficient            │
│      │   ├── Get confidence score (probability)               │
│      │   └── Safety override with rule-based check            │
│      │                                                        │
│      ├── Step 5: LAB ASSESSMENT                               │
│      │   ├── Compare each value to clinical reference ranges  │
│      │   ├── Flag LOW/HIGH/NORMAL for each biomarker          │
│      │   ├── Calculate deviation percentages                  │
│      │   └── Output: Assessment list + deficiencies list      │
│      │                                                        │
│      ├── Step 6: DIET PLAN GENERATION                         │
│      │   ├── Select primary plan based on deficiencies         │
│      │   ├── Adjust for age group, gender, goal               │
│      │   ├── Generate 7-day meal plan (B/L/D/Snacks)          │
│      │   └── Calculate dynamic macros (carbs/protein/fat)     │
│      │                                                        │
│      ├── Step 7: CHART GENERATION                             │
│      │   ├── Macronutrient pie chart                          │
│      │   ├── Health status comparison bars                    │
│      │   └── Diet summary table                               │
│      │                                                        │
│      └── Step 8: SAVE & DISPLAY                               │
│          ├── Save report to MongoDB (linked to user email)    │
│          ├── Render result page with charts                   │
│          └── PDF available for download                       │
│                                                               │
│  ③  USER VIEWS PROFILE                                       │
│      ├── See all past reports (sorted by date)                │
│      ├── View individual report details                       │
│      ├── Download PDF for any report                          │
│      ├── Delete reports                                       │
│      └── Upload new reports ("Check Another Person")          │
│                                                               │
│  ④  AI CHATBOT (NutriBot)                                    │
│      ├── User clicks floating green button                    │
│      ├── Sends message via AJAX to /chatbot                   │
│      ├── Backend pulls user context from session + MongoDB    │
│      │   ├── Profile: name, age, gender, BMI, goal            │
│      │   ├── Latest lab values                                │
│      │   ├── Health status & deficiencies                     │
│      │   └── Diet plan & macros                               │
│      ├── Context + message sent to Groq AI (Llama 3.3 70B)   │
│      └── AI response displayed in chat window                 │
│                                                               │
│  ⑤  PASSWORD RESET                                           │
│      ├── User enters email on /forgot page                    │
│      ├── OTP generated & saved to MongoDB (5-min TTL)         │
│      ├── OTP sent to user email via EmailJS                   │
│      ├── User enters OTP on /verify_otp page                  │
│      └── User sets new password on /reset_password page       │
└──────────────────────────────────────────────────────────────┘
```

---

## 7. Database Schema

**Database:** `nutrition_app_v2` (MongoDB)

### 7.1 `users` Collection
```json
{
  "_id": ObjectId("..."),
  "name": "John Doe",
  "email": "john@example.com",
  "password_hash": "scrypt:32768:...",
  "age": 25,
  "gender": 1,              // 1 = Male, 0 = Female
  "height": 175,            // cm
  "weight": 70,             // kg
  "bmi": 22.86,
  "goal": "Maintenance"
}
```

### 7.2 `reports` Collection
```json
{
  "_id": ObjectId("..."),
  "user_email": "john@example.com",
  "timestamp": "2026-02-18 10:30:00",
  "lab_results": {
    "hemoglobin": 13.5,
    "glucose": 95,
    "total_cholesterol": 180,
    ...
  },
  "health_status": "Normal",
  "deficiencies": ["iron", "vitamin_d"],
  "macros": {"carbs": 50, "protein": 30, "fat": 20},
  "diet_plan": {
    "Monday": {"breakfast": "...", "lunch": "...", "dinner": "..."},
    ...
  },
  "assessment": [
    {"test": "hemoglobin", "value": 13.5, "status": "NORMAL", ...},
    ...
  ],
  "pdf_path": "/download_report/ObjectId"
}
```

### 7.3 `otp_verifications` Collection
```json
{
  "_id": ObjectId("..."),
  "email": "john@example.com",
  "otp": "482931",
  "expires_at": ISODate("2026-02-18T11:05:00Z"),
  "verified": false,
  "created_at": ISODate("2026-02-18T11:00:00Z")
}
```

---

## 8. API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Landing page |
| GET/POST | `/login` | User login |
| GET/POST | `/register` | User registration + report upload |
| GET | `/logout` | Logout & clear session |
| GET | `/profile` | User profile with report history |
| GET/POST | `/profile/edit` | Edit profile |
| GET | `/view_report/<id>` | View specific report |
| GET | `/download_report/<id>` | Download report PDF |
| POST | `/delete_report/<id>` | Delete a report |
| GET/POST | `/analyze` | Upload & analyze new report |
| POST | `/download_pdf` | Generate & download PDF |
| POST | `/chatbot` | **AI chatbot (AJAX, context-aware)** |
| GET/POST | `/forgot` | Password reset - email entry |
| GET/POST | `/verify_otp` | OTP verification |
| GET/POST | `/reset_password` | Set new password |
| GET | `/expert` | Expert advice page |
| POST | `/ask_expert` | Submit question to expert |
| GET | `/diet_plan` | Diet plan page |
| GET | `/progress` | Progress tracking |
| GET | `/categories/<cat>` | Article categories |

---

## 9. Frontend Templates

All templates extend `base.html` which includes:
- **Header** with navigation (Home, Profile, Expert, Articles, Diet Plans)
- **Profile dropdown** with user avatar and logout
- **Footer** with disclaimer
- **NutriBot chatbot widget** (floating bottom-left button + chat window)
- **Google Fonts** (Poppins), **Font Awesome** icons

### Key CSS Variables (from `styles.css`)
```css
:root {
  --primary: #11623A;
  --primary-light: #2FA36C;
  --text-primary: #1a1a2e;
  --bg-gradient: linear-gradient(135deg, #f0fdf4, #ecfdf5);
}
```

---

## 10. AI Chatbot Integration

### Architecture
```
User types message → JavaScript fetch() → /chatbot POST
    ↓
Flask endpoint builds user context:
    - session['user'] → name, age, gender, BMI, goal
    - db.get_reports_for_user() → lab values, health status, deficiencies
    ↓
Context + message sent to Groq API:
    POST https://api.groq.com/openai/v1/chat/completions
    Model: llama-3.3-70b-versatile
    ↓
AI response returned → JavaScript renders in chat window
```

### Chatbot Features
- **Glassmorphism UI** with smooth animations
- **Typing indicator** (3 bouncing dots)
- **Mobile responsive** (adapts for small screens)
- **Pulsing FAB button** with hover effects
- **Context-aware**: Knows user's name, lab values, health status
- **Fallback**: Rule-based responses if API fails
- **Multilingual**: Responds in Hindi if asked in Hindi

---

## 11. PDF Report Generation

Uses **ReportLab** to generate professional PDF reports containing:
1. Patient header (name, age, gender, date)
2. Health status badge (color-coded)
3. BMI classification
4. Lab analysis table (value, status, recommendation)
5. 7-day diet plan table
6. Food recommendations list
7. Macronutrient breakdown

---

## 12. Password Reset Flow (EmailJS)

```
/forgot → Generate OTP → Save to MongoDB (5-min TTL)
    → Send email via EmailJS API
    → /verify_otp → Check OTP against MongoDB
    → /reset_password → Hash new password → Update MongoDB
```

**EmailJS Configuration** (in `otp_service.py`):
- Service ID, Template ID, Public Key, Private Key
- Template uses `{{reply_to}}` for recipient email
- Template uses `{{passcode}}` for OTP code
- Requires "Allow non-browser API" enabled in EmailJS dashboard

---

## 13. Execution Commands

```bash
# Start the server
python -m version2.app
# Available at: http://127.0.0.1:5002/

# Train the ML model
python -c "from version2.model_training_v2 import train_model_v2; train_model_v2()"

# Preprocess data
python -c "from version2.data_preprocessing_v2 import *; df = load_and_merge_data(); preprocess_and_label(df).to_csv('version2/processed_data_v2.csv', index=False)"

# Test chatbot
python -c "from version2.expert_advice_v2 import get_expert_response; print(get_expert_response('What foods are rich in iron?'))"

# Test model inference
python -m version2.model_inference_v2

# Check MongoDB connection
python -c "from version2.mongo_helper import *; print('DB connected:', db is not None)"
```

---

## 14. Error Handling & Logging

- **Flask logging** configured at `INFO` level via `logging.basicConfig()`
- **Terminal output** for each report shows:
  - OCR extraction status
  - Predicted health status + confidence
  - Class probabilities
  - Lab value deviations
  - Clinical risk score
- **Chatbot** gracefully falls back to rule-based responses on API failure
- **OCR** has 3-level fallback: pdfplumber → Tesseract → EasyOCR
- **Model** uses safety override: if rule-based and ML disagree, rule-based wins

---

## 15. Environment & Dependencies

### System Requirements
| Component | Requirement |
|-----------|-------------|
| OS | Windows 10/11, Linux, macOS |
| Python | 3.10+ |
| MongoDB | 6.0+ (localhost:27017) |
| Tesseract | 5.x (in PATH) |
| RAM | 4GB minimum, 8GB recommended |
| Disk | ~500MB for models + data |

### External API Keys
| Service | Key Location | Purpose |
|---------|-------------|---------|
| Groq AI | `expert_advice_v2.py` | Chatbot AI responses |
| EmailJS | `otp_service.py` | Password reset emails |

### Key Python Packages
| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 2.2.5 | Web framework |
| pandas | 2.2.2 | Data manipulation |
| scikit-learn | 1.3.2 | ML training/inference |
| pymongo | 4.7.1 | MongoDB driver |
| pytesseract | 0.3.10 | OCR engine interface |
| easyocr | 1.7.2 | Deep learning OCR |
| reportlab | 3.5.68 | PDF generation |
| matplotlib | 3.10.7 | Chart generation |
| opencv-python | 4.9.0.80 | Image preprocessing |
| requests | 2.32+ | HTTP calls (Groq, EmailJS) |
| werkzeug | 2.2+ | Password hashing |
| joblib | 1.3.2 | Model serialization |
| pillow | 10.2.0 | Image handling |

---

*End of Implementation Document*
