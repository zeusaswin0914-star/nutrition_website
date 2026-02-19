"""Provides simple diet plan templates and a recommend_diet_plan selector.
This is a minimal replacement used by the app when diet_plans.py was removed.
"""

DIET_PLANS = [
    {'id': 'balanced', 'name': 'Balanced Diet', 'macros': {'carbs':50,'protein':20,'fat':30}},
    {'id': 'iron_rich', 'name': 'Iron-rich', 'macros': {'carbs':45,'protein':25,'fat':30}},
    {'id': 'low_carb', 'name': 'Low-Carb', 'macros': {'carbs':30,'protein':35,'fat':35}},
    {'id': 'heart_health', 'name': 'Heart-Healthy', 'macros': {'carbs':45,'protein':20,'fat':35}},
]


def recommend_diet_plan(lab_values=None, age=30, health_conditions=""):
    """Return a dict with primary plan and alternatives based on simple lab heuristics.

    lab_values: dict like {'HGB':12, 'SGP':90, 'TCP':180}
    """
    if lab_values is None:
        lab_values = {}

    primary = {
        'emoji': '🥗',
        'name': 'Balanced Diet',
        'description': 'A balanced diet focusing on whole foods, adequate protein and fiber.',
        'macros': {'carbs':50, 'protein':20, 'fat':30},
        'benefits': ['Supports general health', 'Easy to follow', 'Suitable for most adults'],
        'meals': {
            'breakfast': 'Oatmeal with fruits and nuts',
            'lunch': 'Grilled chicken with quinoa and salad',
            'dinner': 'Baked fish with vegetables and brown rice',
            'snacks': 'Greek yogurt, fruits, nuts'
        }
    }

    alternatives = []

    # Simple rules
    hgb = lab_values.get('HGB') or lab_values.get('hemoglobin')
    glu = lab_values.get('SGP') or lab_values.get('fasting_glucose')
    chol = lab_values.get('TCP') or lab_values.get('total_chol')

    if hgb is not None and hgb < 12:
        primary = {
            'emoji': '🍖',
            'name': 'Iron-rich Plan',
            'description': 'Increase iron-rich foods and pair with vitamin C for better absorption.',
            'macros': {'carbs':45, 'protein':25, 'fat':30},
            'benefits': ['Supports hemoglobin recovery', 'Higher bioavailable iron sources'],
            'meals': {
                'breakfast': 'Fortified cereal with orange slices and eggs',
                'lunch': 'Beef/chicken salad with spinach and beans',
                'dinner': 'Lentil stew with vegetables and a citrus salad',
                'snacks': 'Dried apricots, pumpkin seeds'
            }
        }
        alternatives.append({'emoji':'🥗','name':'Balanced Diet','macros':{'carbs':50,'protein':20,'fat':30},'description':'Balanced'})

    if glu is not None and glu > 140:
        primary = {
            'emoji': '🥦',
            'name': 'Low-Carb Plan',
            'description': 'Lower carbohydrates and focus on fiber-rich vegetables and lean proteins.',
            'macros': {'carbs':30, 'protein':35, 'fat':35},
            'benefits': ['Helps control blood glucose', 'Supports weight management'],
            'meals': {
                'breakfast': 'Vegetable omelet with avocado',
                'lunch': 'Grilled salmon with leafy greens',
                'dinner': 'Stir-fried chicken with broccoli and cauliflower rice',
                'snacks': 'Nuts, Greek yogurt'
            }
        }
        alternatives.append({'emoji':'🍖','name':'Iron-rich','macros':{'carbs':45,'protein':25,'fat':30},'description':'Iron-rich'})

    if chol is not None and chol > 200:
        primary = {
            'emoji': '🐟',
            'name': 'Heart-Healthy Plan',
            'description': 'Focus on soluble fiber, omega-3s and reduced saturated fat.',
            'macros': {'carbs':45, 'protein':20, 'fat':35},
            'benefits': ['Lowers LDL and supports cardiovascular health'],
            'meals': {
                'breakfast': 'Oats with berries and flaxseed',
                'lunch': 'Grilled mackerel with salad and quinoa',
                'dinner': 'Baked trout with steamed vegetables',
                'snacks': 'Almonds, apple'
            }
        }
        alternatives.append({'emoji':'🥗','name':'Balanced Diet','macros':{'carbs':50,'protein':20,'fat':30},'description':'Balanced'})

    # If no special condition detected, keep the balanced primary and add alternatives
    if not alternatives:
        alternatives = [p for p in DIET_PLANS if p['id'] != 'balanced']

    return {'primary': primary, 'alternatives': alternatives}
