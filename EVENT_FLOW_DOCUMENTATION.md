# Event Flow Documentation: Trigger → Source → Render

This document traces the complete user interaction flow from **click event** → **data source** → **HTML rendering** for each major user journey in the nutrition app.

---

## Overview: Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERACTION FLOW                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  TRIGGER              SOURCE                 RENDER          │
│  ↓                    ↓                       ↓              │
│ User clicks/types    Backend route          Jinja2 template  │
│ ↓                    ↓                       ↓              │
│ DOM event fires      Query/Process data     Generate HTML    │
│ ↓                    ↓                       ↓              │
│ JS event listener    Load from:             Map data to:    │
│ or form submission   • Session              • {{ }}variables │
│                      • MongoDB              • {% %} loops   │
│                      • File system          • CSS styling   │
│                      • Compute (ML model)   • Base64 images │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Flow 1: Upload Blood Report & Generate Nutrition Report

### Trigger: Form Submission
```javascript
// Location: templates/upload.html lines 38-68
// Type: Event listener on form submit

const form = document.querySelector('form');
form.addEventListener('submit', async (e) => {
  e.preventDefault();  // ← TRIGGER: Prevent default form submission
  
  const url = form.action;  // → "/upload"
  const fd = new FormData(form);  // ← Collect form data:
                                  // age, height, weight, hgb, glucose, cholesterol, report_file
  
  try {
    const resp = await fetch(url, { method: 'POST', body: fd, redirect: 'follow' });
    
    // If server redirected, navigate to new page
    if (resp.url && resp.url !== window.location.href) {
      window.location.href = resp.url;  // ← Navigate to /report/view
      return;
    }
  } catch(err) {
    alert('Upload failed: ' + err.message);
  }
});
```

**Event Details:**
- **DOM Element:** `<form method="POST" action="{{ url_for('upload_report') }}">`
- **Event Type:** `submit`
- **Trigger Condition:** User clicks "Generate Report" button
- **Data Collected:** `FormData` from all input fields + file

---

### Source: Backend Data Processing

```python
# Location: app.py lines 129-206
# Route: POST /upload

@app.route("/upload", methods=["GET","POST"])
def upload_report():
    if request.method == "POST":
        # STEP 1: Extract form data (strings → numbers)
        age = float(request.form.get("age"))
        height = float(request.form.get("height"))
        weight = float(request.form.get("weight"))
        hgb = float(request.form.get("hgb") or 0)
        glucose = float(request.form.get("glucose") or 0)
        cholesterol = float(request.form.get("cholesterol") or 0)
        
        # STEP 2: Load ML model from disk
        load_model()  # ← Loads from: calorie_model.pkl
        # Returns: (model, num_cols, medians) via joblib.load()
        
        # STEP 3: Build feature vector
        inp = {c: medians.get(c, 0) for c in num_cols}
        inp.update({'age': age, 'height': height, 'weight': weight, ...})
        user_data = np.array([[inp[c] for c in num_cols]])
        
        # STEP 4: Predict calories using model
        pred = model.predict(user_data)[0]  # ← Returns: float (e.g., 2450.5)
        
        # STEP 5: Analyze biomarkers against hard-coded ranges
        # Source: NORMAL_RANGES (global dict from nutrition_engine.py)
        lab_values = {"HGB": hgb, "SGP": glucose, "TCP": cholesterol}
        report, deficiencies = analyze_biomarkers(lab_values)
        # Returns:
        # report = ["Hemoglobin (g/dL): 12.5 is NORMAL", "Cholesterol: 185 is HIGH"]
        # deficiencies = ["TCP"]  # cholesterol is high
        
        # STEP 6: Get food recommendations
        # Source: FOOD_RECO (global dict from nutrition_engine.py)
        recs = recommend_foods(deficiencies)
        # Returns: ["Oats", "Almonds", "Avocado", ...]
        
        # STEP 7: Generate visualization charts
        # Source: matplotlib (diet_chart_generator.py)
        chart_data = {
            'calories': float(pred),
            'macros': {'carbs': 50, 'protein': 20, 'fat': 30},
            'lab_values': lab_values,
            'deficiencies': deficiencies,
            'normal_ranges': NORMAL_RANGES,  # Hard-coded global
            'food_reco': FOOD_RECO  # Hard-coded global
        }
        diet_charts = generate_complete_diet_chart(chart_data)
        # Returns: dict with 4 base64 PNG data URIs:
        # {
        #   'macronutrient_chart': 'data:image/png;base64,iVBO...',
        #   'meal_plan_chart': 'data:image/png;base64,iVBO...',
        #   'lab_status_chart': 'data:image/png;base64,iVBO...',
        #   'food_recommendation_chart': 'data:image/png;base64,iVBO...'
        # }
        
        # STEP 8: Get diet plan recommendation
        # Source: diet_plans.recommend_diet_plan() (rule-based)
        diet_recommendation = recommend_diet_plan(
            lab_values=lab_values,
            age=int(age),
            health_conditions=""
        )
        # Returns: dict {
        #   'primary': {'name': '...', 'emoji': '...', 'macros': {...}, 'benefits': [...], 'meals': {...}},
        #   'alternatives': [...]
        # }
        
        # STEP 9: Store in session (temporary, per-request)
        session['last_result'] = {
            "prediction": round(float(pred), 2),
            "report": report,
            "recommendations": recs,
            "macros": {"carbs": 50, "protein": 20, "fat": 30},
            "diet_charts": diet_charts,  # Base64 PNG URIs
            "lab_values": lab_values,
            "deficiencies": deficiencies,
            "diet_plan": diet_recommendation,
            "age": age
        }
        
        # STEP 10: Persist to MongoDB (long-term storage)
        save_prediction(inputs=inp, prediction=float(pred), report=report, recommendations=recs)
        
        # STEP 11: Redirect to display page
        return redirect(url_for('show_report'))  # ← Redirects to GET /report/view
```

**Data Sources Used:**
| Source | Type | Data |
|--------|------|------|
| `calorie_model.pkl` | File (joblib artifact) | ML model, feature names, median values |
| `NORMAL_RANGES` | Python dict (nutrition_engine.py) | Clinical reference ranges |
| `FOOD_RECO` | Python dict (nutrition_engine.py) | Food→deficiency mappings |
| `matplotlib` | Library | Chart generation (→ base64 PNG) |
| `Session storage` | Flask session | Temporary storage for this request |
| `MongoDB` | Database | Persistent predictions collection |

---

### Render: Jinja2 Template Processing

```python
# Location: app.py line 209
# After redirect from POST /upload → GET /report/view

@app.route("/report/view")
def show_report():
    r = session.get('last_result')  # ← Retrieve data from previous POST request
    
    return render_template("report.html",
        prediction=r['prediction'],              # Float: 2450.5
        report=r['report'],                      # List: ["...", "..."]
        recommendations=r['recommendations'],    # List: ["...", "..."]
        macros=r['macros'],                      # Dict: {carbs:50, protein:20, fat:30}
        diet_charts=r.get('diet_charts', {}),    # Dict: {chart_key: 'data:image/...'}
        diet_plan=r.get('diet_plan', {}),        # Dict: {primary:{...}, alternatives:[...]}
        now=datetime.now()
    )
```

**Template Rendering (report.html):**

```html
<!-- DIRECT VARIABLE BINDING -->
<div class="value">{{ prediction }} kcal</div>
<!-- Jinja2 substitutes: {{ prediction }} → 2450.5 -->
<!-- Output: <div class="value">2450.5 kcal</div> -->

<!-- LIST ITERATION -->
<h3>Lab Analysis</h3>
{% for line in report %}
  <li>{{ line }}</li>
{% endfor %}
<!-- Jinja2 loop over list, outputs one <li> per item -->
<!-- Output:
  <li>Hemoglobin (g/dL): 12.5 is NORMAL</li>
  <li>Total Cholesterol (mg/dL): 185 is HIGH</li>
-->

<!-- IMAGE EMBEDDING (Base64 data URI) -->
<div style="text-align: center;">
  {% if diet_charts['macronutrient_chart'].startswith('data:') %}
    <img src="{{ diet_charts['macronutrient_chart'] }}" style="max-width: 100%; height: auto;">
  {% endif %}
</div>
<!-- Jinja2 embeds base64 string directly in src attribute -->
<!-- Output:
  <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" style="max-width: 100%; height: auto;">
-->

<!-- NESTED DICT ACCESS + CONDITIONAL RENDERING -->
{% if diet_plan and diet_plan.get('primary') %}
  <h2 style="margin: 0 0 0.5rem 0; color: white;">
    {{ diet_plan['primary'].get('name', 'Diet Plan') }}
  </h2>
  <p style="margin: 0 0 1rem 0; opacity: 0.95;">
    {{ diet_plan['primary'].get('description', '') }}
  </p>
  
  <!-- NESTED LIST ITERATION -->
  {% for reason in diet_plan.get('reasoning', []) %}
    <li style="margin: 0.25rem 0;">{{ reason }}</li>
  {% endfor %}
  
  <!-- NESTED DICT ITERATION (meals) -->
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
    {% for meal_type, meal_desc in diet_plan['primary']['meals'].items() %}
      <div style="padding: 1rem; background-color: #f8f9fa; border-radius: 8px;">
        <p style="margin: 0 0 0.5rem 0; font-weight: bold; text-transform: capitalize;">
          {{ meal_type.replace('_', ' ') }}
        </p>
        <p style="margin: 0; color: #666; font-size: 0.9rem;">{{ meal_desc }}</p>
      </div>
    {% endfor %}
  </div>
{% endif %}
<!-- Jinja2 accesses nested dicts and iterates meals -->
<!-- Output: Grid of 4 meal cards with breakfast/lunch/dinner/snacks -->
```

**Rendering Summary:**
| Template Element | Jinja2 Method | Data Source | Output |
|---|---|---|---|
| `{{ prediction }}` | Direct substitution | Context dict | `2450.5` |
| `{% for line in report %}` | Loop over list | Context list | Multiple `<li>` elements |
| `{{ diet_charts[...] }}` | Dict key access | Base64 strings | `data:image/...` (embedded in `<img>`) |
| `{% if diet_plan %}` | Conditional rendering | Dict existence check | Show/hide block |
| `{% for meal_type, meal_desc in ... %}` | Dict iteration | Nested dict `.items()` | Multiple grid cards |

---

## Flow 2: View Progress Tracking Table

### Trigger: Link Navigation

```html
<!-- Location: profile.html or index.html -->
<a href="{{ url_for('progress') }}">📊 Progress Tracking</a>
```

**Event Details:**
- **DOM Element:** `<a>` tag
- **Event Type:** Browser link navigation (no JavaScript needed)
- **Trigger Condition:** User clicks link
- **HTTP Request:** `GET /progress`

---

### Source: MongoDB Query

```python
# Location: app.py lines 681-696

@app.route("/progress")
def progress():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    try:
        col = predictions_collection
        
        # QUERY MONGODB
        # Query: Find all documents with type = "blood_report_analysis"
        # Source: MongoDB "predictions" collection
        reports = list(col.find({"type": "blood_report_analysis"})
                        .sort("created_at", -1))  # ← Sort by date descending
        
        # TRANSFORM DATA FOR TEMPLATE
        for report in reports:
            report['created_at'] = report.get('created_at', datetime.now()).strftime("%Y-%m-%d %H:%M")
        
        return render_template("progress_tracking.html", reports=reports, now=datetime.now())
    except Exception as e:
        print(f"Failed to load progress: {e}")
        return render_template("progress_tracking.html", reports=[], now=datetime.now())
```

**Data Structure (from MongoDB):**
```python
reports = [
    {
        '_id': ObjectId('5f8a1c2e3b4e5f6a7b8c9d0a'),
        'type': 'blood_report_analysis',
        'person_name': 'John Doe',
        'age_category': 'adult',
        'health_conditions': 'Diabetes',
        'lab_values': {
            'HGB': 12.5,
            'glucose': 145,
            'cholesterol': 220,
            'triglycerides': 180
        },
        'assessments': [
            {'test': 'HGB', 'value': 12.5, 'unit': 'g/dL', 'normal_range': '12-16', 'status': 'NORMAL'},
            {'test': 'Glucose', 'value': 145, 'unit': 'mg/dL', 'normal_range': '70-100', 'status': 'HIGH'},
            {'test': 'Cholesterol', 'value': 220, 'unit': 'mg/dL', 'normal_range': '0-200', 'status': 'HIGH'}
        ],
        'recommendations_count': 5,
        'created_at': datetime(2025, 12, 14, 10, 15, 0)
    },
    {
        '_id': ObjectId('5f8a1c2e3b4e5f6a7b8c9d0b'),
        'type': 'blood_report_analysis',
        'person_name': 'Jane Smith',
        'age_category': 'senior',
        'lab_values': {...},
        'assessments': [...],
        'created_at': datetime(2025, 12, 13, 14, 22, 0)
    }
]
```

---

### Render: Jinja2 Table Generation

```html
<!-- Location: progress_tracking.html lines 35-55 -->

<table style="width: 100%; border-collapse: collapse;">
  <thead>
    <tr style="background-color: #2E5090; color: white;">
      <th style="padding: 0.75rem; text-align: left;">Person Name</th>
      <th style="padding: 0.75rem; text-align: left;">Age Category</th>
      <th style="padding: 0.75rem; text-align: center;">Lab Values Found</th>
      <th style="padding: 0.75rem; text-align: center;">Concerns</th>
      <th style="padding: 0.75rem; text-align: left;">Date</th>
    </tr>
  </thead>
  <tbody>
    <!-- LOOP: Iterate over reports list from MongoDB -->
    {% for report in reports %}
    <tr style="border: 1px solid #ddd;">
      
      <!-- CELL 1: Person name (direct binding) -->
      <td style="padding: 0.75rem; border: 1px solid #ddd;">
        <strong>{{ report.person_name }}</strong>
      </td>
      <!-- Output: <td><strong>John Doe</strong></td> -->
      
      <!-- CELL 2: Age category (filter + conditional) -->
      <td style="padding: 0.75rem; border: 1px solid #ddd;">
        <span style="background-color: #e0e0e0; padding: 0.25rem 0.5rem; border-radius: 3px;">
          {{ report.age_category.title() if report.age_category else 'N/A' }}
        </span>
      </td>
      <!-- Output: <td><span style="...">Adult</span></td> -->
      <!-- Jinja2 applies .title() filter to convert "adult" → "Adult" -->
      
      <!-- CELL 3: Lab values count (conditional display) -->
      <td style="padding: 0.75rem; text-align: center; border: 1px solid #ddd;">
        {% if report.lab_values and report.lab_values|length > 0 %}
          <span style="color: #4caf50; font-weight: bold;">
            ✓ {{ report.lab_values|length }}
          </span>
        {% else %}
          <span style="color: #999;">None</span>
        {% endif %}
      </td>
      <!-- Output (if lab_values present):
        <td><span style="color: #4caf50; font-weight: bold;">✓ 4</span></td>
      -->
      <!-- Jinja2 uses |length filter to count dict keys -->
      
      <!-- CELL 4: Concerns count (complex logic) -->
      <td style="padding: 0.75rem; text-align: center; border: 1px solid #ddd;">
        {% if report.assessments %}
          <!-- Filter assessments list to count non-NORMAL status -->
          {% set concern_count = report.assessments|selectattr('status', 'ne', 'NORMAL')|list|length %}
          {% if concern_count > 0 %}
            <span style="color: #ff9800; font-weight: bold;">
              ⚠️ {{ concern_count }}
            </span>
          {% else %}
            <span style="color: #4caf50;">✓ All Normal</span>
          {% endif %}
        {% endif %}
      </td>
      <!-- Output (if 2 concerns):
        <td><span style="color: #ff9800; font-weight: bold;">⚠️ 2</span></td>
      -->
      <!-- Jinja2:
        1. selectattr('status', 'ne', 'NORMAL') filters to non-NORMAL items
        2. |list converts filter object to list
        3. |length counts items
      -->
      
      <!-- CELL 5: Date string -->
      <td style="padding: 0.75rem; border: 1px solid #ddd;">
        {{ report.created_at }}
      </td>
      <!-- Output: <td>2025-12-14 10:15</td> -->
      <!-- Format already applied in backend with .strftime() -->
      
    </tr>
    {% endfor %}
  </tbody>
</table>
```

**Final Rendered HTML:**
```html
<table style="width: 100%; border-collapse: collapse;">
  <thead>
    <tr style="background-color: #2E5090; color: white;">
      <th>Person Name</th>
      <th>Age Category</th>
      <th>Lab Values Found</th>
      <th>Concerns</th>
      <th>Date</th>
    </tr>
  </thead>
  <tbody>
    <!-- Row 1 (from MongoDB doc) -->
    <tr style="border: 1px solid #ddd;">
      <td><strong>John Doe</strong></td>
      <td><span style="...">Adult</span></td>
      <td style="text-align: center;"><span style="color: #4caf50; font-weight: bold;">✓ 4</span></td>
      <td style="text-align: center;"><span style="color: #ff9800; font-weight: bold;">⚠️ 2</span></td>
      <td>2025-12-14 10:15</td>
    </tr>
    <!-- Row 2 (from MongoDB doc) -->
    <tr style="border: 1px solid #ddd;">
      <td><strong>Jane Smith</strong></td>
      <td><span style="...">Senior</span></td>
      <td style="text-align: center;"><span style="color: #4caf50; font-weight: bold;">✓ 5</span></td>
      <td style="text-align: center;"><span style="color: #4caf50;">✓ All Normal</span></td>
      <td>2025-12-13 14:22</td>
    </tr>
  </tbody>
</table>
```

---

## Flow 3: View Old Report from Profile

### Trigger: Link Click

```html
<!-- Location: profile.html line 116 -->
<a href="{{ url_for('view_report', report_id=r.id) }}" class="btn-ghost">View</a>
```

**Event Details:**
- **DOM Element:** `<a>` link
- **Event Type:** Browser navigation
- **Trigger Condition:** User clicks "View" button in report item
- **HTTP Request:** `GET /report/<report_id>`
- **Example URL:** `/report/5f8a1c2e3b4e5f6a7b8c9d0a`

---

### Source: MongoDB Query by ID

```python
# Location: app.py lines 403-457

@app.route('/report/<report_id>')
def view_report(report_id):
    try:
        # QUERY MONGODB BY OBJECT ID
        doc = predictions_collection.find_one({'_id': ObjectId(report_id)})
        # ↑ Converts string report_id to ObjectId for MongoDB query
        
        if not doc:
            return "Report not found", 404
        
        # EXTRACT FIELDS FROM DOCUMENT
        prediction = doc.get('prediction', 0)
        report_lines = doc.get('report', [])
        recommendations = doc.get('recommendations', [])
        macros = doc.get('macros', {'carbs':0.5,'protein':0.2,'fat':0.3})
        inputs = doc.get('inputs', {}) or {}
        
        # RECONSTRUCT LAB VALUES FROM STORED INPUTS
        hgb = _asfloat(inputs.get('hemoglobin') or inputs.get('HGB'))
        glu = _asfloat(inputs.get('fasting_glucose') or inputs.get('SGP') or inputs.get('glucose'))
        chol = _asfloat(inputs.get('total_chol') or inputs.get('TCP') or inputs.get('cholesterol'))
        lab_values = {"HGB": (hgb or 0), "SGP": (glu or 0), "TCP": (chol or 0)}
        
        try:
            # REGENERATE BIOMARKER ANALYSIS (re-analyze from stored lab values)
            report_analysis, deficiencies = analyze_biomarkers(lab_values)
            food_recs = recommend_foods(deficiencies)
            
            # REGENERATE CHARTS (matplotlib)
            chart_data = {
                'calories': float(prediction),
                'macros': macros,
                'lab_values': lab_values,
                'deficiencies': deficiencies,
                'normal_ranges': NORMAL_RANGES,
                'food_reco': FOOD_RECO
            }
            diet_charts = generate_complete_diet_chart(chart_data)
            
            # REGENERATE DIET PLAN (rule-based)
            diet_recommendation = recommend_diet_plan(
                lab_values=lab_values,
                age=int(inputs.get('age') or 30),
                health_conditions=""
            )
        except Exception as e:
            print(f"[REPORT] Failed to generate charts: {e}")
            diet_charts = {}
            diet_recommendation = {}
        
        # RENDER WITH RECONSTRUCTED DATA
        return render_template('report.html',
            prediction=prediction,
            report=report_lines,
            recommendations=recommendations,
            macros=macros,
            diet_charts=diet_charts,
            lab_values=lab_values,
            deficiencies=deficiencies,
            diet_plan=diet_recommendation,
            now=datetime.now()
        )
    except Exception as e:
        return f"Error loading report: {e}", 500
```

**Data Flow:**
```
URL Parameter: report_id (string)
    ↓
ObjectId(report_id) conversion
    ↓
MongoDB Query: find_one({'_id': ObjectId(...)})
    ↓
MongoDB Document (dict)
    ↓
Extract fields: prediction, report, recommendations, lab_values
    ↓
Regenerate derived data:
  • analyze_biomarkers(lab_values)
  • generate_complete_diet_chart({...})
  • recommend_diet_plan({...})
    ↓
Pass context to template
    ↓
Jinja2 renders (same as Flow 1)
```

---

## Flow 4: Toggle Charts Visibility (Client-Side Only)

### Trigger: Button Click

```html
<!-- Location: report.html line 126 -->
<button id="toggleChartsBtn" class="btn" style="...">
  ▼ Show Charts
</button>

<div id="chartsSection" style="display: none;">
  <!-- All chart images and descriptions -->
</div>

<script>
  // TOGGLE CHARTS VISIBILITY
  const toggleBtn = document.getElementById('toggleChartsBtn');
  const chartsSection = document.getElementById('chartsSection');
  
  toggleBtn.addEventListener('click', function() {
    const isVisible = chartsSection.style.display !== 'none';
    chartsSection.style.display = isVisible ? 'none' : 'block';
    toggleBtn.textContent = isVisible ? '▼ Show Charts' : '▲ Hide Charts';
  });
</script>
```

**Event Details:**
- **DOM Element:** `<button id="toggleChartsBtn">`
- **Event Type:** `click`
- **Trigger Condition:** User clicks button
- **No HTTP Request:** This is purely client-side DOM manipulation

**Render (JavaScript DOM Update):**
```javascript
// Initial state
chartsSection.style.display = 'none';  // Hidden
toggleBtn.textContent = '▼ Show Charts';

// After first click
chartsSection.style.display = 'block';  // Visible
toggleBtn.textContent = '▲ Hide Charts';

// After second click
chartsSection.style.display = 'none';   // Hidden again
toggleBtn.textContent = '▼ Show Charts';
```

---

## Flow 5: File Input Preview (Client-Side Only)

### Trigger: File Selection

```html
<!-- Location: upload.html lines 38-48 -->
<input id="fileInput" type="file" name="report_file" accept=".pdf,.png,.jpg,.jpeg">
<p id="fileName">No file selected</p>
<button id="uploadBtn" type="button" class="upload-btn">Choose file</button>

<script>
  // FILE PREVIEW WHEN USER SELECTS FILE
  const uploadBtn = document.getElementById('uploadBtn');
  const fileInput = document.getElementById('fileInput');
  const fileName = document.getElementById('fileName');
  
  // TRIGGER: uploadBtn click
  uploadBtn.addEventListener('click', () => fileInput.click());
  
  // TRIGGER: File selection via file dialog
  fileInput.addEventListener('change', () => {
    const f = fileInput.files[0];
    // RENDER: Update DOM with filename
    fileName.textContent = f ? f.name : 'No file selected';
  });
</script>
```

**Event Details:**
- **DOM Element:** `<input type="file">` and `<button id="uploadBtn">`
- **Event Type:** `click` (on button), `change` (on input)
- **Trigger Sequence:**
  1. User clicks "Choose file" button
  2. Browser opens file dialog
  3. User selects file and clicks "Open"
  4. `change` event fires on input element
- **No HTTP Request:** This is purely client-side DOM manipulation

**Render (JavaScript DOM Update):**
```javascript
// Initial state
fileName.textContent = 'No file selected';

// After user selects file_20251214.pdf
fileName.textContent = 'file_20251214.pdf';

// After user selects report.jpg
fileName.textContent = 'report.jpg';
```

---

## Flow 6: BMI Calculator (Client-Side Computation)

### Trigger: Button Click

```html
<!-- Location: index.html or templates/index.html -->
<div id="bmi-widget">
  <input id="bmi_height" type="number" placeholder="Height (cm)" />
  <input id="bmi_weight" type="number" placeholder="Weight (kg)" />
  <button id="bmi_calc">Calculate BMI</button>
  <div id="bmi_result"></div>
</div>

<script>
  // BMI CALCULATOR
  const bmiCalc = document.getElementById('bmi_calc');
  
  bmiCalc.addEventListener('click', () => {
    const hEl = document.getElementById('bmi_height');
    const wEl = document.getElementById('bmi_weight');
    const res = document.getElementById('bmi_result');
    
    const h = parseFloat(hEl.value);  // Get height input
    const w = parseFloat(wEl.value);  // Get weight input
    
    if(!h || !w) {
      res.textContent = 'Enter height and weight';
      return;
    }
    
    // COMPUTE: BMI = weight / (height_in_meters)^2
    const hm = h / 100.0;  // Convert cm to meters
    const bmi = w / (hm * hm);
    const bmiRounded = Math.round(bmi * 10) / 10;
    
    // CATEGORIZE: Based on hard-coded ranges
    let cat = '';
    if(bmi < 18.5) cat = 'Underweight';
    else if(bmi < 25) cat = 'Normal';
    else if(bmi < 30) cat = 'Overweight';
    else cat = 'Obese';
    
    // RENDER: Display result
    res.textContent = bmiRounded + ' — ' + cat;
  });
</script>
```

**Event Details:**
- **DOM Element:** `<button id="bmi_calc">`
- **Event Type:** `click`
- **Trigger Condition:** User clicks "Calculate BMI" button
- **No HTTP Request:** Computation happens entirely in browser
- **No Data Source:** Uses hard-coded ranges (BMI categories)

**Render (JavaScript DOM Update):**
```javascript
// Initial state
bmi_result.textContent = '';

// After user enters height=170, weight=70, clicks button
// Computed: bmi = 70 / (1.7 * 1.7) = 24.2 → 'Normal'
bmi_result.textContent = '24.2 — Normal';

// After user enters height=160, weight=85, clicks button
// Computed: bmi = 85 / (1.6 * 1.6) = 33.2 → 'Obese'
bmi_result.textContent = '33.2 — Obese';
```

---

## Summary Table: All Interaction Flows

| Flow | Trigger | Event Type | HTTP Request | Data Source | Render Method |
|------|---------|-----------|---------|-------------|--|
| 1. Upload Report | Form submit | `submit` | POST /upload | Form + Model + MongoDB | Jinja2 template (report.html) |
| 2. Progress Tracking | Link click | Navigation | GET /progress | MongoDB query | Jinja2 loop over list |
| 3. View Old Report | Link click | Navigation | GET /report/<id> | MongoDB by ID + regenerate | Jinja2 template (report.html) |
| 4. Toggle Charts | Button click | `click` | None | Session (already on page) | JavaScript DOM toggle |
| 5. File Preview | Input change | `change` | None | Local file input | JavaScript DOM update |
| 6. BMI Calculator | Button click | `click` | None | User inputs (local) | JavaScript DOM update |

---

## Key Rendering Methods Used

### 1. Jinja2 Template Syntax

**Direct Variable Substitution:**
```html
{{ variable }}
{{ dict.key }}
{{ dict['key'] }}
{{ object.method() }}
{{ value|filter }}
```

**Loops:**
```html
{% for item in list %}
  {{ item }}
{% endfor %}

{% for key, value in dict.items() %}
  {{ key }}: {{ value }}
{% endfor %}
```

**Conditionals:**
```html
{% if condition %}
  ...
{% elif other_condition %}
  ...
{% else %}
  ...
{% endif %}
```

**Filters:**
```html
{{ string|upper }}
{{ string|title }}
{{ string|replace('a', 'b') }}
{{ number|round(2) }}
{{ list|length }}
```

### 2. JavaScript DOM Manipulation

**Setting Text Content:**
```javascript
element.textContent = 'new text';  // Plain text
element.innerHTML = '<b>html</b>';  // HTML
```

**Toggling CSS Display:**
```javascript
element.style.display = 'none';    // Hide
element.style.display = 'block';   // Show
element.style.display = 'grid';    // Grid layout
```

**Event Listeners:**
```javascript
element.addEventListener('click', function() { ... });
element.addEventListener('submit', function(e) { e.preventDefault(); ... });
element.addEventListener('change', function() { ... });
```

### 3. Matplotlib (Server-Side Chart Generation)

**Process:**
```python
fig, ax = plt.subplots(figsize=(6, 4))
ax.pie([50, 20, 30], labels=['Carbs', 'Protein', 'Fat'])
# Convert to PNG
buf = io.BytesIO()
fig.savefig(buf, format='png', bbox_inches='tight')
# Encode to base64
data = base64.b64encode(buf.read()).decode('ascii')
# Return as data URI
return f"data:image/png;base64,{data}"
```

**Embedding in HTML:**
```html
<img src="data:image/png;base64,iVBO..." style="max-width: 100%;" />
```

---

## Architecture Comparison

### Traditional Server-Rendered (This App)
```
┌─────────────┐
│  User Input │ (click form, click link)
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Browser Sends HTTP Request         │ (POST/GET to Flask)
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Flask Backend Processing           │ (Query DB, compute, etc.)
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Jinja2 Renders HTML String         │ ({{ }} substitution, {% %} loops)
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Browser Receives Full HTML         │ (Complete page)
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Browser Renders Page               │ (Display to user)
└─────────────────────────────────────┘
```

### Modern SPA (NOT used here)
```
┌─────────────┐
│  User Input │ (click element)
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│  JavaScript Fetch/AJAX              │ (Call API endpoint)
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Backend API Returns JSON           │ (Data only, no HTML)
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  JavaScript Maps Data to DOM        │ (React/Vue/Angular)
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Browser Renders Updated UI         │ (Only changed parts)
└─────────────────────────────────────┘
```

---

## Conclusion

This application uses a **traditional server-side rendering architecture** where:

1. **Trigger:** User interactions (form submission, link clicks, button clicks) are handled by:
   - HTML `<form>` elements (POST), `<a>` links (GET), `<button>` elements
   - JavaScript `addEventListener()` for client-side interactions only

2. **Source:** Data comes from:
   - Flask session storage (temporary)
   - MongoDB database (persistent)
   - File system (ML model: `calorie_model.pkl`)
   - Hard-coded Python dicts (NORMAL_RANGES, FOOD_RECO)
   - Computed values (Matplotlib charts → base64)

3. **Render:** Output is generated via:
   - **Server-side:** Jinja2 template engine ({{ }}, {% %})
   - **Client-side:** JavaScript DOM manipulation (for UI toggles only)
   - **Client-side:** Matplotlib-generated base64 PNG images embedded directly

**No REST API exists** (except the implicit form POST/redirect pattern). All page updates require full-page loads or server redirects.
