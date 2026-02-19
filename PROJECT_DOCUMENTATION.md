# Personalized Nutrition Generator from Blood Report
## Project Documentation

---

## 1. Technologies Used

### Frontend
- **HTML5/CSS3**: Used for structure and styling. Minimalistic, professional design with responsive layouts.
- **Jinja2 Templating**: Integrated with Flask to dynamically render data (user profiles, report results) directly into HTML pages.

### Backend
- **Python (Flask)**: The core web framework. It handles routing, file uploads, session management, and orchestrates the connection between OCR, ML models, and the database.
- **Werkzeug**: Used for secure file handling and password hashing (if applicable).

### Machine Learning
- **Scikit-Learn**: Used for data preprocessing (StandardScaler, LabelEncoder) and training baseline models (Logistic Regression, Random Forest, KNN).
- **XGBoost**: Advanced gradient boosting algorithm used for high-accuracy health classification and diet recommendation.
- **Joblib**: For serializing and saving trained models (`.pkl` files) to disk for efficient inference.

### OCR (Optical Character Recognition)
- **Tesseract (pytesseract)**: The primary engine for extracting text from images.
- **PDFPlumber**: Exact text extraction from digitally generated PDFs.
- **pdf2image / pypdfium2**: Converts PDF pages to images for Tesseract processing when direct text extraction fails.
- **OpenCV & PIL**: Used for image preprocessing (grayscale conversion, noise reduction) to improve OCR accuracy.

### Database
- **MongoDB (PyMongo)**: A NoSQL database chosen for its flexibility in storing unstructured data like JSON-based health reports and user profiles.

### Visualization & Reporting
- **Matplotlib**: Generates static charts (bar charts, pie charts) for the PDF report.
- **ReportLab**: A powerful library for programmatically generating high-quality PDF reports containing text, tables, and images.

---

## 2. System Architecture

The system follows a modular Monolithic architecture where the Flask backend serves as the central controller.

### Component Flow
```
[ User ]
   │
   ▼
[ Frontend Interface ] (HTML/CSS)
   │
   ▼
[ Flask Backend ] ◄───► [ MongoDB Database ]
   │    │
   │    ├──► [ OCR Module ] (Extracts Text from PDF/Image)
   │    │
   │    ├──► [ ML Engine ] (Predicts Health Status & Diet)
   │    │
   │    └──► [ Report Generator ] (Creates PDF with Charts)
   │
   ▼
[ Final Output ] (Web Dashboard + PDF Download)
```

---

## 3. Project Structure

```
project/
├── version2/                  # Core Application Code (V2)
│   ├── app.py                 # Main Flask Application
│   ├── mongo_helper.py        # Database Interface
│   ├── ocr_fix_v2.py          # OCR Logic & Preprocessing
│   ├── model_training_v2.py   # Master Training Script
│   ├── model_inference_v2.py  # Inference Logic
│   ├── pdf_generator_v2.py    # PDF Creation Logic
│   ├── chart_generator_v2.py  # Visualization Utilities
│   └── models/ (*.pkl)        # Saved ML Models
├── templates/                 # HTML Files (UI)
│   ├── index.html             # Landing Page
│   ├── login.html             # Auth Pages
│   ├── report.html            # Results Dashboard
│   └── ...
├── static/                    # CSS, JS, Images
├── uploads/                   # Temp storage for uploaded reports
├── datasets/                  # Raw CSV Data for Training
└── README.md                  # Quick Start Guide
```

---

## 4. Workflow

1.  **Registration**: User signs up with basic details (Age, Gender, Weight, Height, Goal).
2.  **Report Upload**: User uploads a blood test report (PDF/Image).
3.  **OCR Extraction**: System preprocesses the file and extracts clinical text using Tesseract/Regex.
4.  **Validation**: Extracted biomarkers (e.g., Hemoglobin, Glucose) are validated against realistic usage ranges.
5.  **Health Prediction**: ML model analyzes the biomarkers to classify health status (Normal, At Risk, Action Needed).
6.  **Diet Generation**: A secondary model recommends a 7-day diet plan based on the user's goal (Weight Loss, Gain), type (Veg/Non-Veg), and health status.
7.  **Visualization**: Charts comparing user values vs. normal ranges are generated on the fly.
8.  **PDF Creation**: A comprehensive PDF is compiled with all findings.
9.  **Storage**: Extracted data and report paths are stored in MongoDB.
10. **Display**: User is redirected to a dashboard to view the analysis and download the PDF.

---

## 5. Machine Learning Models

### MODEL 1 – Health Classification
-   **Goal**: Predict overall health status based on biomarkers.
-   **Algorithms Evaluated**: Logistic Regression, Random Forest, Gradient Boosting, XGBoost.
-   **Training Pipeline**:
    1.  Load data (`processed_data_v2.csv`).
    2.  Scale features using `StandardScaler`.
    3.  Train/Test Split (80/20).
    4.  Evaluate all models.
-   **Best Model**: **XGBoost** (typically chosen for highest accuracy and F1-score on tabular data).
-   **Metrics**: Accuracy, F1-Score (Weighted).

### MODEL 2 – Diet Recommendation
-   **Goal**: Recommend food items based on user profile (BMI, Goal, Diet Preference).
-   **Approach**: Multi-label classification or Multi-output classification.
-   **Dataset**: Custom/Synthetic dataset mapping nutritional profiles to health goals.
-   **Algorithms**: Random Forest, KNN, XGBoost.
-   **Evaluation**: Accuracy in matching food items to specific health goals.

---

## 6. Datasets

1.  **`lab_clean_processed.csv`**:
    *   **Source**: Aggregated real-world lab data (anonymized) / NHANES derivatives.
    *   **Features**: Age, Gender, Glucose, Cholesterol, Hemoglobin, etc.
    *   **Purpose**: Training the Health Classification Model.

2.  **`nhanes_real_with_calories.csv`**:
    *   **Source**: NHANES (National Health and Nutrition Examination Survey).
    *   **Features**: Detailed nutritional intake data linked to health markers.
    *   **Purpose**: Correlation analysis and auxiliary training.

3.  **`diet_dataset.csv`**:
    *   **Source**: Curated/Synthetic dataset.
    *   **Features**: Food items, Calories, Macros (Protein/Fat/Carbs), Suitability (Weight Loss/Gain).
    *   **Purpose**: Training the Diet Recommendation Engine.

---

## 7. OCR Module

### Challenges Faced
-   **Noise**: Scanned images often have dots/lines that confuse Tesseract.
-   **Skew**: Rotated pages lead to gibberish output.
-   **Formats**: Handling both PDFs (digital/scanned) and Images.

### Solutions
-   **Preprocessing**: `cv2.cvtColor` (Grayscale) to reduce noise complexity.
-   **Libraries**:
    -   `pdfplumber` for digital PDFs (fast, 100% accurate).
    -   `pdf2image` + `pytesseract` for scanned documents.
-   **Regex**: Custom regular expressions (e.g., `r'h[ae]moglobin\s*[:=]?\s*(\d+\.?\d*)'`) used to robustly capture values even if text surrounding it is messy.
-   **Validation**: Values outside physiological ranges (e.g., Hemoglobin > 25) are flagged or discarded.

---

## 8. Database Design (MongoDB)

**Database Name**: `nutrition_app_v2`

### Collections

**1. `users`**
*   Stores profile info.
*   **Fields**: `_id`, `name`, `email`, `age`, `gender`, `height`, `weight`, `goal`, `diet_type`.

**2. `reports`**
*   Stores analysis history.
*   **Fields**:
    -   `_id`: Report ID.
    -   `user_email`: Foreign Key link.
    -   `lab_results`: JSON object `{ 'hemoglobin': 14, ... }`.
    -   `health_status`: String (e.g., "At Risk").
    -   `diet_plan`: 7-day JSON structure.
    -   `pdf_path`: Link to generated PDF.
    -   `timestamp`: Creation time.

---

## 9. PDF Generation

The `reportlab` library constructs the PDF layer by layer:
1.  **Header**: "Personalized Nutrition Report" with Date.
2.  **Patient Details**: Table with Name, Age, BMI, Goal.
3.  **Health Summary**: Color-coded status (Green/Orange/Red) and a list of identified deficiencies.
4.  **Visuals**: Embedded Matplotlib charts (Macros Pie Chart, Health Bar Chart).
5.  **Diet Chart**: A structured 7-day meal table (Breakfast, Lunch, Snack, Dinner).
6.  **Footer**: Medical Disclaimer.

---

## 10. Visualization

-   **Pie Chart**: Macronutrient breakdown (Protein vs. Carbs vs. Fat). Visualizes the diet composition.
-   **Bar/Status Chart**: Visualizes where the user's specific lab values fall compared to the "Normal Range".
-   **Why?**: Makes complex medical data instantly understandable for a layman.

---

## 11. Execution Commands

### Prerequisites
-   Python 3.8+
-   MongoDB (Running on default port `27017`)
-   Tesseract OCR installed on system path.

### Setup
```bash
# 1. Create Environment
python -m venv env
source env/bin/activate  # or env\Scripts\activate on Windows

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Verify Database
# Ensure 'mongod' is running
```

### Running the App
```bash
# Start Backend
python version2/app.py
```
Access at `http://localhost:5002`.

### Training Models (Optional)
```bash
python version2/model_training_v2.py
```

---

## 12. Troubleshooting

| Issue | Logic/Fix |
| :--- | :--- |
| **OCR returns empty text** | Ensure Poppler and Tesseract are added to System PATH. Check if PDF is encrypted. |
| **MongoDB Connection Fail** | Check if `mongod` service is started. default URI `mongodb://localhost:27017/`. |
| **ModuleNotFoundError** | Run `pip install -r requirements.txt` and ensure you are in the virtual environment. |
| **XGBoost Error** | On some Windows systems, requires Visual C++ Redistributable. |
| **PDF Generation Error** | Ensure write permissions on `uploads/` folder for saving temporary files. |

---

## 13. System Flowchart

[ User ] -> [ Upload Report ]
                 |
                 v
            [ OCR Engine ]
                 |
         (Extracted Text)
                 v
      [ Data Parsing & Validation ]
                 |
                 v
      [ ML Models (Health + Diet) ]
                 |
                 v
       [ Result Generation ]
      /          |          \
 [ MongoDB ] [ PDF Gen ] [ Web UI ]

---

## 14. Future Scope

1.  **Mobile Application**: Convert the web app to React Native/Flutter for easier access.
2.  **Doctor Integration**: Allow doctors to verify reports and add manual comments.
3.  **Real-Time Monitoring**: Connect with wearables (Fitbit/Apple Watch) for dynamic health tracking.
4.  **Multi-Language Support**: Support reports in local languages using Google Translate API.
5.  **Subscription Model**: Premium features like detailed meal recipes and grocery lists.

---
*Generated by Antigravity Agent*
