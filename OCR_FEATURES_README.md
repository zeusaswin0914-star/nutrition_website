# Advanced Blood Report Features - Documentation

## Overview

The Personalized Nutrition Flask app now includes advanced features for analyzing blood reports using OCR technology, generating personalized AI recommendations, tracking progress, and creating downloadable PDF reports.

## New Features

### 1. **OCR Text Extraction from Blood Reports**
**Module:** `ocr_helper.py`

Automatically extracts text from blood report PDFs and images using:
- **pytesseract**: For standard OCR text extraction from images
- **pdfplumber**: For PDF text extraction (if available)
- **opencv**: For image processing and enhancement

**Key Functions:**
- `extract_blood_report_text(file_path)` - Extracts text from PDF, PNG, or JPG files
- `parse_lab_values(extracted_text)` - Parses common lab values from extracted text using regex patterns
- `get_lab_value_ranges(age_category)` - Returns age-appropriate normal ranges for lab tests
- `assess_lab_values(lab_values, age_category)` - Compares lab values against normal ranges

**Supported Lab Tests:**
- Hemoglobin (Hb/HGB)
- Hematocrit (Hct)
- Iron (Fe)
- Ferritin
- Vitamin D
- Calcium (Ca)
- Phosphorus (P)
- Fasting Glucose
- Total Cholesterol
- LDL/HDL Cholesterol
- Triglycerides
- Albumin
- Total Protein
- BMI

### 2. **AI-Powered Personalized Recommendations**
**Module:** `recommendation_engine.py`

Generates personalized nutrition recommendations based on detected lab value abnormalities.

**Key Functions:**
- `get_recommendations_for_assessment(assessments, age_category, health_conditions)` - Main recommendation generator
- `get_age_specific_guidance(age_category)` - Returns age-specific nutrition guidance
- `get_general_nutrition_tips(age_category)` - Returns general wellness tips
- `generate_meal_plan_recommendation(recommendations, age_category)` - Creates sample meal plans

**Recommendation Categories:**
- **Low Values:** Foods and supplements to increase deficient nutrients
- **High Values:** Foods to reduce excessive levels (e.g., cholesterol, glucose)
- **Age-Specific Guidance:** Tailored advice for toddlers, children, teens, adults, and seniors
- **Meal Plans:** Sample meal schedules with recommended foods

### 3. **PDF Report Generation**
**Module:** `pdf_generator.py`

Creates professional, downloadable PDF reports with:
- User information and test date
- Lab assessment table with normal ranges and status
- Personalized recommendations with foods and supplements
- Age-specific guidance
- General nutrition tips
- Professional disclaimer

**Key Function:**
- `generate_pdf_report(user_name, age_category, assessments, recommendations, health_conditions, output_path)` - Generates PDF file

### 4. **Progress Tracking**
**Route:** `/progress`
**Template:** `progress_tracking.html`

Displays:
- Timeline of all uploaded blood reports
- Lab values found in each report
- Number of concerns (abnormal values)
- Comparison view to track improvements over time
- Tips for using progress tracking effectively

### 5. **Blood Report Analysis Interface**
**Routes:**
- `POST /check-blood-report` - Upload and analyze blood report
- `GET /blood-report/view` - View analysis results
- `GET /blood-report/download/<filename>` - Download PDF report

**Template:** `blood_report_result.html`

Displays:
- Extracted text from blood report
- Detected lab values
- Lab assessment against age-appropriate ranges
- Personalized recommendations by test
- Age-specific guidance
- Downloadable PDF report link

## Updated Flask Routes

### New Routes Added to `app.py`

```python
# Upload and analyze blood report (OCR + AI recommendations + PDF)
POST /check-blood-report
- Input: person_name, age_category, health_conditions, blood_report (file)
- Output: Redirects to /blood-report/view with full analysis

# View blood report analysis results
GET /blood-report/view
- Returns: blood_report_result.html with extracted data, assessments, recommendations

# Download generated PDF report
GET /blood-report/download/<filename>
- Returns: PDF file for download

# Progress tracking dashboard
GET /progress
- Returns: progress_tracking.html showing all blood report history
```

## Usage Workflow

### Step 1: Upload Blood Report
1. Navigate to "Analyze Report" in the main menu
2. Enter person's name
3. Select age category (Toddler, Child, Teen, Adult, Senior)
4. (Optional) Enter any health conditions
5. Upload blood report (PDF, PNG, or JPG)
6. Click "Analyze"

### Step 2: System Processing
1. OCR extracts text from blood report
2. Lab values are parsed from extracted text
3. Values are compared against age-appropriate normal ranges
4. AI generates personalized nutrition recommendations
5. PDF report is generated automatically

### Step 3: Review Results
1. View extracted text and detected lab values
2. See assessment table (Normal/Low/High status)
3. Read personalized recommendations for each abnormal value
4. View age-specific guidance
5. Download PDF report for sharing with healthcare provider

### Step 4: Track Progress
1. View all submitted blood reports in "Progress" section
2. Compare lab values over time
3. Monitor improvements in nutritional status
4. Download historical reports as needed

## Age Categories and Normal Ranges

### Toddler (1-3 years)
- Hemoglobin: 10.5-13.5 g/dL
- Hematocrit: 33-39%
- Iron: 30-100 µg/dL
- Calcium: 8.5-10.2 mg/dL
- Glucose: 70-100 mg/dL

### Child (4-8 years)
- Hemoglobin: 11.5-15.5 g/dL
- Hematocrit: 35-45%
- Iron: 40-100 µg/dL
- Calcium: 8.5-10.2 mg/dL
- Glucose: 70-100 mg/dL

### Teen (9-18 years)
- Hemoglobin: 12.0-16.0 g/dL
- Hematocrit: 36-46%
- Iron: 50-120 µg/dL
- Calcium: 8.5-10.2 mg/dL
- Glucose: 70-100 mg/dL

### Adult (19-65 years)
- Hemoglobin: 13.5-17.5 g/dL (males)
- Hematocrit: 41-53%
- Iron: 60-170 µg/dL
- Ferritin: 30-300 ng/mL
- Vitamin D: 30-100 ng/mL
- Calcium: 8.5-10.2 mg/dL
- Glucose: 70-100 mg/dL
- Total Cholesterol: <200 mg/dL
- LDL: <100 mg/dL
- HDL: >40 mg/dL
- Triglycerides: <150 mg/dL
- Albumin: 3.5-5.5 g/dL

### Senior (65+ years)
- Hemoglobin: 12.0-17.5 g/dL
- Hematocrit: 36-50%
- Iron: 40-170 µg/dL
- Ferritin: 30-400 ng/mL
- Vitamin D: 30-100 ng/mL
- Calcium: 8.5-10.2 mg/dL
- Glucose: 70-100 mg/dL
- Total Cholesterol: <200 mg/dL
- LDL: <100 mg/dL
- HDL: >40 mg/dL
- Triglycerides: <150 mg/dL
- Albumin: 3.5-5.5 g/dL

## Dependencies

The following Python packages are required for the new features:

```
pytesseract==0.3.10        # OCR text extraction
opencv-python==4.9.0.80     # Image processing
easyocr==1.7.2              # Alternative OCR for handwritten text
pdfplumber==0.9.0           # PDF text extraction (optional)
pdf2image==1.16.0           # PDF to image conversion (optional)
reportlab==3.5.68           # PDF report generation
Pillow==9.5.0               # Image processing
```

All are already in `requirements.txt`.

## Installation & Setup

### Prerequisites
- Python 3.10+
- Tesseract OCR engine (for pytesseract)

### Install Tesseract (Windows)
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location: `C:\Program Files\Tesseract-OCR`
3. No additional configuration needed

### Install Tesseract (macOS)
```bash
brew install tesseract
```

### Install Tesseract (Linux - Ubuntu/Debian)
```bash
sudo apt-get install tesseract-ocr
```

### Python Package Installation
```bash
pip install -r requirements.txt
```

## File Structure

```
project/
├── app.py                           # Main Flask app (updated)
├── ocr_helper.py                   # OCR text extraction module (NEW)
├── recommendation_engine.py         # AI recommendations module (NEW)
├── pdf_generator.py                # PDF report generation (NEW)
├── templates/
│   ├── base.html                   # Navigation updated
│   ├── blood_report_result.html    # Results page (NEW)
│   ├── progress_tracking.html      # Progress dashboard (NEW)
│   └── ... (other templates)
├── uploads/                        # Blood reports and PDFs stored here
└── requirements.txt                # Dependencies
```

## API Integration Points

### Flask Routes Integration

The new modules are integrated into Flask routes:

```python
# In app.py
from ocr_helper import extract_blood_report_text, parse_lab_values, assess_lab_values
from recommendation_engine import get_recommendations_for_assessment
from pdf_generator import generate_pdf_report

# In /check-blood-report route
extracted_text = extract_blood_report_text(save_path)
lab_values = parse_lab_values(extracted_text)
assessments = assess_lab_values(lab_values, age_category)
recommendations = get_recommendations_for_assessment(assessments, age_category, health_conditions)
generate_pdf_report(person_name, age_category, assessments, recommendations, health_conditions, pdf_path)
```

## Error Handling

The system includes graceful error handling:
- If OCR fails: Falls back to manual text input or displays "No text extracted" message
- If lab parsing fails: Shows available extracted text for manual review
- If PDF generation fails: User can still view web-based report
- If database unavailable: Uses in-memory fallback (graceful degradation)

## Testing

### Quick Test
```bash
python app.py
# Navigate to http://127.0.0.1:5000/check-blood-report
# Upload a blood report image/PDF
```

### Test OCR Extraction Directly
```python
from ocr_helper import extract_blood_report_text, parse_lab_values
text = extract_blood_report_text("path/to/report.pdf")
values = parse_lab_values(text)
print(values)
```

## Limitations & Future Improvements

### Current Limitations
1. OCR accuracy depends on blood report image quality
2. Lab value parsing uses regex patterns (may miss non-standard formatting)
3. Recommendations are template-based (not ML-based)
4. No user authentication for progress tracking (demo mode)

### Potential Improvements
1. **Advanced ML:** Train ML model on actual lab reports for better parsing
2. **Image Enhancement:** Auto-enhance low-quality report images before OCR
3. **Handwriting Recognition:** Better support for handwritten lab values
4. **Deep Learning Recommendations:** Use LLM for more personalized advice
5. **Multi-language Support:** Support blood reports in multiple languages
6. **User Accounts:** Persistent user accounts with personal progress history
7. **Integration with EHR:** Connect to electronic health records systems
8. **API Export:** REST API for third-party integrations

## Security Notes

1. **File Upload:** Uses `secure_filename()` to prevent path traversal attacks
2. **File Storage:** Uploads stored in separate `uploads/` directory
3. **Database:** Graceful fallback if MongoDB unavailable
4. **PDF Download:** Validates report ownership before download

## Support & Troubleshooting

### OCR Not Working
- Ensure Tesseract is installed and in PATH
- Check blood report image quality
- Try alternative file format (PNG vs PDF)

### Lab Values Not Detected
- Check extracted text for expected values
- Verify lab report format matches expected patterns
- Consider adding custom regex patterns to `ocr_helper.py`

### PDF Generation Fails
- Ensure `uploads/` directory has write permissions
- Check disk space available
- Verify reportlab is correctly installed

## Contributing

To add support for additional lab tests:
1. Add regex pattern to `parse_lab_values()` in `ocr_helper.py`
2. Add normal ranges to age categories in `get_lab_value_ranges()`
3. Add recommendations to `get_recommendations_for_assessment()` in `recommendation_engine.py`

## License

This project is for educational purposes. Not medical advice.
Always consult with qualified healthcare professionals for medical guidance.
