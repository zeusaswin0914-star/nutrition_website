# System Architecture - Personalized Nutrition System V2

## 1. High-Level Architecture

The system utilizes a **Layered Monolithic Architecture** centered around a Flask Application Server. It integrates distinct subsystems for Vision (OCR), Intelligence (ML), and Reporting (PDF).

### Core Components:
1.  **Presentation Layer (Frontend)**: HTML5/CSS3 templates rendered by Jinja2.
2.  **Application Layer (Backend)**: Flask (Python) handling routing, business logic, and security.
3.  **Data Processing Layer**: Tesseract OCR & Pandas for ETL (Extract, Transform, Load).
4.  **Intelligence Layer**: Scikit-Learn Models for decision making.
5.  **Persistence Layer**: JSON Document Store.

---

## 2. Complete Project Flow Diagram

```ascii
      [ User ]
         ↓
    (Web Interface)
         ↓
  [ Frontend Form ] --> (Validation)
         ↓
 [ Flask Controller ]
         ↓
 +-------+----------------------------------+
 | 1. FILE UPLOAD HANDLING                 |
 |   - Save PDF to /uploads                |
 |   - Convert PDF to Image (pdf2image)    |
 +-------+----------------------------------+
         ↓
 +-------+----------------------------------+
 | 2. OCR & EXTRACTION                     |
 |   - Tesseract extracts text             |
 |   - Regex parses "Hemoglobin: 14.2"     |
 |   - Range Checker validates values      |
 +-------+----------------------------------+
         ↓
 +-------+----------------------------------+
 | 3. INTELLIGENCE (ML)                    |
 |   - Health Model (Random Forest)        |
 |     -> Predicted Status: "Normal"       |
 |   - Diet Model (Random Forest)          |
 |     -> Recommended: "High Protein"      |
 +-------+----------------------------------+
         ↓
 +-------+----------------------------------+
 | 4. REPORT GENERATION                    |
 |   - Charts created (Matplotlib)         |
 |   - PDF built (ReportLab)               |
 +-------+----------------------------------+
         ↓
 [ Database ] <--- (Save Report & User)
         ↓
 [ User Profile View ]
```

---

## 3. Block Diagram

```ascii
                    [ User Device ]
                          |
                          v
                 [ Frontend (HTML/JS) ]
                          |
                          v
              +-----------+-----------+
              |     Flask Backend     |
              +-----------+-----------+
                          |
        +-----------------+-----------------+
        |                                   |
        v                                   v
+-------+-------+                   +-------+-------+
|   OCR Module  |                   |   ML Engine   |
| (Tesseract)   |                   | (Sklearn/XGB) |
+-------+-------+                   +-------+-------+
        |                                   |
        v                                   v
+-------+-------+                   +-------+-------+
|  Preprocessing|                   |  PDF Engine   |
| (CV2/Pandas)  |                   |  (ReportLab)  |
+-------+-------+                   +-------+-------+
        |                                   |
        +-----------------+-----------------+
                          |
                          v
                 [ Database (JSON) ]
```

**Block Explanation**:
- **OCR Module**: The "eyes" of the system. Reads raw pixels/text.
- **Preprocessing**: Cleaning unit. Ensures "14.2 mg/dL" becomes float `14.2`.
- **ML Engine**: The "brain". Decisions are made here (Health Checks, Diet Selection).
- **PDF Engine**: The "printer". Formats decisions into a human-readable document.

---

## 4. Model Architecture

### A. Health Prediction Model
- **Input Features**: Age (int), Gender (binary), Hemoglobin (float), Glucose (float), Total Cholesterol (float), BMI (float).
- **Preprocessing Pipeline**: 
    1. **Imputation**: Fill missing values with column median.
    2. **Scaling**: StandardScaler (Mean=0, Var=1) to normalize different units.
- **Classifier**: **Random Forest** (n_estimators=100).
- **Cross-Validation**: 5-Fold CV used during training to ensure robustness.

### B. Diet Recommendation Model
- **Input Features**: `[Age, Gender, BMI, Diet_Type(Encoded), Goal(Encoded)]`.
- **Target**: `Food_Item_Name`.
- **Architecture**: A multi-class Classifier that maps a user's biological profile to the most statistically probable suitable food item from the training set.

---

## 5. Datasets

### 1. `lab_clean_processed.csv` (Medical Data)
- **Rows**: ~2000
- **Columns**: 8 (Gender, Age, Hb, PCV, RBC, MCV, WBC, Platelet).
- **Purpose**: Ground truth for teaching the Health Model what a "Healthy" vs "Unhealthy" blood report looks like.
- **Preprocessing**: Removed duplicates, handled outliers > 3 Z-score.

### 2. `nhanes_real_with_calories.csv` (Nutrition Data)
- **Rows**: ~7000+
- **Columns**: Food Name, Energy (kcal), Protein (g), Fiber (g), etc.
- **Purpose**: The "Knowledge Base" for the diet recommender.
- **Preprocessing**: Normalized Serving Sizes to 100g standard.

### 3. `diet_dataset.csv` (Synthetic Logic)
- **Rows**: 2000 (Generated via `model_training_diet_v2.py`).
- **Purpose**: Bridges the gap between generic nutrition data and specific user goals (e.g., links "High Protein" foods specifically to "Muscle Gain" goal labels).

---

## 6. Frontend-Backend Flow

1. **Route**: `/upload` [POST]
2. **Form Data**: `request.files['report']`, `request.form['age']`...
3. **Processing**: Backend calls `process_report_pipeline()`.
4. **Rendering**:
   - Backend renders `report.html`.
   - Passes variables: `health_status`, `diet_plan`, `charts`.
   - Template logic: `{% if status == 'Normal' %} <span class="green">...`

---

## 7. Security

- **File Validation**: `secure_filename()` from `werkzeug` is mandatory to prevent filesystem attacks.
- **Input Sanitization**: Numerical inputs are cast to `int/float` immediately, stripping potential SQL injection strings (though we use NoSQL-style JSON, this prevents logic errors).
- **Session Security**: Signed Cookies are used for Session management (Flask default).

---

## 8. Performance

- **Lazy Loading**: Huge ML models (`.pkl`) are loaded into memory *once* (Global Singleton) rather than per-request, reducing latency from ~2s to ~0.1s.
- **On-the-Fly Generation**: Visual charts are not saved to disk (saving IO); they are generated in RAM as Base64 strings.

---

## 9. Technology Stack

- **Python**: Universal Glue Language.
- **Flask**: Micro-framework logic.
- **Tesseract**: Best-in-class Open Source OCR.
- **Scikit-Learn**: Industry standard for tabular ML.
- **XGBoost**: High-performance gradient boosting (used for benchmark).
- **MongoDB (Simulated)**: JSON Store flexible for different report structures.

---

## 10. Final Flowchart

```ascii
      [ START ]
          ↓
  [ User Registration ]
  (Capture Name, Goal)
          ↓
 [ Upload Blood Report ]
          ↓
  [ OCR Extraction ]
  (Raw Text -> Regex)
          ↓
 [ Feature Processing ]
 (Clean, Impute, Scale)
          ↓
  [ Health Prediction ]
  (Random Forest: Normal/Risk)
          ↓
  [ Diet Recommendation ]
  (KNN/RF: Select Foods)
          ↓
  [ PDF Generation ]
  (Compile Charts & Tables)
          ↓
  [ Store in Database ]
  (History Persistence)
          ↓
       [ END ]
```
