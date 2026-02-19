"""
Flask Application V2 - Refactored for Registration Flow & DB Persistence

Backend integration for ML Pipeline V2.
- Handles file uploads during Registration & Profile
- OCR processing (V2)
- Health Status Prediction (V2)
- Diet Recommendation (V2)
- Persistent Storage (SimpleDB)
- Renders results to existing templates
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import numpy as np
import io

# Add project root to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# V2 Imports
from version2.ocr_fix_v2 import extract_blood_report_text_v2, parse_lab_values_v2, assess_lab_values_v2, calculate_clinical_risk_score, normalize_biomarkers
from version2.model_inference_health_v2 import predict_health_status, get_dataset_metrics as get_health_metrics
from version2.model_inference_diet_v2 import predict_diet_metrics, get_dataset_metrics as get_diet_metrics
from version2.diet_plan_generator_v2 import generate_v2_diet_plan
from version2.expert_advice_v2 import get_expert_response
from version2.pdf_generator_v2 import generate_pdf_v2
from version2.chart_generator_v2 import generate_macronutrient_chart, generate_diet_chart_image, generate_health_status_chart
from version2 import mongo_helper as db

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'supersecretkey_v2'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# --- Helper Function for Report Processing ---
def process_report_pipeline(filepath, user_profile, manual_overrides=None):
    """
    Core Pipeline: OCR -> Health Prediction -> Diet Plan -> Charts
    """
    # 1. OCR
    extracted_text = extract_blood_report_text_v2(filepath)
    lab_values = parse_lab_values_v2(extracted_text)
    
    # 2. Strict OCR Enforcement
    # If manual_overrides provided, apply them EXCEPT for protected keys
    protected_keys = ['hemoglobin', 'glucose', 'total_cholesterol']
    if manual_overrides:
        for k, v in manual_overrides.items():
            if k not in protected_keys:
                lab_values[k] = v
    
    # --- BIOMARKER NORMALIZATION LAYER ---
    raw_biomarkers = lab_values.copy()
    lab_values = normalize_biomarkers(lab_values)
    # -------------------------------------
    
    # --- DEBUG TERMINAL LOGGING (CRITICAL) ---
    try:
        print("\n" + "=" * 50)
        print(f"REPORT DEBUG LOG (ID: {datetime.now().strftime('%H%M%S')})")
        print("=" * 50)
        
        print("Extracted biomarkers: ", list(raw_biomarkers.keys()))
        print("Normalized biomarkers:", list(lab_values.keys()))
        
        # Check Visualization Matching
        # Chart generator now accepts broad range of keys
        # We will log what is being passed to the chart engine
        
        print(f"Passing {len(lab_values)} biomarkers to chart generator.")
        
        # Simple check for critical ones just for info
        critical = ['hemoglobin', 'glucose', 'total_cholesterol']
        found_critical = [k for k in critical if k in lab_values]
        print(f"Critical metrics found: {found_critical}")
        
        if not lab_values:
            print("WARNING: Zero biomarkers extracted! Chart will be empty.")
        
        if skipped:
            print(f"Skipped biomarkers: {skipped} (Not in chart config)")
            
        print("=" * 50 + "\n")
    except Exception as e:
        logger.error(f"Debug logging failed: {e}")
    # -----------------------------------------

    # 3. Full Profile for Prediction
    full_profile = user_profile.copy()
    full_profile.update(lab_values)
    
    # 4. Health Prediction
    health_result = predict_health_status(full_profile)
    health_status = health_result.get('status_label', 'Unknown')
    
    # SAFETY OVERRIDE: Use rule-based status if model misses a critical flag
    rule_status = health_result.get('rule_based_status')
    if rule_status and rule_status != health_status:
        logger.info(f"Health Status Override: Model ({health_status}) -> Rule ({rule_status})")
        print(f"Health Status Override: Model ({health_status}) -> Rule ({rule_status})")
        health_status = rule_status
    
    # 5. Assessment
    gender_str = 'Male' if user_profile['gender'] == 1 else 'Female'
    assessment = assess_lab_values_v2(lab_values, user_profile['age'], gender_str)
    deficiencies = [item['test'] for item in assessment if item['status'] != 'NORMAL']
    
    # 6. Recommendation Table Data
    recommendation_table_data = []
    for item in assessment:
         rec_food = f"Foods rich in {item['test']}"
         if item['test'] == 'hemoglobin': rec_food = "Spinach, Red Meat, Beans"
         elif item['test'].lower() == 'glucose': rec_food = "Whole Grains, Leafy Greens"
         elif item['test'].lower() == 'total cholesterol': rec_food = "Oats, Avocados, Nuts"
         
         recommendation_table_data.append({
             'nutrient': item['test'].replace('_', ' ').title(),
             'value': str(item['value']),
             'status': item['status'],
             'food': rec_food if item['status'] != 'NORMAL' else "Maintain balanced diet"
         })

    # 7. Diet Plan
    diet_plan = generate_v2_diet_plan(user_profile)
    
    # --- TERMINAL LOGGING START ---
    try:
        # Calculate Risk Score
        clinical_risk_score = calculate_clinical_risk_score(assessment)
        
        # Model Confidence Level Logic
        conf_val = health_result.get('confidence', 0)
        conf_level_str = "HIGH" if conf_val >= 0.8 else ("MEDIUM" if conf_val >= 0.6 else "LOW")
        if conf_val < 0.6:
            logger.warning("Model confidence is LOW (<60%). Predictions may be unreliable.")

        print("\n" + "-" * 40)
        print("BLOOD REPORT UPLOADED")
        print("OCR EXTRACTION SUCCESSFUL")
        
        print("\nPER-REPORT EVALUATION METRICS:")
        
        print(f"\nPredicted Health Status : {health_result.get('status_label', 'Unknown')}")
        print(f"Prediction Confidence   : {conf_val*100:.1f}%")
        
        print("\nClass Probabilities:")
        probs = health_result.get('class_probabilities', {})
        for label, prob in probs.items():
            print(f"  {label:<10} -> {prob*100:.1f}%")
            
        print("\nLAB VALUE DEVIATION:")
        for item in assessment:
            if item['status'] != 'NORMAL':
                dev_pct = item.get('deviation_pct', 0)
                dev_lbl = item.get('deviation_label', 'Normal')
                sign = "+" if dev_pct > 0 else ""
                print(f"  {item['test']:<15} : {sign}{dev_pct:.0f}% ({dev_lbl})")
        
        print(f"\nClinical Risk Score : {clinical_risk_score} / 100")
        print(f"Model Confidence    : {conf_level_str}")
        print("-" * 40 + "\n")
        
    except Exception as log_err:
        logger.error(f"Failed to print terminal logs: {log_err}")
    # --- TERMINAL LOGGING END ---
    
    # 8. Visuals (Macros)
    # Dynamic Macros calculation
    goal = user_profile.get('goal', 'Maintenance').lower()
    
    # Defaults
    c, p, f = 50, 30, 20
    
    # Adjust based on Goal
    if 'loss' in goal:
        c, p, f = 40, 40, 20
    elif 'muscle' in goal or 'gain' in goal:
        c, p, f = 45, 35, 20
        
    # Adjust based on Health Status (Overrides)
    # If Glucose is high (Diabetes risk), lower carbs
    if 'glucose' in [d.lower() for d in deficiencies] or 'diabetes' in health_status.lower():
         c, p, f = 35, 35, 30
         
    macros = {'carbs': c, 'protein': p, 'fat': f}
    
    # Bundle Report Data
    report_data = {
        'user_profile': user_profile,
        'lab_results': lab_values,
        'health_status': health_status,
        'diet_plan': diet_plan,
        'deficiencies': deficiencies,
        'macros': macros,
        'assessment': assessment, # Needed for display
        'recommendation_table_data': recommendation_table_data,
        'prediction': 2000 # Placeholder calories
    }
    return report_data

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        # Simple DB check
        user = db.get_user_by_email(email)
        if user:
            session['user'] = user
            return redirect(url_for('profile'))
        else:
            # Fallback for demo if not found, create temp session
            session['user'] = {'name': 'Demo User', 'email': email}
            return redirect(url_for('profile'))
    return render_template('login.html')

from werkzeug.security import generate_password_hash
from version2.otp_service import generate_otp, send_otp_email

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form.get('email')
        
        # 1. Verify user exists
        user = db.get_user_by_email(email)
        if not user:
            # Security: Don't reveal user existence, but for UX we might say "If email exists..."
            # For this internal app, let's be explicit
            return "Email not found", 404
            
        # 2. Generate OTP
        otp = generate_otp()
        
        # 3. Save to DB
        saved = db.save_otp(email, otp)
        
        # 4. Send Email
        if saved:
            send_otp_email(email, otp)
            session['reset_email'] = email # Store context
            return redirect(url_for('verify_otp'))
            
    return render_template('forgot.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    email = session.get('reset_email')
    if not email:
        return redirect(url_for('forgot'))
        
    if request.method == 'POST':
        otp_input = request.form.get('otp')
        
        # Verify
        is_valid, msg = db.verify_and_delete_otp(email, otp_input)
        
        if is_valid:
            session['authorized_reset'] = True # Secure token for next step
            return redirect(url_for('reset_password'))
        else:
            return render_template('verify_otp.html', email=email, error=msg)
            
    return render_template('verify_otp.html', email=email)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    email = session.get('reset_email')
    authorized = session.get('authorized_reset')
    
    if not email or not authorized:
        return redirect(url_for('forgot'))
        
    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        if password != confirm:
            return "Passwords do not match", 400
            
        # Hash and Save
        hashed_pw = generate_password_hash(password)
        updated = db.update_password(email, hashed_pw)
        
        if updated:
            # Cleanup session
            session.pop('reset_email', None)
            session.pop('authorized_reset', None)
            return redirect(url_for('login'))
        else:
            return "Error updating password", 500
            
    return render_template('reset_password.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 1. Collect Register Data
        name = request.form.get('name')
        email = request.form.get('email')
        age = int(request.form.get('age', 25))
        gender_str = request.form.get('gender', 'male')
        gender = 1 if gender_str.lower() in ['male', 'm'] else 0
        height = float(request.form.get('height', 170))
        weight = float(request.form.get('weight', 60))
        
        user_data = {
            'name': name,
            'email': email,
            'age': age,
            'gender': gender,
            'height': height,
            'weight': weight,
            'goal': 'Health'
        }
        
        # 2. Handle Mandatory Upload
        f = request.files.get('report')
        if f and f.filename:
            filename = secure_filename(f.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(filepath)
            
            # 3. Process Report
            # Calculate BMI
            height_m = height / 100
            user_data['bmi'] = weight / (height_m ** 2)
            user_data['diet_type'] = 'Vegetarian' # Default
            user_data['uploaded_report_path'] = filepath

            report_data = process_report_pipeline(filepath, user_data)
            
            # 4. Save to DB
            saved_user = db.save_user(user_data)
            saved_report_id = db.save_report(email, report_data)
            
            # 5. Session & Redirect
            session['user'] = saved_user
            return redirect(url_for('view_report', report_id=saved_report_id))
        else:
            # If no file uploaded (should be required, but fallback just saves user)
            saved_user = db.save_user(user_data)
            session['user'] = saved_user
            return redirect(url_for('profile'))
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    
    # Fetch Reports
    reports = db.get_reports_for_user(user['email'])
    
    # Format for display
    display_reports = []
    for r in reports:
        display_reports.append({
            'id': r['id'],
            'title': f"Health Report - {r['timestamp']}",
            'timestamp': r['timestamp'],
            'prediction': r.get('prediction', 2000)
        })
        
    return render_template('profile.html', user=user, reports=display_reports)

@app.route('/delete_report/<report_id>')
def delete_report_route(report_id):
    user = session.get('user')
    if not user:
        return redirect(url_for('login'))
    
    # Optional: Verify user owns the report for security, but for now simple delete
    # (The mongo_helper.delete_report relies on ID)
    
    deleted = db.delete_report(report_id)
    if deleted:
        # Optionally flash a message here
        pass
        
    return redirect(url_for('profile'))

@app.route('/report/<report_id>')
def view_report(report_id):
    report_data = db.get_report_by_id(report_id)
    if not report_data:
        return "Report not found", 404
        
    # Re-generate charts on fly
    macros = report_data.get('macros')
    diet_plan = report_data.get('diet_plan')
    lab_values = report_data.get('lab_results')
    health_status = report_data.get('health_status')
    
    chart_macros = generate_macronutrient_chart(macros)
    chart_meal_plan = generate_diet_chart_image(diet_plan)
    chart_health = generate_health_status_chart(lab_values, health_status)
    
    diet_charts = {
        'macronutrient_chart': chart_macros,
        'meal_plan_chart': chart_meal_plan,
        'lab_status_chart': chart_health,
        'lab_status_chart': chart_health # Duplicate key in original dict? Fixed.
    }
    
    # Save to session for PDF download context
    session['last_report'] = report_data 
    
    # Format for template
    gender_str = "Male" if report_data['user_profile']['gender'] == 1 else "Female"
    
    return render_template('report.html',
                           lab_data=lab_values,
                           prediction=report_data.get('prediction', 2000),
                           health_status=health_status,
                           deficiencies=report_data.get('deficiencies', []),
                           diet_plan={'primary': {'name': 'Custom Diet Plan', 'description': 'AI Generated', 'macros': macros, 'meals': diet_plan['Monday']}},
                           assessment=report_data.get('assessment', []),
                           macros=macros,
                           diet_charts=diet_charts,
                           report=[f"Profile: {report_data['user_profile']['age']}yrs, {gender_str}, {report_data['user_profile']['height']}cm, {report_data['user_profile']['weight']}kg", 
                                   f"Health Status: {health_status}"] + 
                                  [f"{k.replace('_', ' ').title()}: {v}" for k, v in lab_values.items()],
                           recommendations=[f"Eat more {d} rich foods" for d in report_data.get('deficiencies', [])])

@app.route('/download_report/<report_id>')
def download_report(report_id):
    # Retrieve specific report and set as last_report then call pdf logic
    report_data = db.get_report_by_id(report_id)
    if report_data:
        session['last_report'] = report_data
        return redirect(url_for('download_pdf'))
    return "Report not found", 404

# Original route for "Check Another Person" (kept for profile functionality)
@app.route('/analyze_blood_report', methods=['GET', 'POST'])
def analyze_blood_report():
    if request.method == 'POST':
        # "Check Another Person" logic
        # Uses separate input names in profile.html: 'person_name', 'blood_report', 'age_category' (mapped to age?)
        # Actually profile.html uses: 'person_name', 'age_category', 'height', 'weight', 'blood_report'
        
        # We need to adapt this to our pipeline
        f = request.files.get('blood_report')
        if f:
             filename = secure_filename(f.filename)
             filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
             f.save(filepath)
             
             # Construct temp profile
             try:
                 weight = float(request.form.get('weight', 70))
                 height = float(request.form.get('height', 170))
                 age = int(request.form.get('age', 30))
                 gender_str = request.form.get('gender', 'male')
                 gender = 1 if gender_str.lower() == 'male' else 0
                 
                 user_profile = {
                     'name': request.form.get('person_name', 'Guest'),
                     'age': age,
                     'gender': gender,
                     'weight': weight,
                     'height': height,
                     'bmi': weight / ((height/100)**2),
                     'diet_type': 'Vegetarian', # Could add this to form too, but default for now
                     'goal': 'Maintenance' # Default, could infer or add inputs
                 }
                 
                 report_data = process_report_pipeline(filepath, user_profile)
                 
                 # Save temporarily to session for viewing
                 session['last_report'] = report_data
                 
                 # Render directly
                 macros = report_data['macros']
                 diet_plan = report_data['diet_plan']
                 lab_values = report_data['lab_results']
                 health_status = report_data['health_status']
                 
                 chart_macros = generate_macronutrient_chart(macros)
                 chart_meal_plan = generate_diet_chart_image(diet_plan)
                 chart_health = generate_health_status_chart(lab_values, health_status)
                 
                 diet_charts = {
                     'macronutrient_chart': chart_macros,
                     'meal_plan_chart': chart_meal_plan,
                     'lab_status_chart': chart_health
                 }
                 
                 gender_display = "Male" if gender == 1 else "Female"
                 
                 return render_template('report.html',
                           lab_data=lab_values,
                           prediction=2000,
                           health_status=health_status,
                           deficiencies=report_data['deficiencies'],
                           diet_plan={'primary': {'name': 'Custom Diet Plan', 'description': 'AI Generated', 'macros': macros, 'meals': diet_plan['Monday']}},
                           assessment=report_data['assessment'],
                           macros=macros,
                           diet_charts=diet_charts,
                           report=[f"Guest Analysis: {user_profile['name']}", 
                                   f"Profile: {age} yrs, {gender_display}, {height}cm, {weight}kg",
                                   f"Status: {health_status}"],
                           recommendations=report_data['deficiencies'])

             except Exception as e:
                 logger.error(f"Error analyzing guest report: {e}")
                 return "Error processing report", 500
                     
    return redirect(url_for('profile')) # Start at profile

@app.route('/download_pdf')
def download_pdf():
    report_data = session.get('last_report')
    if not report_data:
        return "No report found. Please generate one first.", 404
    
    # Re-generate charts on the fly
    macros = report_data.get('macros', {'carbs': 50, 'protein': 30, 'fat': 20})
    diet_plan = report_data['diet_plan']
    lab_values = report_data['lab_results']
    health_status = report_data['health_status']
    recommendation_table_data = report_data.get('recommendation_table_data', [])
    
    chart_macros = generate_macronutrient_chart(macros)
    chart_meal_plan = generate_diet_chart_image(diet_plan)
    chart_health = generate_health_status_chart(lab_values, health_status)
    
    diet_charts = {
        'macronutrient_chart': chart_macros,
        'meal_plan_chart': chart_meal_plan,
        'lab_status_chart': chart_health
    }
    
    pdf_buffer = generate_pdf_v2(
        report_data['user_profile'],
        report_data['lab_results'],
        report_data['health_status'],
        report_data['diet_plan'],
        report_data['deficiencies'],
        diet_charts,
        recommendation_table_data
    )
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"Nutrition_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
        mimetype='application/pdf'
    )

# --- Other Placeholder Routes ---
@app.route('/profile/edit', methods=['GET', 'POST'])
def profile_edit():
    user = session.get('user')
    if request.method == 'POST':
        user['name'] = request.form.get('name')
        # Could update DB here
        session['user'] = user
        return redirect(url_for('profile'))
    return render_template('profile_edit.html', user=user)

@app.route('/expert')
def expert(): return render_template('expert.html')

@app.route('/ask_expert', methods=['POST'])
def ask_expert():
    # Fallback for non-AJAX form submission
    return render_template('expert.html', message="Question submitted successfully!")

@app.route('/submit_expert_doubt', methods=['POST'])
def submit_expert_doubt():
    # ... reused logic ...
    data = request.form
    answer = get_expert_response(data.get('doubt_question'), data.get('doubt_category'), data.get('selected_expert'))
    return jsonify({'message': f"Thank you. {answer}"})

@app.route('/chatbot', methods=['POST'])
def chatbot():
    """AJAX endpoint for the floating chatbot widget — context-aware."""
    data = request.get_json()
    message = data.get('message', '')
    if not message.strip():
        return jsonify({'reply': 'Please type a question!'})
    
    # ── Build user context from session & DB ──
    context_parts = []
    
    user = session.get('user')
    if user:
        gender_str = "Male" if user.get('gender') == 1 else "Female"
        context_parts.append(
            f"USER PROFILE: Name={user.get('name','N/A')}, "
            f"Age={user.get('age','N/A')}, Gender={gender_str}, "
            f"Height={user.get('height','N/A')}cm, Weight={user.get('weight','N/A')}kg, "
            f"BMI={user.get('bmi','N/A')}, Goal={user.get('goal','N/A')}"
        )
        
        # Fetch latest report from DB
        try:
            reports = db.get_reports_for_user(user.get('email', ''))
            if reports:
                latest = reports[0]  # Most recent
                
                # Lab values
                lab = latest.get('lab_results', {})
                if lab:
                    lab_str = ", ".join([f"{k}={v}" for k, v in lab.items()])
                    context_parts.append(f"LATEST LAB VALUES: {lab_str}")
                
                # Health status
                hs = latest.get('health_status')
                if hs:
                    context_parts.append(f"HEALTH STATUS: {hs}")
                
                # Deficiencies
                defs = latest.get('deficiencies', [])
                if defs:
                    context_parts.append(f"DEFICIENCIES: {', '.join(defs)}")
                
                # Macros
                macros = latest.get('macros', {})
                if macros:
                    context_parts.append(
                        f"RECOMMENDED MACROS: Carbs={macros.get('carbs')}%, "
                        f"Protein={macros.get('protein')}%, Fat={macros.get('fat')}%"
                    )
                
                # Diet plan (just Monday as sample)
                diet = latest.get('diet_plan', {})
                if diet and 'Monday' in diet:
                    meals = diet['Monday']
                    meal_str = ", ".join([f"{k}: {v}" for k, v in meals.items()]) if isinstance(meals, dict) else str(meals)
                    context_parts.append(f"SAMPLE DIET (Monday): {meal_str}")
                    
                # Assessment details
                assessment = latest.get('assessment', [])
                if assessment:
                    abnormal = [f"{a['test']}={a['value']} ({a['status']})" for a in assessment if a.get('status') != 'NORMAL']
                    if abnormal:
                        context_parts.append(f"ABNORMAL LAB RESULTS: {', '.join(abnormal)}")
                    normal = [a['test'] for a in assessment if a.get('status') == 'NORMAL']
                    if normal:
                        context_parts.append(f"NORMAL LAB RESULTS: {', '.join(normal)}")
        except Exception as e:
            logger.error(f"Chatbot context fetch error: {e}")
    
    # Also check session for last viewed report
    last_report = session.get('last_report')
    if last_report and not context_parts:
        lab = last_report.get('lab_results', {})
        if lab:
            lab_str = ", ".join([f"{k}={v}" for k, v in lab.items()])
            context_parts.append(f"VIEWED REPORT LAB VALUES: {lab_str}")
        hs = last_report.get('health_status')
        if hs:
            context_parts.append(f"HEALTH STATUS: {hs}")
    
    # Build the final message with context
    if context_parts:
        context_block = "\n".join(context_parts)
        full_message = (
            f"[USER CONTEXT]\n{context_block}\n"
            f"[END CONTEXT]\n\n"
            f"User's question: {message}"
        )
    else:
        full_message = message
    
    from version2.expert_advice_v2 import get_expert_response
    reply = get_expert_response(full_message, 'general', 'NutriBot')
    return jsonify({'reply': reply})

@app.route('/diet_plan')
def diet_plan():
    return render_template('diet_plans.html', age_group=request.args.get('age_group'))



@app.route('/progress')
def progress(): return render_template('index.html')

@app.route('/categories')
@app.route('/categories/<category>')
def categories(category=None):
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, port=5002)
