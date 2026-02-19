# 🔄 Complete Data Flow Documentation — Input Movement to Frontend Output

## How Every Input Travels Through Every File to Reach the Frontend

---

## Table of Contents

1. [Overview](#1-overview)
2. [Complete Data Flow Diagram](#2-complete-data-flow-diagram)
3. [Flow 1: User Registration + Report Upload](#flow-1-registration--report-upload)
4. [Flow 2: Viewing a Report](#flow-2-viewing-a-report)
5. [Flow 3: PDF Download](#flow-3-pdf-download)
6. [Flow 4: Chatbot Interaction](#flow-4-chatbot-interaction)
7. [Flow 5: Password Reset (OTP)](#flow-5-password-reset-otp)
8. [Flow 6: Analyze Another Person's Report](#flow-6-analyze-another-persons-report)
9. [Frontend Variable Reference](#frontend-variable-reference)
10. [How Each Chart Reaches the Browser](#how-each-chart-reaches-the-browser)

---

## 1. Overview

This document traces **every input** from the moment the user types or uploads it, through **every Python file** it passes through, and explains **exactly what variable** the frontend template uses to display the final output.

### Simple Analogy

Think of it like a **post office**:
- **User** = Person writing a letter (uploading blood report)
- **app.py** = Post office reception (receives and routes)
- **ocr_fix_v2.py** = Letter opener (reads the content)
- **model_inference_health_v2.py** = Doctor (gives health verdict)
- **diet_plan_generator_v2.py** = Chef (creates meal plan)
- **chart_generator_v2.py** = Artist (draws charts)
- **report.html** = Display board (shows everything to the user)

---

## 2. Complete Data Flow Diagram

```
USER BROWSER                                   SERVER (Python)
═══════════                                    ════════════════

┌──────────────────┐
│  register.html   │
│                  │
│  Name: [Murali ] │───── name ──────────────────────────────────────────────────────────┐
│  Email:[m@g.com] │───── email ─────────────────────────────────────────────────────────┤
│  Age:  [25     ] │───── age ───────────────────────────────────────────────────────────┤
│  Gender:[Male  ] │───── gender ────────────────────────────────────────────────────────┤
│  Height:[175   ] │───── height ────────────────────────────────────────────────────────┤
│  Weight:[70    ] │───── weight ────────────────────────────────────────────────────────┤
│  File: [📄 PDF ] │───── report (file) ─────────────────────────────────────────────────┤
│  [Register]      │                                                                     │
└──────────────────┘                                                                     │
         │                                                                               ▼
         │ POST /register                                                    ┌───────────────────────┐
         │                                                                   │     app.py            │
         ▼                                                                   │  register() route     │
                                                                             │                       │
    ┌────────────────────────────────────────────────────────────────────────►│  1. Collect form data │
    │                                                                        │  2. Build user_data   │
    │                                                                        │     dict              │
    │                                                                        │  3. Save PDF file     │
    │                                                                        │  4. Call pipeline()   │
    │                                                                        └───────┬───────────────┘
    │                                                                                │
    │                                                                                ▼
    │                                                                   process_report_pipeline()
    │                                                                                │
    │                                    ┌───────────────────────────────────────────┤
    │                                    ▼                                           │
    │                          ┌──────────────────────┐                              │
    │                          │   ocr_fix_v2.py       │                              │
    │                          │                       │                              │
    │                          │  PDF ──► Image ──►    │                              │
    │                          │  Tesseract OCR ──►    │                              │
    │                          │  Raw Text ──►         │                              │
    │                          │  Regex Parsing ──►    │                              │
    │                          │  Validation ──►       │                              │
    │                          │                       │                              │
    │                          │  OUTPUT:              │                              │
    │                          │  lab_values = {       │                              │
    │                          │    'hemoglobin': 14.2 │                              │
    │                          │    'glucose': 95.0    │                              │
    │                          │  }                    │                              │
    │                          └───────────┬──────────┘                              │
    │                                      │                                          │
    │                                      ▼                                          │
    │                          ┌──────────────────────────┐                           │
    │                          │ model_inference_health    │                           │
    │                          │                           │                           │
    │                          │  Load health_model_v2.pkl │                           │
    │                          │  Scale features           │                           │
    │                          │  Random Forest predict    │                           │
    │                          │  Rule-based override      │                           │
    │                          │                           │                           │
    │                          │  OUTPUT:                  │                           │
    │                          │  health_status = "Normal" │                           │
    │                          │  confidence = 0.95        │                           │
    │                          └───────────┬──────────────┘                           │
    │                                      │                                          │
    │                                      ▼                                          │
    │                          ┌──────────────────────────┐                           │
    │                          │ diet_plan_generator_v2    │                           │
    │                          │                           │                           │
    │                          │  Load diet_model_v2.pkl   │                           │
    │                          │  Get ML food recs         │                           │
    │                          │  Mix with South Indian DB │                           │
    │                          │  Build 7-day plan         │                           │
    │                          │                           │                           │
    │                          │  OUTPUT:                  │                           │
    │                          │  diet_plan = {            │                           │
    │                          │    'Monday': {            │                           │
    │                          │      'Breakfast': 'Idli'  │                           │
    │                          │    }, ...                  │                           │
    │                          │  }                        │                           │
    │                          └───────────┬──────────────┘                           │
    │                                      │                                          │
    │                                      ▼                                          │
    │                          ┌──────────────────────────┐                           │
    │                          │  Back to app.py           │                           │
    │                          │                           │◄──────────────────────────┘
    │                          │  Bundles report_data dict │
    │                          │  Saves to MongoDB         │
    │                          │  Redirects to /report/<id>│
    │                          └───────────┬──────────────┘
    │                                      │
    │                                      ▼
    │                          ┌──────────────────────────┐
    │                          │  view_report() route      │
    │                          │                           │
    │                          │  Fetch from MongoDB       │
    │                          │  Generate charts ──────────────────►  chart_generator_v2.py
    │                          │  Render report.html       │                    │
    │                          └───────────┬──────────────┘                    │
    │                                      │                          Returns Base64 images
    │                                      │                                    │
    │                                      ▼                                    │
    │                          ┌──────────────────────────┐◄───────────────────┘
    │                          │      report.html          │
    │                          │                           │
    │                          │  {{ health_status }}       │
    │                          │  {{ lab_data }}            │
    │                          │  {{ diet_plan }}           │
    │                          │  {{ macros }}              │
    │                          │  {{ diet_charts }}         │
    │                          │  {{ recommendations }}     │
    │                          │                           │
    │                          │  DISPLAYED TO USER ✓      │
    │                          └──────────────────────────┘
```

---

## Flow 1: Registration + Report Upload

This is the **primary flow** — the main path data takes through the system.

### Step 1: User Fills HTML Form → Browser

**File:** `templates/register.html`

The user fills in a form with these fields:
```html
<input type="text" name="name" required>          <!-- "Murali" -->
<input type="email" name="email" required>        <!-- "murali@gmail.com" -->
<input type="number" name="age">                  <!-- 25 -->
<select name="gender">                            <!-- "male" -->
<input type="number" name="height">               <!-- 175 -->
<input type="number" name="weight">               <!-- 70 -->
<input type="file" name="report">                 <!-- blood_report.pdf -->
```

When the user clicks **"Register"**, the browser sends an HTTP POST request to `/register` with all this data packed as `multipart/form-data` (because there's a file).

---

### Step 2: Flask Receives Form Data → `app.py`

**File:** `version2/app.py` → `register()` function (Line 315)

```python
# The browser's form data arrives here via Flask's request object
name = request.form.get('name')         # "Murali"
email = request.form.get('email')       # "murali@gmail.com"
age = int(request.form.get('age', 25))  # 25 (converted from string to integer)
gender_str = request.form.get('gender') # "male"
gender = 1 if gender_str.lower() in ['male', 'm'] else 0  # 1 (binary encoding)
height = float(request.form.get('height', 170))  # 175.0
weight = float(request.form.get('weight', 60))    # 70.0

# Build user profile dictionary
user_data = {
    'name': 'Murali', 'email': 'murali@gmail.com',
    'age': 25, 'gender': 1, 'height': 175.0, 'weight': 70.0, 'goal': 'Health'
}

# Handle file upload
f = request.files.get('report')                   # The uploaded PDF file object
filename = secure_filename(f.filename)             # "blood_report.pdf" (sanitized)
filepath = os.path.join('uploads', filename)       # "uploads/blood_report.pdf"
f.save(filepath)                                   # File saved to disk

# Calculate BMI
height_m = 175.0 / 100  # = 1.75 meters
user_data['bmi'] = 70.0 / (1.75 ** 2)  # = 22.86
```

**What moves forward:**
- `filepath` = `"uploads/blood_report.pdf"` → goes to OCR module
- `user_data` = complete user profile dict → goes to pipeline

---

### Step 3: Pipeline Calls OCR → `ocr_fix_v2.py`

**File:** `version2/ocr_fix_v2.py`

```python
# Called by: process_report_pipeline(filepath, user_data)

# STEP 3a: Determine file type and extract text
extracted_text = extract_blood_report_text_v2("uploads/blood_report.pdf")
# Internally:
#   1. Checks extension → .pdf
#   2. Tries pdfplumber first (for digital PDFs)
#   3. If that fails, converts PDF to images at 300 DPI
#   4. Preprocesses images (grayscale conversion)
#   5. Runs Tesseract OCR on each page
#   6. Returns raw text string

# extracted_text now contains something like:
# "COMPLETE BLOOD COUNT\nHemoglobin: 14.2 g/dL\nGlucose (Fasting): 95 mg/dL\n
#  Total Cholesterol: 185 mg/dL\nWBC: 7500 /uL\n..."

# STEP 3b: Parse text using regex patterns
lab_values = parse_lab_values_v2(extracted_text)
# For each biomarker (hemoglobin, glucose, etc.):
#   1. Try multiple regex patterns
#   2. Extract the numeric value
#   3. Validate against broad ranges (hemoglobin must be 5-25)
#   4. If valid, add to dict

# lab_values = {'hemoglobin': 14.2, 'glucose': 95.0, 'total_cholesterol': 185.0, 'wbc': 7500.0}

# STEP 3c: Normalize keys
lab_values = normalize_biomarkers(lab_values)
# 'fasting_glucose' → 'glucose', 'hgb' → 'hemoglobin'
# Ensures consistent naming across all modules
```

**What moves forward:**
- `lab_values` = `{'hemoglobin': 14.2, 'glucose': 95.0, ...}` → goes to health model

---

### Step 4: Health Prediction → `model_inference_health_v2.py`

**File:** `version2/model_inference_health_v2.py`

```python
# Called by: predict_health_status(full_profile)
# full_profile = user_data + lab_values merged

# STEP 4a: Load model (lazy — only once)
pipeline = load_model()  # Loads health_model_v2.pkl (15 MB)
# Contains: {scaler, model (RandomForest), feature_names}

# STEP 4b: Build input vector
# feature_names from training = ['age', 'gender', 'hemoglobin', 'glucose', ...]
vector = [25, 1, 14.2, 95.0, 185.0, ...]  # Values in same order as training

# STEP 4c: Scale features
X_scaled = scaler.transform(X_input)
# StandardScaler: x_scaled = (x - mean) / std
# Makes all features comparable regardless of units

# STEP 4d: Predict
pred = model.predict(X_scaled)[0]  # Returns 0, 1, or 2
# 0 = Normal, 1 = At Risk, 2 = Action Needed

# STEP 4e: Get probabilities
probs = model.predict_proba(X_scaled)[0]  # e.g., [0.95, 0.03, 0.02]
confidence = max(probs)  # 0.95 = 95% confident

# STEP 4f: Rule-based safety check
# Hardcoded rules to catch cases the model might miss
if hemoglobin < 10: rule_status = 'Action Needed'
if glucose > 200: rule_status = 'Action Needed'
```

**What moves forward:**
```python
health_result = {
    'status_label': 'Normal',
    'confidence': 0.95,
    'class_probabilities': {'Normal': 0.95, 'At Risk': 0.03, 'Action Needed': 0.02},
    'rule_based_status': 'Normal'
}
```

---

### Step 5: Clinical Assessment → `ocr_fix_v2.py`

**File:** `version2/ocr_fix_v2.py` → `assess_lab_values_v2()`

```python
# Called by: assess_lab_values_v2(lab_values, age=25, gender='Male')

# For each biomarker, compare against REFERENCE_RANGES:
# hemoglobin: value=14.2, range=13.5-17.5 → STATUS: NORMAL
# glucose: value=95.0, range=70-100 → STATUS: NORMAL
# If glucose was 130: range=70-100 → STATUS: HIGH, deviation=+30%

assessment = [
    {'test': 'Hemoglobin', 'value': 14.2, 'status': 'NORMAL', 'deviation_pct': 0, ...},
    {'test': 'Glucose', 'value': 95.0, 'status': 'NORMAL', 'deviation_pct': 0, ...},
    {'test': 'Total Cholesterol', 'value': 185.0, 'status': 'NORMAL', ...}
]

deficiencies = []  # Empty because all values are NORMAL
# If glucose was 130 → deficiencies = ['Glucose']
```

---

### Step 6: Diet Plan Generation → `diet_plan_generator_v2.py`

**File:** `version2/diet_plan_generator_v2.py`

```python
# Called by: generate_v2_diet_plan(user_data)

# STEP 6a: Get ML food recommendations
base_recs = predict_food_recommendation(user_data)
# Calls model_inference_diet_v2.py internally
# Returns: ['Oatmeal with Berries', 'Lentil Soup', 'Greek Yogurt Parfait']

# STEP 6b: Build 7-day plan from South Indian database
for day in ['Monday', 'Tuesday', ..., 'Sunday']:
    day_plan['Breakfast'] = random.choice(SOUTH_INDIAN_OPTIONS['Breakfast'])
    day_plan['Lunch'] = random.choice(SOUTH_INDIAN_OPTIONS['Lunch'])
    day_plan['Snacks'] = random.choice(SOUTH_INDIAN_OPTIONS['Snacks'])
    day_plan['Dinner'] = random.choice(SOUTH_INDIAN_OPTIONS['Dinner'])

    # 30% chance: replace dinner with ML recommendation
    if random.random() > 0.7:
        day_plan['Dinner'] = random.choice(base_recs)
```

---

### Step 7: Macronutrient Calculation → `app.py`

**File:** `version2/app.py` → inside `process_report_pipeline()`

```python
# Dynamic macro split based on user's goal and health status
goal = user_profile.get('goal', 'Maintenance').lower()

# Default split
c, p, f = 50, 30, 20  # Carbs 50%, Protein 30%, Fat 20%

# Adjust based on goal
if 'loss' in goal:      c, p, f = 40, 40, 20  # More protein for weight loss
elif 'muscle' in goal:  c, p, f = 45, 35, 20  # More protein for muscle gain

# Override if health issue detected
if 'glucose' in deficiencies:
    c, p, f = 35, 35, 30  # Less carbs if diabetes risk!

macros = {'carbs': 50, 'protein': 30, 'fat': 20}
```

---

### Step 8: Data Saved to MongoDB → `mongo_helper.py`

**File:** `version2/mongo_helper.py`

```python
# Save user profile
saved_user = db.save_user(user_data)
# MongoDB document in 'users' collection:
# { "_id": ObjectId("..."), "name": "Murali", "email": "murali@gmail.com",
#   "age": 25, "gender": 1, "height": 175, "weight": 70, "bmi": 22.86 }

# Save complete report
saved_report_id = db.save_report(email, report_data)
# MongoDB document in 'reports' collection:
# { "_id": ObjectId("abc123"), "user_email": "murali@gmail.com",
#   "timestamp": "2026-02-19 10:42:45",
#   "lab_results": {"hemoglobin": 14.2, "glucose": 95.0},
#   "health_status": "Normal",
#   "diet_plan": {"Monday": {...}, ...},
#   "macros": {"carbs": 50, "protein": 30, "fat": 20},
#   "deficiencies": [],
#   "assessment": [...] }
```

---

### Step 9: Redirect to Report Page → `app.py`

```python
# After saving, redirect browser to the report view
return redirect(url_for('view_report', report_id=saved_report_id))
# Browser navigates to: /report/abc123
```

---

### Step 10: Report Page Loads → `app.py` → `chart_generator_v2.py`

**File:** `version2/app.py` → `view_report()` (Line 410)

```python
# Fetch report from MongoDB
report_data = db.get_report_by_id("abc123")

# Generate charts ON THE FLY (not saved to disk)
chart_macros = generate_macronutrient_chart({'carbs': 50, 'protein': 30, 'fat': 20})
# Returns: "data:image/png;base64,iVBORw0KGgoAAAANSUhEU..."
# This is a pie chart as a Base64 string

chart_meal_plan = generate_diet_chart_image(diet_plan)
# Returns: Base64 table image

chart_health = generate_health_status_chart(lab_values, "Normal")
# Returns: Base64 horizontal bar chart

diet_charts = {
    'macronutrient_chart': chart_macros,     # Base64 pie chart
    'meal_plan_chart': chart_meal_plan,       # Base64 table
    'lab_status_chart': chart_health          # Base64 bar chart
}
```

---

### Step 11: HTML Template Renders → `report.html`

**File:** `templates/report.html`

The `render_template()` function passes all variables to Jinja2:

```python
return render_template('report.html',
    lab_data=lab_values,            # {'hemoglobin': 14.2, 'glucose': 95.0}
    prediction=2000,                # Daily calories (integer)
    health_status='Normal',         # String
    deficiencies=[],                # List of abnormal biomarkers
    diet_plan={...},                # Full diet plan object
    assessment=[...],               # Per-biomarker analysis
    macros={'carbs': 50, ...},      # Macro split
    diet_charts={...},              # Base64 chart images
    report=[...],                   # Summary strings
    recommendations=[...]          # Food recommendation strings
)
```

### What Each Template Variable Displays

| Template Code | Source Variable | What User Sees |
|--------------|-----------------|----------------|
| `{{ prediction }} kcal` | `prediction` (int: 2000) | **"2000 kcal"** in the Daily Calories box |
| `{{ health_status }}` | `health_status` (str) | **"Normal"** in green or **"At Risk"** in orange |
| `{{ _carbs_pct }}% / {{ _protein_pct }}% / {{ _fat_pct }}%` | `macros` dict | **"50% / 30% / 20%"** in Macros section |
| `{% for line in report %}{{ line }}{% endfor %}` | `report` (list) | Bullet points: "Age: 25, Male, 175cm, 70kg" |
| `{% for i in recommendations %}{{ i }}{% endfor %}` | `recommendations` (list) | "Eat more Hemoglobin rich foods" |
| `<img src="{{ diet_charts['macronutrient_chart'] }}">` | Base64 string | **Pie chart image** rendered inline |
| `<img src="{{ diet_charts['lab_status_chart'] }}">` | Base64 string | **Bar chart** of lab values vs ranges |
| `{{ diet_plan['primary']['name'] }}` | `diet_plan` dict | **"South Indian Fusion Plan"** |
| `{% for reason in diet_plan['reasoning'] %}` | `diet_plan['reasoning']` | Bullet list of why this plan was chosen |
| `{% for meal_type, meal_desc in diet_plan['primary']['meals'].items() %}` | Meals dict | Cards showing Breakfast/Lunch/Dinner/Snacks |

### Jinja2 Logic for Macros Normalization (Lines 14–37 of report.html)

```html
{# The macros might arrive as whole numbers (50) or fractions (0.5) #}
{# This code handles both cases: #}
{% set _carbs_raw = macros.get('carbs', 50) %}
{% if _carbs_raw > 1 %}
  {% set _carbs_pct = (_carbs_raw)|round(0) %}     {# 50 → 50% #}
  {% set _carbs_frac = _carbs_raw / 100.0 %}       {# 50 → 0.5 #}
{% else %}
  {% set _carbs_pct = (_carbs_raw * 100)|round(0) %} {# 0.5 → 50% #}
  {% set _carbs_frac = _carbs_raw %}                  {# 0.5 stays 0.5 #}
{% endif %}

{# Used for Daily Targets calculation: #}
{# Carbs grams = (2000 * 0.5) / 4 = 250g #}
{# Protein grams = (2000 * 0.3) / 4 = 150g #}
{# Fat grams = (2000 * 0.2) / 9 = 44g #}
```

---

## Flow 2: Viewing a Report

```
Browser: GET /report/abc123
    │
    ▼
app.py → view_report("abc123")
    │
    ├── MongoDB: db.get_report_by_id("abc123")
    │   Returns: { lab_results, health_status, diet_plan, macros, ... }
    │
    ├── chart_generator_v2.py:
    │   ├── generate_macronutrient_chart(macros)    → Base64 pie chart
    │   ├── generate_diet_chart_image(diet_plan)    → Base64 table image
    │   └── generate_health_status_chart(lab_values) → Base64 bar chart
    │
    └── render_template('report.html', lab_data=..., diet_charts=..., ...)
         │
         ▼
    Browser displays: Charts, Lab Analysis, Diet Plan, Macros, Download button
```

---

## Flow 3: PDF Download

```
Browser: GET /download_pdf
    │
    ▼
app.py → download_pdf()
    │
    ├── Read report_data from session['last_report']
    │
    ├── Re-generate charts (same as Flow 2)
    │
    ├── pdf_generator_v2.py → generate_pdf_v2(...)
    │   │
    │   ├── Page 1: User Info Table → Health Status → Deficiencies → Macro Chart → Food Recs Table
    │   ├── Page 2: 7-Day Diet Plan Table (Day | Breakfast | Lunch | Snacks | Dinner)
    │   │
    │   └── Returns: io.BytesIO buffer (PDF in memory)
    │
    └── send_file(buffer, download_name="Nutrition_Report_20260219.pdf")
         │
         ▼
    Browser: Downloads PDF file to user's computer
```

---

## Flow 4: Chatbot Interaction

```
Browser: User types "What should I eat?" in chatbot widget
    │
    ├── JavaScript: fetch('/chatbot', {method: 'POST', body: JSON.stringify({message: "What should I eat?"})})
    │
    ▼
app.py → chatbot()
    │
    ├── Read user profile from session
    │   context_parts.append("USER PROFILE: Name=Murali, Age=25, Gender=Male, BMI=22.86")
    │
    ├── Fetch latest report from MongoDB
    │   context_parts.append("LATEST LAB VALUES: hemoglobin=14.2, glucose=95.0")
    │   context_parts.append("HEALTH STATUS: Normal")
    │   context_parts.append("RECOMMENDED MACROS: Carbs=50%, Protein=30%, Fat=20%")
    │
    ├── Build full message:
    │   "[USER CONTEXT]\n...all context...\n[END CONTEXT]\n\nUser's question: What should I eat?"
    │
    ├── expert_advice_v2.py → get_expert_response(full_message, 'general', 'NutriBot')
    │   │
    │   ├── Sends to Groq API (LLaMA 3.3-70B model):
    │   │   POST https://api.groq.com/openai/v1/chat/completions
    │   │   System Prompt: "You are NutriBot, an expert AI nutrition assistant..."
    │   │   User Message: "[USER CONTEXT]...[END CONTEXT]\n\nWhat should I eat?"
    │   │
    │   ├── Groq Returns: "Based on your profile Murali, your lab values look great! 
    │   │                   Since your BMI is healthy at 22.86, I'd recommend 
    │   │                   starting with Idli with Sambar for breakfast..."
    │   │
    │   └── If Groq fails → fallback to KEYWORDS matching → random response from category
    │
    └── return jsonify({'reply': 'Based on your profile Murali...'})
         │
         ▼
    JavaScript: Displays bot reply in chatbot window as a green bubble
```

---

## Flow 5: Password Reset (OTP)

```
Step 1: User clicks "Forgot Password" → GET /forgot → renders forgot.html

Step 2: User enters email → POST /forgot
    │
    ▼
app.py → forgot()
    ├── db.get_user_by_email("murali@gmail.com")  → Checks user exists
    ├── otp_service.py → generate_otp()           → "483927" (6 random digits)
    ├── mongo_helper.py → db.save_otp(email, "483927")
    │   MongoDB otp_verifications: {email, otp: "483927", expires_at: now+5min}
    ├── otp_service.py → send_otp_email(email, "483927")
    │   │
    │   ├── Always prints to terminal: [OTP SERVICE] Code: 483927
    │   └── POST https://api.emailjs.com/api/v1.0/email/send
    │       Body: {service_id, template_id, template_params: {reply_to: email, passcode: "483927"}}
    │       → User receives email with OTP code
    │
    └── redirect to /verify_otp

Step 3: User enters OTP → POST /verify_otp
    │
    ▼
app.py → verify_otp()
    └── db.verify_and_delete_otp(email, "483927")
        ├── Checks: record exists? not expired? OTP matches?
        ├── If valid: deletes OTP record, sets session['authorized_reset'] = True
        └── redirect to /reset_password

Step 4: User enters new password → POST /reset_password
    │
    ▼
app.py → reset_password()
    ├── generate_password_hash(password)  → "pbkdf2:sha256:260000$..."
    ├── db.update_password(email, hashed_password)
    │   MongoDB users: updates password_hash field
    └── redirect to /login
```

---

## Flow 6: Analyze Another Person's Report

```
Browser: POST /analyze_blood_report (from profile.html form)
    │
    ├── Input: person_name, age, gender, height, weight, blood_report (file)
    │
    ▼
app.py → analyze_blood_report()
    │
    ├── Same as Flow 1 steps 2-7 (OCR → Health → Diet → Charts)
    │   but with a temporary user profile instead of registered user
    │
    └── render_template('report.html', ...)  → Renders directly (no DB save)
```

---

## Frontend Variable Reference

### Complete mapping: Python variable → Template variable → What displays

| Python (app.py) | Template (report.html) | Display |
|-----------------|----------------------|---------|
| `lab_values` dict | `{{ lab_data }}` | Biomarker values in Lab Analysis card |
| `2000` (int) | `{{ prediction }}` | "2000 kcal" header |
| `'Normal'` (str) | `{{ health_status }}` | Green/Orange/Red status badge |
| `['Glucose']` (list) | `{{ deficiencies }}` | List of flagged biomarkers |
| `{'carbs':50,...}` | `{{ macros }}` | Pie chart data + percentage display |
| `{'Monday':{...}}` | `{{ diet_plan }}` | 7-day meal cards + table |
| `[{test,value,status}]` | `{{ assessment }}` | Per-biomarker analysis rows |
| Base64 strings | `{{ diet_charts.macronutrient_chart }}` | Inline `<img>` pie chart |
| Base64 strings | `{{ diet_charts.meal_plan_chart }}` | Inline `<img>` table |
| Base64 strings | `{{ diet_charts.lab_status_chart }}` | Inline `<img>` bar chart |
| `['Profile: 25yrs, Male']` | `{{ report }}` | Summary bullet points |
| `['Eat more Glucose rich foods']` | `{{ recommendations }}` | Blue recommendation cards |

### base.html Variables (Available on ALL pages)

| Variable | Source | Display |
|----------|--------|---------|
| `{{ session.get('user').get('name') }}` | Flask session | Username in navbar |
| `{{ now.year }}` | `inject_now()` context processor | "© 2026" in footer |
| `{{ url_for('login') }}` | Flask URL generator | Login link href |

---

## How Each Chart Reaches the Browser

### Theory: Why Base64?

Normal images require saving to disk and serving via a URL. Base64 encoding converts image binary into a text string that can be embedded **directly in HTML**. This means:
- No disk writes (faster)
- No extra HTTP requests (the image IS the HTML)
- Charts live in memory only (cleaned up by garbage collector)

### The Journey of a Chart

```
chart_generator_v2.py
    │
    ├── matplotlib creates Figure object in RAM
    ├── fig.savefig(BytesIO_buffer, format='png')     ← Image saved to memory buffer
    ├── base64.b64encode(buffer.getvalue())            ← Binary → Base64 text
    ├── Returns: "data:image/png;base64,iVBORw0KGgo..." ← Data URI
    │
    ▼
app.py
    │
    ├── Stores in dict: diet_charts['macronutrient_chart'] = "data:image/png;base64,..."
    │
    ▼
report.html (Jinja2)
    │
    ├── <img src="{{ diet_charts['macronutrient_chart'] }}">
    │   Renders as: <img src="data:image/png;base64,iVBORw0KGgo...">
    │
    ▼
Browser
    │
    └── Decodes Base64 → Displays pie chart image inline
```

---

*Document generated on 2026-02-19. This traces every input through every file in the Personalized Nutrition System V2.*
