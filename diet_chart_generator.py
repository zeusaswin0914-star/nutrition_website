import io
import base64
from matplotlib import pyplot as plt

def _to_data_uri(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode('ascii')
    return f"data:image/png;base64,{data}"

def _macronutrient_pie(macros):
    labels = ['Carbs', 'Protein', 'Fat']
    sizes = [macros.get('carbs',50), macros.get('protein',20), macros.get('fat',30)]
    fig, ax = plt.subplots(figsize=(4,4))
    ax.pie(sizes, labels=labels, autopct='%1.0f%%', colors=['#66BB6A','#29B6F6','#FFCA28'])
    ax.set_title('Macronutrient Distribution')
    return _to_data_uri(fig)

def _meal_plan_bar(calories):
    # Simple distribution across meals
    meals = ['Breakfast','Lunch','Dinner','Snacks']
    # default percentage split
    pct = [0.3, 0.35, 0.3, 0.05]
    vals = [int(calories * p) for p in pct]
    fig, ax = plt.subplots(figsize=(6,3))
    ax.bar(meals, vals, color=['#f39c12','#e67e22','#d35400','#f1c40f'])
    ax.set_ylabel('Calories')
    ax.set_title('Daily Meal Calorie Distribution')
    return _to_data_uri(fig)

def _lab_status_chart(lab_values, normal_ranges):
    # Create a simple horizontal bar showing each lab relative to range
    tests = []
    values = []
    colors = []
    for k, v in lab_values.items():
        tests.append(k)
        values.append(v or 0)
        if k in normal_ranges:
            lo, hi = normal_ranges[k]
            if v is None:
                colors.append('#95a5a6')
            elif v < lo:
                colors.append('#FF6B6B')
            elif v > hi:
                colors.append('#FFA500')
            else:
                colors.append('#66BB6A')
        else:
            colors.append('#95a5a6')

    fig, ax = plt.subplots(figsize=(6, max(2, 0.6*len(tests))))
    y_pos = range(len(tests))
    ax.barh(y_pos, values, color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(tests)
    ax.set_xlabel('Value')
    ax.set_title('Lab Values Status')
    return _to_data_uri(fig)

def _food_reco_image(deficiencies, food_reco):
    # Very simple text-based image listing foods
    text_lines = []
    for d in deficiencies:
        items = food_reco.get(d, [])
        text_lines.append(f"{d}: {', '.join(items)}")
    if not text_lines:
        text_lines = ["No specific food recommendations"]

    fig, ax = plt.subplots(figsize=(6, max(2, 0.4*len(text_lines))))
    ax.axis('off')
    txt = '\n'.join(text_lines)
    ax.text(0, 0.5, txt, fontsize=12, va='center')
    ax.set_title('Food Recommendations')
    return _to_data_uri(fig)

def generate_complete_diet_chart(chart_data):
    """Accepts a dict with keys: calories, macros, lab_values, deficiencies, normal_ranges, food_reco
    Returns a dict of data-URI images for templates to render.
    """
    calories = int(chart_data.get('calories', 2000))
    macros = chart_data.get('macros', {'carbs':50,'protein':20,'fat':30})
    # Normalize macros: accept either fractions (0.5) or percentages (50)
    def _norm(m):
        if m is None:
            return {'carbs':50,'protein':20,'fat':30}
        c = m.get('carbs',50)
        p = m.get('protein',20)
        f = m.get('fat',30)
        if c <= 1:
            c = c * 100
        if p <= 1:
            p = p * 100
        if f <= 1:
            f = f * 100
        # ensure numeric
        return {'carbs': float(c), 'protein': float(p), 'fat': float(f)}

    macros = _norm(macros)
    lab_values = chart_data.get('lab_values', {})
    deficiencies = chart_data.get('deficiencies', [])
    normal_ranges = chart_data.get('normal_ranges', {})
    food_reco = chart_data.get('food_reco', {})

    result = {
        'macronutrient_chart': _macronutrient_pie(macros),
        'meal_plan_chart': _meal_plan_bar(calories),
        'lab_status_chart': _lab_status_chart(lab_values, normal_ranges),
        'food_recommendation_chart': _food_reco_image(deficiencies, food_reco)
    }
    return result
