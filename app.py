# app.py (FULL updated snippet)
from flask import Flask, render_template, request, redirect, url_for, session, send_file, make_response
import joblib, os, io
import numpy as np
from nutrition_engine import analyze_biomarkers, recommend_foods, generate_pdf, NORMAL_RANGES, FOOD_RECO
from mongo_helper import init_mongo, save_prediction, get_collection
from datetime import datetime
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from ocr_helper import extract_blood_report_text, parse_lab_values, assess_lab_values
from recommendation_engine import get_recommendations_for_assessment, generate_meal_plan_recommendation
from pdf_generator import generate_pdf_report
from diet_chart_generator import generate_complete_diet_chart
from diet_plans import recommend_diet_plan, DIET_PLANS

app = Flask(__name__)
app.secret_key = "replace_this_with_a_random_secret"

# uploads
UPLOAD_FOLDER = "uploads"
ALLOWED = {".pdf", ".png", ".jpg", ".jpeg"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# init mongo helper
init_mongo()

# Alias for convenience
predictions_collection = get_collection()

# model will be loaded lazily to avoid blocking startup
model = None
num_cols = []
medians = {}

def load_model():
    """Load the model artifact on first use."""
    global model, num_cols, medians
    if model is None:
        try:
            model, num_cols, medians = joblib.load("calorie_model.pkl")
            print("Model loaded successfully")
        except Exception as e:
            print("Model load error:", e)
            model = None
            num_cols = []
            medians = {}

# helpers
def allowed_file(name):
    _, ext = os.path.splitext(name.lower())
    return ext in ALLOWED

# homepage
@app.route("/")
def index():
    return render_template("index.html", now=datetime.now())

# login/register/logout (demo, no real hashing)
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        email = request.form.get("email")
        password = request.form.get("password")
        # demo: accept any login
        session['user'] = {"email":email, "name": email.split("@")[0]}
        return redirect(url_for('index'))
    return render_template("login.html", now=datetime.now())

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        # basic store in users collection (optional)
        u = {
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "age": request.form.get("age"),
            "height_cm": request.form.get("height"),
            "weight_kg": request.form.get("weight"),
            "password": request.form.get("password")
        }
        # store to DB
        try:
            from mongo_helper import predictions_collection, client
            db = client['nutrition']
            users = db['users']

            # handle uploaded blood report file
            report_file = request.files.get('report')
            if report_file and report_file.filename:
                if allowed_file(report_file.filename):
                    filename = secure_filename(report_file.filename)
                    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    report_file.save(save_path)
                    u['report_file'] = filename
                else:
                    print('Uploaded file not allowed:', report_file.filename)

            users.insert_one({**u, "created": datetime.now()})
        except Exception as e:
            print("User save failed:", e)
        session['user'] = {"name": u['name'], "email": u['email']}
        return redirect(url_for('index'))
    return render_template("register.html", now=datetime.now())

@app.route("/forgot", methods=["GET","POST"])
def forgot():
    if request.method=="POST":
        # demo only: show message
        return render_template("forgot.html", message="If the email exists, we sent a reset link (demo).", now=datetime.now())
    return render_template("forgot.html", now=datetime.now())

# upload report / manual input
@app.route("/upload", methods=["GET","POST"])
def upload_report():
    if request.method == "POST":
        # try file upload
        f = request.files.get("report_file")
        # collect manual values
        age = request.form.get("age")
        height = request.form.get("height")
        weight = request.form.get("weight")
        hgb = request.form.get("hgb")
        glucose = request.form.get("glucose")
        cholesterol = request.form.get("cholesterol")

        parsed = {}
        if f and f.filename and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(path)
            parsed['source_file'] = path
            # Simple OCR fallback: try to extract numeric patterns using pytesseract if available
            try:
                import pytesseract
                from PIL import Image
                # works for PNG/JPG; PDF would need extra handling
                if path.lower().endswith(('.png','.jpg','.jpeg')):
                    txt = pytesseract.image_to_string(Image.open(path))
                    parsed['ocr_text'] = txt
                    # try to find some numbers (very simple heuristics)
                    import re
                    numbers = re.findall(r"(\d+\.\d+|\d+)", txt)
                    # attempt mapping heuristics
                    if numbers:
                        # naive mapping: first numbers maybe Hb, Glucose, Cholesterol
                        if len(numbers)>=1 and not hgb: hgb = numbers[0]
                        if len(numbers)>=2 and not glucose: glucose = numbers[1]
                        if len(numbers)>=3 and not cholesterol: cholesterol = numbers[2]
            except Exception as e:
                parsed['ocr_error'] = str(e)

        # build input vector matching model
        inp = {c: medians.get(c, 0) for c in num_cols}  # medians filled at training time
        # fill available manual values if provided
        def asf(x): 
            try:
                return float(x) if x is not None and x!='' else None
            except:
                return None
        v_age = asf(age); v_height = asf(height); v_weight = asf(weight)
        v_hgb = asf(hgb); v_glu = asf(glucose); v_chol = asf(cholesterol)

        if 'age' in inp and v_age is not None: inp['age'] = v_age
        if 'height' in inp and v_height is not None: inp['height'] = v_height
        if 'weight' in inp and v_weight is not None: inp['weight'] = v_weight
        if 'hemoglobin' in inp and v_hgb is not None: inp['hemoglobin'] = v_hgb
        if 'fasting_glucose' in inp and v_glu is not None: inp['fasting_glucose'] = v_glu
        if 'total_chol' in inp and v_chol is not None: inp['total_chol'] = v_chol

        # predict calories
        user_data = np.array([[inp[c] for c in num_cols]])
        pred = model.predict(user_data)[0] if model else 2000  # default 2000 if no model

        # run nutrition analysis
        lab_values = {"HGB": (v_hgb or 0), "SGP": (v_glu or 0), "TCP": (v_chol or 0)}
        report, deficiencies = analyze_biomarkers(lab_values)
        recs = recommend_foods(deficiencies)
        macros = {"carbs": 50, "protein": 20, "fat": 30}  # percentages

        # save prediction
        try:
            save_prediction(inputs=inp,
                            prediction=float(round(pred,2)),
                            report=report,
                            recommendations=recs)
        except Exception as e:
            print("Save prediction failed:", e)

        # Generate diet charts and diet plan recommendations
        try:
            chart_data = {
                'calories': float(pred),
                'macros': macros,
                'lab_values': lab_values,
                'deficiencies': deficiencies,
                'normal_ranges': NORMAL_RANGES,
                'food_reco': FOOD_RECO
            }
            diet_charts = generate_complete_diet_chart(chart_data)
            
            # Get diet plan recommendations
            diet_recommendation = recommend_diet_plan(
                lab_values=lab_values,
                age=int(v_age) if v_age else 30,
                health_conditions=""
            )
            
            session['last_result'] = {
                "prediction": round(float(pred), 2),
                "report": report,
                "recommendations": recs,
                "macros": macros,
                "diet_charts": diet_charts,
                "lab_values": lab_values,
                "deficiencies": deficiencies,
                "diet_plan": diet_recommendation,
                "age": v_age
            }
        except Exception as e:
            print("Diet chart generation failed:", e)
            session['last_result'] = {
                "prediction": round(float(pred), 2),
                "report": report,
                "recommendations": recs,
                "macros": macros,
                "diet_charts": {},
                "lab_values": lab_values,
                "deficiencies": deficiencies,
                "diet_plan": {},
                "age": v_age
            }
        
        return redirect(url_for('show_report'))

    return render_template("upload.html", now=datetime.now())


# Backwards-compatible endpoint: some templates/forms post to /predict
@app.route('/predict', methods=["GET","POST"])
def predict():
    if request.method == 'POST':
        # reuse upload_report POST handling
        return upload_report()
    return redirect(url_for('base'))

# show result page
@app.route("/report/view")
def show_report():
    r = session.get('last_result')
    if not r:
        # try to load the most recent saved prediction from DB as a fallback
        try:
            doc = predictions_collection.find_one(sort=[('created_at', -1)])
            if doc:
                r = {
                    'prediction': doc.get('prediction', 0),
                    'report': doc.get('report', []),
                    'recommendations': doc.get('recommendations', []),
                    'macros': doc.get('macros', {'carbs':0.5,'protein':0.2,'fat':0.3})
                }
                print(f"[REPORT] Loaded from DB: prediction={r['prediction']}, report_lines={len(r['report'])}")
            else:
                print("[REPORT] No documents in DB")
                return render_template('report.html', prediction=0, report=['No report available.'], recommendations=[], macros={'carbs':0.5,'protein':0.2,'fat':0.3}, now=datetime.now())
        except Exception as e:
            print(f'[REPORT] Failed to load from DB: {e}')
            return render_template('report.html', prediction=0, report=['No report available.'], recommendations=[], macros={'carbs':0.5,'protein':0.2,'fat':0.3}, now=datetime.now())
    else:
        print(f"[REPORT] Loaded from session: prediction={r['prediction']}")

    return render_template("report.html", prediction=r['prediction'],
                           report=r['report'], recommendations=r['recommendations'],
                           macros=r['macros'], diet_charts=r.get('diet_charts', {}),
                           lab_values=r.get('lab_values', {}),
                           deficiencies=r.get('deficiencies', []),
                           diet_plan=r.get('diet_plan', {}),
                           diet_plans=DIET_PLANS,
                           age=r.get('age'),
                           now=datetime.now())

# download pdf endpoint (calls nutrition_engine.generate_pdf which must accept dict)
@app.route("/report/pdf")
def download_pdf():
    r = session.get('last_result')
    if not r:
        return redirect(url_for('base'))
    report_dict = {
        "biomarkers": {},
        "recommendations": r['recommendations'],
        "calories": r['prediction'],
        "macros": r['macros']
    }
    # generate PDF to memory (nutrition_engine.generate_pdf should be adapted to return bytes)
    try:
        pdf_path = generate_pdf(report_dict, filename="nutrition_report.pdf")
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return "PDF generation failed: " + str(e), 500


@app.route('/report/download_html')
def download_html():
    # render the report template as HTML and return as downloadable file
    r = session.get('last_result')
    if not r:
        return redirect(url_for('base'))
    html = render_template('report.html', prediction=r['prediction'], report=r['report'], recommendations=r['recommendations'], macros=r['macros'], now=datetime.now())
    resp = make_response(html)
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    resp.headers['Content-Disposition'] = 'attachment; filename=nutrition_report.html'
    return resp

# expert page
@app.route("/expert")
def expert():
    return render_template("expert.html", now=datetime.now())

# submit expert doubt/question
@app.route("/submit-expert-doubt", methods=["POST"])
def submit_expert_doubt():
    name = request.form.get("doubt_name")
    email = request.form.get("doubt_email")
    category = request.form.get("doubt_category")
    question = request.form.get("doubt_question")
    selected_expert = request.form.get("selected_expert")
    
    # Save to database
    try:
        col = predictions_collection
        col.insert_one({
            "type": "expert_doubt",
            "name": name,
            "email": email,
            "category": category,
            "question": question,
            "selected_expert": selected_expert,
            "created_at": datetime.now()
        })
        print(f"[DOUBT] Saved question from {name} for expert {selected_expert}")
    except Exception as e:
        print(f"[DOUBT] Failed to save: {e}")
    
    # Return JSON response
    return {'message': f'Your doubt has been submitted to {selected_expert}. We will respond within 24 hours!'}

# profile / history
@app.route("/profile")
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    # load user's saved predictions (demo loads all)
    try:
        docs = list(predictions_collection.find().sort("timestamp",-1).limit(30))
        # convert ObjectId/timestamp for template
        for d in docs:
            d['timestamp'] = d.get('timestamp', datetime.now()).strftime("%Y-%m-%d %H:%M")
            # ensure string id for url building in templates
            try:
                d['id'] = str(d.get('_id'))
            except Exception:
                d['id'] = ''
        return render_template("profile.html", reports=docs, now=datetime.now())
    except Exception as e:
        print("Failed to load reports:", e)
        return render_template("profile.html", reports=[], now=datetime.now())


@app.route('/profile/edit', methods=["GET","POST"])
def profile_edit():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Collect form data
        name = request.form.get('name')
        email = request.form.get('email')
        age = request.form.get('age')
        age_category = request.form.get('age_category')
        height_cm = request.form.get('height_cm')
        weight_kg = request.form.get('weight_kg')
        phone = request.form.get('phone')
        health_conditions = request.form.get('health_conditions')
        
        # Update session immediately
        session['user']['name'] = name or session['user'].get('name')
        session['user']['email'] = email or session['user'].get('email')
        session['user']['age'] = age
        session['user']['age_category'] = age_category
        session['user']['height_cm'] = height_cm
        session['user']['weight_kg'] = weight_kg
        session['user']['phone'] = phone
        session['user']['health_conditions'] = health_conditions
        
        # Persist to MongoDB users collection
        try:
            from mongo_helper import client
            db = client['nutrition']
            users_col = db['users']
            users_col.update_one(
                {'email': session['user'].get('email')},
                {'$set': {
                    'name': name,
                    'email': email,
                    'age': age,
                    'age_category': age_category,
                    'height_cm': height_cm,
                    'weight_kg': weight_kg,
                    'phone': phone,
                    'health_conditions': health_conditions,
                    'updated_at': datetime.now()
                }},
                upsert=True
            )
            print(f"[DB] Updated profile for {email}")
        except Exception as e:
            print(f"[DB] Failed to update profile: {e}")
        
        # Redirect back to profile with success message
        return render_template("profile_edit.html", message="Profile updated successfully!", now=datetime.now())
    
    # GET request -> show edit form
    return render_template("profile_edit.html", now=datetime.now())


@app.route('/report/<report_id>')
def view_report(report_id):
    try:
        doc = predictions_collection.find_one({'_id': ObjectId(report_id)})
        if not doc:
            return "Report not found", 404
        # prepare values for report view
        prediction = doc.get('prediction', 0)
        report_lines = doc.get('report', [])
        recommendations = doc.get('recommendations', [])
        macros = doc.get('macros', {'carbs':0.5,'protein':0.2,'fat':0.3})

        # Reconstruct lab values from saved inputs (if present) to generate charts
        inputs = doc.get('inputs', {}) or {}
        def _asfloat(x):
            try:
                return float(x)
            except Exception:
                return None

        hgb = _asfloat(inputs.get('hemoglobin') or inputs.get('HGB'))
        glu = _asfloat(inputs.get('fasting_glucose') or inputs.get('SGP') or inputs.get('glucose'))
        chol = _asfloat(inputs.get('total_chol') or inputs.get('TCP') or inputs.get('cholesterol'))

        lab_values = {"HGB": (hgb or 0), "SGP": (glu or 0), "TCP": (chol or 0)}

        try:
            # Analyze biomarkers and generate food recommendations
            report_analysis, deficiencies = analyze_biomarkers(lab_values)
            food_recs = recommend_foods(deficiencies)

            # Build chart data and generate diet charts for the report view
            chart_data = {
                'calories': float(prediction),
                'macros': macros,
                'lab_values': lab_values,
                'deficiencies': deficiencies,
                'normal_ranges': NORMAL_RANGES,
                'food_reco': FOOD_RECO
            }
            diet_charts = generate_complete_diet_chart(chart_data)
            diet_recommendation = recommend_diet_plan(lab_values=lab_values, age=int(inputs.get('age') or 30), health_conditions="")
        except Exception as e:
            print(f"[REPORT] Failed to generate diet charts: {e}")
            diet_charts = {}
            diet_recommendation = {}

        return render_template('report.html', prediction=prediction, report=report_lines, recommendations=recommendations, macros=macros, diet_charts=diet_charts, lab_values=lab_values, deficiencies=deficiencies, diet_plan=diet_recommendation, now=datetime.now())
    except Exception as e:
        return f"Error loading report: {e}", 500


@app.route('/report/download/<report_id>')
def download_report(report_id):
    try:
        doc = predictions_collection.find_one({'_id': ObjectId(report_id)})
        if not doc:
            return "Report not found", 404
        prediction = doc.get('prediction', 0)
        report_lines = doc.get('report', [])
        recommendations = doc.get('recommendations', [])
        macros = doc.get('macros', {'carbs':0.5,'protein':0.2,'fat':0.3})
        html = render_template('report.html', prediction=prediction, report=report_lines, recommendations=recommendations, macros=macros, now=datetime.now())
        resp = make_response(html)
        resp.headers['Content-Type'] = 'text/html; charset=utf-8'
        resp.headers['Content-Disposition'] = f'attachment; filename=report_{report_id}.html'
        return resp
    except Exception as e:
        return f"Error downloading report: {e}", 500

# nutrition categories page
@app.route("/categories")
@app.route("/categories/<category>")
def categories(category=None):
    return render_template("categories.html", category=category, now=datetime.now())

# articles page
@app.route("/articles")
@app.route("/articles/<article>")
def articles(article=None):
    return render_template("articles.html", article=article, now=datetime.now())

# expert Q&A submission
@app.route("/ask-expert", methods=["GET","POST"])
def ask_expert():
    if request.method=="POST":
        name = request.form.get("name")
        age_category = request.form.get("age_category")
        question = request.form.get("question")
        # Save to DB (in-memory or MongoDB)
        try:
            col = predictions_collection
            col.insert_one({
                "type": "expert_question",
                "name": name,
                "age_category": age_category,
                "question": question,
                "created_at": datetime.now()
            })
        except Exception as e:
            print("Failed to save question:", e)
        return render_template("expert.html", message="Thank you! Your question has been submitted. Our experts will review it soon.", now=datetime.now())
    return redirect(url_for('expert'))

# diet plans by age group
@app.route("/diet-plan")
@app.route("/diet-plan/<age_group>")
def diet_plan(age_group=None):
    return render_template("diet_plans.html", age_group=age_group, now=datetime.now())

# analyze another person's blood report
@app.route("/check-blood-report", methods=["GET","POST"])
def analyze_blood_report():
    if request.method=="POST":
        person_name = request.form.get("person_name") or "Unnamed"
        age_category = request.form.get("age_category")
        health_conditions = request.form.get("health_conditions") or ""
        blood_report = request.files.get("blood_report")
        
        if not age_category:
            return render_template("check_report.html", error="Please select an age category.", now=datetime.now())
        
        if blood_report and blood_report.filename:
            if allowed_file(blood_report.filename):
                filename = secure_filename(f"{person_name}_{age_category}_{datetime.now().timestamp()}.pdf")
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                blood_report.save(save_path)
                
                # Extract text from blood report using OCR
                extracted_text = ""
                lab_values = {}
                assessments = []
                recommendations = {}
                
                try:
                    extracted_text = extract_blood_report_text(save_path)
                    print(f"[OCR] Extracted {len(extracted_text)} characters from {filename}")
                except Exception as e:
                    print(f"[OCR] Error extracting text: {e}")
                
                # Parse lab values from extracted text
                if extracted_text:
                    try:
                        lab_values = parse_lab_values(extracted_text)
                        print(f"[PARSE] Found {len(lab_values)} lab values: {list(lab_values.keys())}")
                    except Exception as e:
                        print(f"[PARSE] Error parsing lab values: {e}")
                
                # Assess lab values against age-appropriate ranges
                if lab_values:
                    try:
                        assessments = assess_lab_values(lab_values, age_category)
                        print(f"[ASSESS] Generated {len(assessments)} assessments")
                    except Exception as e:
                        print(f"[ASSESS] Error assessing values: {e}")
                
                # Generate personalized recommendations
                if assessments or lab_values:
                    try:
                        recommendations = get_recommendations_for_assessment(assessments, age_category, health_conditions)
                        print(f"[RECOMMEND] Generated {len(recommendations.get('test_recommendations', []))} recommendations")
                    except Exception as e:
                        print(f"[RECOMMEND] Error generating recommendations: {e}")
                
                # Generate PDF report
                pdf_filename = None
                try:
                    pdf_filename = secure_filename(f"nutrition_report_{person_name}_{datetime.now().timestamp()}.pdf")
                    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
                    generate_pdf_report(person_name, age_category, assessments, recommendations, health_conditions, pdf_path)
                    print(f"[PDF] Generated report: {pdf_filename}")
                except Exception as e:
                    print(f"[PDF] Error generating PDF: {e}")
                
                # Log the analysis in DB
                try:
                    col = predictions_collection
                    col.insert_one({
                        "type": "blood_report_analysis",
                        "person_name": person_name,
                        "age_category": age_category,
                        "health_conditions": health_conditions,
                        "report_file": filename,
                        "pdf_report": pdf_filename,
                        "extracted_text": extracted_text[:500] if extracted_text else "",
                        "lab_values": lab_values,
                        "assessments": assessments,
                        "recommendations_count": len(recommendations.get('test_recommendations', [])),
                        "created_at": datetime.now()
                    })
                except Exception as e:
                    print("Failed to save blood report analysis:", e)
                
                # Store in session for display
                session['blood_report_result'] = {
                    "person_name": person_name,
                    "age_category": age_category,
                    "health_conditions": health_conditions,
                    "extracted_text": extracted_text[:1000] if extracted_text else "No text extracted",
                    "lab_values": lab_values,
                    "assessments": assessments,
                    "recommendations": recommendations,
                    "pdf_filename": pdf_filename,
                    "report_file": filename
                }
                
                return redirect(url_for('view_blood_report'))
            else:
                return render_template("check_report.html", error="File type not allowed. Please upload PDF, PNG, or JPG.", now=datetime.now())
        else:
            return render_template("check_report.html", error="Please upload a blood report file.", now=datetime.now())
    
    return render_template("check_report.html", now=datetime.now())

# view blood report analysis results
@app.route("/blood-report/view")
def view_blood_report():
    result = session.get('blood_report_result')
    if not result:
        return redirect(url_for('analyze_blood_report'))
    
    return render_template("blood_report_result.html", 
                          person_name=result['person_name'],
                          age_category=result['age_category'],
                          health_conditions=result['health_conditions'],
                          extracted_text=result['extracted_text'],
                          lab_values=result['lab_values'],
                          assessments=result['assessments'],
                          recommendations=result['recommendations'],
                          pdf_filename=result['pdf_filename'],
                          now=datetime.now())

# download blood report PDF
@app.route("/blood-report/download/<filename>")
def download_blood_report_pdf(filename):
    result = session.get('blood_report_result')
    if not result or result.get('pdf_filename') != filename:
        return "Unauthorized", 403
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename)
    else:
        return "File not found", 404

# progress tracking - view all user's blood reports
@app.route("/progress")
def progress():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    try:
        col = predictions_collection
        # Get all blood report analyses for all people (demo: no user filtering)
        reports = list(col.find({"type": "blood_report_analysis"}).sort("created_at", -1))
        
        for report in reports:
            report['created_at'] = report.get('created_at', datetime.now()).strftime("%Y-%m-%d %H:%M")
        
        return render_template("progress_tracking.html", reports=reports, now=datetime.now())
    except Exception as e:
        print(f"Failed to load progress: {e}")
        return render_template("progress_tracking.html", reports=[], now=datetime.now())

if __name__ == "__main__":
    app.run(debug=True)
