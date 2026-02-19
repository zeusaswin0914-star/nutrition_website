# Technical Walkthrough - Personalized Nutrition System V2

## 1. Project Overview

The **Personalized Nutrition System V2** is a Full-Stack AI Healthcare Application that creates customized diet plans based on biological data extracted from blood reports.

**Problem Solved:**
Most diet apps provide generic suggestions (e.g., "Eat less carbs"). They lack **biological context**. This project bridges that gap by directly analyzing a user's blood report (Hemoglobin, Cholesterol, Glucose, etc.) to detect specific deficiencies and recommend foods that scientifically address those biological needs.

**End-to-End Workflow:**
1.  **User Registration**: User enters details and MUST upload a blood report (PDF/Image).
2.  **Preprocessing**: The report is converted to high-resolution images.
3.  **OCR Extraction**: Tesseract OCR reads the text, and Regex parsers search for clinical keywords.
4.  **Data Cleaning**: Extracted values are validated against medical ranges.
5.  **Health Prediction**: A machine learning model (Random Forest) classifies the user as *Normal*, *At Risk*, or *Critical*.
6.  **Diet Generation**: A second ML model predicts the optimal food items based on the health profile.
7.  **Report Delivery**: A reusable PDF report is generated containing visual charts and a 7-day meal plan.

---

## 2. Installation & Setup

### Environment
- **Python Version**: 3.8+
- **Virtual Environment**: Recommended to isolate dependencies.

### Dependencies
**OCR Engine**:
- **Tesseract 5.x**: Must be installed on the OS.
    - Windows: [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
    - Path: Add `C:\Program Files\Tesseract-OCR` to System PATH.

**Python Libraries**:
```bash
pip install flask              # Web Framework
pip install pandas numpy       # Data Manipulation
pip install scikit-learn       # Machine Learning
pip install xgboost            # Advanced ML Model
pip install pytesseract        # OCR Wrapper
pip install pdf2image          # PDF Conversion
pip install pypdfium2          # PDF Rendering (Alternative)
pip install reportlab          # PDF Generation
pip install opencv-python-headless # Image Processing
pip install matplotlib         # Chart Generation
```

### Database
- **JSON Store**: The current version uses a flat-file JSON database (`version2/user_data_store.json`) to simulate a NoSQL structure (MongoDB). No external installation required for MVP.

---

## 3. Folder Structure

```
/version2
├── app.py                      # CONTROLLER: Main Flask Application
├── database.py                 # MODEL: JSON Database Interface
├── ocr_fix_v2.py               # UTILS: OCR & Regex Extraction Logic
├── data_preprocessing_v2.py    # UTILS: Data Cleaning & Feature Engineering
├── model_training_health_v2.py # ML: Script to Train Health Classifier
├── model_training_diet_v2.py   # ML: Script to Train Diet Recommender
├── model_inference_health_v2.py# ML: Inference Wrapper for Health
├── model_inference_diet_v2.py  # ML: Inference Wrapper for Diet
├── chart_generator_v2.py       # VISUALIZATION: Matplotlib Chart Helpers
├── pdf_generator_v2.py         # VISUALIZATION: PDF Report Builder
├── expert_advice_v2.py         # CHATBOT: Simple Rule-Based Expert
└── README.md                   # DOCUMENTATION

/static
├── css/                        # Stylesheets
├── js/                         # Frontend Scripts
└── img/                        # Assets

/templates                      # HTML Views (Jinja2)
/models                         # Serialized .pkl Model Files
```

---

## 4. Module-by-Module Explanation

### **app.py**
**Purpose**: The central entry point. Orchestrates the flow between Frontend, OCR, ML, and Database.
**Key Function**: `upload_report()`
**Code Snippet**:
```python
@app.route('/upload', methods=['POST'])
def upload_report():
    file = request.files['report']
    # 1. Save File
    file.save(path)
    # 2. Extract Data (OCR)
    lab_data = extract_blood_report_text_v2(path)
    # 3. Predict Health
    status = predict_health_status(lab_data)
    # 4. Generate Diet
    diet = generate_v2_diet_plan(lab_data)
    # 5. Render
    return render_template('report.html', ...)
```
**Explanation**: This function accepts the POST request, triggers the entire V2 pipeline synchronously, and returns the results to the user.

### **ocr_fix_v2.py**
**Purpose**: Converts unstructured documents (PDF/Img) into structured JSON data.
**Imports**:
- `pytesseract`: To execute OCR.
- `re`: standard Python regex for pattern matching.
- `cv2`: For image preprocessing (grayscale/thresholding).
**Key Function**: `parse_lab_values_v2(text)`
- Uses strict regex patterns like `r'hemoglobin\s*[:=]?\s*(\d+\.?\d*)'` to capture values.
- **Why**: Medical reports differ in layout; regex is more robust than positional extraction.

### **model_training_health_v2.py**
**Purpose**: Trains the supervised classification model for health status.
**Input**: `lab_clean_processed.csv`
**Output**: `health_model_v2.pkl`
**Code Logic**:
1. Load CSV.
2. Impute missing values with Median.
3. Train **Random Forest Classifier**.
4. Save model using `joblib`.

### **pdf_generator_v2.py**
**Purpose**: Creates the downloadable PDF.
**Library**: `reportlab`.
**Logic**: Uses a "Canvas" to draw strings and images at specific (x, y) coordinates. Creates tables for the Diet Plan to ensure perfect alignment.

---

## 5. Input Flow

1. **User**: Registers or uploads `my_report.pdf`.
2. **System - Preprocessing**:
   - `pdf2image` converts PDF pages to high-res images (300 DPI).
   - `cv2` converts images to Grayscale to remove color noise.
3. **System - Extraction**:
   - Tesseract extracts raw text strings.
   - Regex engine searches for keywords (`Hemoglobin`, `Granulocytes`, etc.).
   - Found values are cast to `float`.
4. **System - Validation**:
   - Extracted `Hemoglobin: 95.0` -> **Rejected** (Clinically impossible).
   - Extracted `Hemoglobin: 14.2` -> **Accepted**.
5. **System - Model Input**:
   - Valid data is combined with User Profile (Age 25, Male).
   - Input Vector: `[25, 1, 14.2, 95.0, ...]` -> Logic Unit.

---

## 6. ML Pipelines

### **A. Health Prediction Model**

**Goal**: Classify user as Normal, Risk, or Warning.
**Dataset**: `lab_clean_processed.csv` (Public Medical Data).
**Comparison of Algorithms**:

| Algorithm | Accuracy | F1-Score | Remarks |
|-----------|----------|----------|---------|
| Logistic Regression | 74.7% | 0.74 | Low non-linear capability. |
| **Random Forest** | **99.9%** | **0.99** | **Selected**. Best performance and interpretability. |
| XGBoost | 99.8% | 0.99 | Competitive but slightly heavier. |

**Selected Model**: **Random Forest**
- **Why**: It handles the tabular nature of medical data excellently and provides feature importance (explaining *which* biomarker caused the risk).

---

### **B. Diet Recommendation Model**

**Goal**: Recommend specific food items.
**Dataset**: Synthetic Rules based on *Common Foods* + *Nutrient Profiles*.
**Comparison of Algorithms**:

| Algorithm | Accuracy | Remarks |
|-----------|----------|---------|
| KNN | 88.0% | Good for finding similarity, but slower at scale. |
| **Random Forest** | **95.0%** | **Selected**. Effectively learns the rules (Label = Food Item). |

**Selected Model**: **Random Forest Classifier** (Trained on Synthetic Diet Data)
- **Why**: Since our training data is generated based on strict nutritional rules (e.g., "If Weight Loss -> Recommend High Protein/Low Calorie"), Decision Tree-based ensembles like RF learn these mappings almost perfectly.

---

## 7. Database

**Schema** (JSON Document Structure):
```json
{
  "users": {
    "user@example.com": { "name": "DeepMind User", "age": 25, "gender": 1 }
  },
  "reports": {
    "uuid_1234": {
      "user_email": "user@example.com",
      "timestamp": "2024-01-01 10:00",
      "lab_results": { "hemoglobin": 14.5, "glucose": 98 },
      "health_status": "Normal",
      "diet_plan": { "Monday": { "Breakfast": "Oatmeal" } }
    }
  }
}
```
**Storage Logic**:
- Reports are linked by `user_email`.
- This allows a "History" view where we filter `reports` by the logged-in user's email.

---

## 8. PDF Generation

- **Library**: `reportlab`.
- **Logic**:
  1. **Header**: Draws Logo and User Name.
  2. **Charts**: Inserts temporary Base64 images generated by Matplotlib.
  3. **Tables**: Uses `reportlab.platypus.Table` for the 7-Day Diet Plan.
  4. **Dynamic Data**: Iterate through the JSON diet plan to fill the table cells.

---

## 9. Chatbot Module

- **Type**: Expert System (Rule-Based + Keyword Matching).
- **Files**: `expert_advice_v2.py`.
- **Logic**:
  - Checks query for keywords: "diabetes", "weight loss", "protein".
  - Returns pre-curated medical advice strings.
  - Future scope: Integrate LLM (Gemini/OpenAI) via API.

---

## 10. Execution

**Commands**:
1. **Activate Environment**: `venv\Scripts\activate`
2. **Run Application**: `python version2/app.py`
3. **Open Browser**: Navigate to `http://localhost:5002`.
4. **Test**:
   - Click "Register".
   - Upload `sample_pdf/muralibloodrep.pdf`.
   - Submit.
   - View Dashboard.
   - Click "Download PDF".

---

## 11. Error Handling

- **Image Noise**: Code applies Gaussian Blur before OCR to reduce speckles.
- **Empty OCR**: If Tesseract returns nothing, code falls back to `pypdfium2` text extraction.
- **Missing Values**: Code keeps the UI functioning even if only partial biomarkers are found (e.g., calculates status based on available data).
