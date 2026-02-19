
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import numpy as np

def get_base64_image(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{img_str}"

def generate_macronutrient_chart(macros):
    """
    Generates a pie chart for macronutrients.
    macros: dict {'carbs': 50, 'protein': 30, 'fat': 20}
    """
    labels = list(macros.keys())
    sizes = list(macros.values())
    colors = ['#ff9999', '#66b3ff', '#99ff99']
    
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(sizes, labels=[l.title() for l in labels], colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    plt.title("Recommended Macronutrient Split")
    
    return get_base64_image(fig)

def generate_diet_chart_image(diet_plan):
    """
    Generates a table image for the 7-day diet plan.
    diet_plan: dict with keys 'Monday', 'Tuesday', ...
    """
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    data = []
    
    for day in days:
        meals = diet_plan.get(day, {})
        row = [
            day[:3], # Mon, Tue
            meals.get('Breakfast', '-'),
            meals.get('Lunch', '-'),
            meals.get('Dinner', '-')
        ]
        data.append(row)
        
    df = pd.DataFrame(data, columns=['Day', 'Breakfast', 'Lunch', 'Dinner'])
    
    # Plotting table
    fig, ax = plt.subplots(figsize=(10, 5)) 
    ax.axis('tight')
    ax.axis('off')
    
    # Create table
    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='left')
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.8) # Stretch height
    
    # Styling
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor('#0d4c6b')
            cell.set_text_props(color='white', weight='bold')
        elif row % 2 == 0:
            cell.set_facecolor('#f0f9ff')
            
    plt.title("7-Day Diet Plan Summary", pad=20, fontsize=12, weight='bold')
    
    return get_base64_image(fig)

def generate_health_status_chart(lab_values, health_status):
    """
    Generates a horizontal bar chart comparing user values to normal reference ranges.
    Uses unified scaling: Normal Min = 25, Normal Max = 75.
    """
    # Define normal ranges (approximate for general adult)
    # Define comprehensive normal ranges for visualization
    references = {
        'hemoglobin': (12.0, 16.0),
        'glucose': (70.0, 100.0),
        'total_cholesterol': (125.0, 200.0),
        'triglycerides': (10.0, 150.0),
        'ldl': (0.0, 100.0),
        'hdl': (40.0, 60.0),
        'tsh': (0.4, 4.0),
        'vitamin_d': (20.0, 50.0),
        # Expanded List
        'hematocrit': (41, 50),
        'rbc': (4.5, 5.9),
        'wbc': (4500, 11000),
        'platelets': (150000, 450000),
        'creatinine': (0.7, 1.3),
        'urea': (7, 20),
        'uric_acid': (3.5, 7.2),
        'bilirubin': (0.1, 1.2),
        'sgpt': (7, 56),
        'sgot': (10, 40),
        'alkaline_phosphatase': (44, 147),
        'protein': (6.0, 8.3),
        'albumin': (3.4, 5.4),
        'sodium': (135, 145),
        'potassium': (3.5, 5.0),
        'calcium': (8.5, 10.5),
        'iron': (65, 175),
        'ferritin': (20, 250),
        'vitamin_b12': (200, 900),
        'folate': (2, 20),
        'hba1c': (4.0, 5.6),
        'chloride': (95, 105),
        'mcv': (80, 100),
        'mch': (27, 32),
        'mchc': (32, 36),
        'neutrophils': (40, 75),
        'lymphocytes': (20, 45),
        'monocytes': (2, 10),
        'eosinophils': (1, 6),
        'basophils': (0, 1),
        'alkaline_phosphatase': (44, 147),
        'globulin': (2.0, 3.5),
        'ag_ratio': (1.0, 2.5),
        'esr': (0, 20),
        'rdw': (11.5, 14.5),
        'mpv': (7.4, 10.4),
        'pct': (0.1, 0.28)
    }

    # Normalize keys: Handle synonyms
    if 'glucose' not in lab_values and 'fasting_glucose' in lab_values:
        lab_values['glucose'] = lab_values['fasting_glucose']

    # Filter keys that exist in lab_values
    keys = [k for k in references.keys() if k in lab_values and lab_values[k] > 0]
    
    if not keys:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(0.5, 0.5, 'No matching biomarkers found for visualization', 
                horizontalalignment='center', verticalalignment='center')
        ax.axis('off')
        return get_base64_image(fig)

    y_pos = np.arange(len(keys))
    # Dynamic height
    fig, ax = plt.subplots(figsize=(9, len(keys) * 0.9 + 2))
    
    # Unified Scale Constants
    NORM_START = 25
    NORM_END = 75
    RANGE_WIDTH = NORM_END - NORM_START 
    
    for i, key in enumerate(keys):
        val = lab_values[key]
        ref_low, ref_high = references[key]
        ref_span = ref_high - ref_low
        
        # 1. Background Zones
        # Low Zone (0-25) - Light Red
        ax.barh(i, 25, left=0, height=0.5, color='#ffe6e6', alpha=0.5, edgecolor='none')
        # Normal Zone (25-75) - Light Green
        ax.barh(i, 50, left=25, height=0.5, color='#d4edda', alpha=0.8, edgecolor='none')
        # High Zone (75-100) - Light Red
        ax.barh(i, 25, left=75, height=0.5, color='#ffe6e6', alpha=0.5, edgecolor='none')
        
        # 2. Calculate Scaled Position
        if val < ref_low:
             if ref_low > 0:
                 pos = (val / ref_low) * 25
             else:
                 pos = 0 
        elif val > ref_high:
             excess = val - ref_high
             pos = 75 + (excess / ref_high) * 25 
             if pos > 100: pos = 100
        else:
             offset = val - ref_low
             pct = offset / ref_span
             pos = 25 + (pct * 50)
        
        # 3. Plot Value
        color = '#28a745' if ref_low <= val <= ref_high else '#dc3545' # Green vs Red
        ax.scatter(pos, i, color=color, s=120, zorder=5, edgecolors='white', linewidth=1.5)
        
        # 4. Text Label
        # Format label with unit/status hints logic could be added here
        label_text = f"{val}"
        ax.text(pos, i - 0.3, label_text, ha='center', va='top', fontsize=10, fontweight='bold', color=color)

    ax.set_yticks(y_pos)
    # Improved Labels: Name + Range
    yticklabels = []
    for k in keys:
        name = k.replace('_', ' ').title()
        low, high = references[k]
        yticklabels.append(f"{name}\n({low}-{high})")
        
    ax.set_yticklabels(yticklabels, fontsize=9)
    ax.invert_yaxis()
    
    # Custom X-Axis
    ax.set_xticks([0, 25, 75, 100])
    ax.set_xticklabels(['Low', 'Min', 'Max', 'High'], fontsize=9, color='#666')
    
    ax.set_title('Biomarker Status & Comparison', fontsize=13, fontweight='bold', pad=15)
    ax.grid(axis='x', linestyle='--', alpha=0.3)
    
    # Cleanup border
    for spine in ax.spines.values():
        spine.set_visible(False)
        
    return get_base64_image(fig)
