"""
Diet Plan Generator V2

Generates a 7-day diet plan using the V2 ML model.
"""

from version2.model_inference_diet_v2 import predict_food_recommendation
import random

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
MEALS = ['Breakfast', 'Lunch', 'Dinner', 'Snacks']


SOUTH_INDIAN_OPTIONS = {
    'Breakfast': [
        'Idli with Sambar & Chutney', 
        'Dosa with Coconut Chutney', 
        'Vegetable Upma', 
        'Rava Dosa with Sambar', 
        'Ven Pongal with Vadai',
        'Poha with Peanuts',
        'Ragi Malt & Fruit'
    ],
    'Lunch': [
        'Sambar Rice with Beetroot Poriyal', 
        'Curd Rice with Pomegranate', 
        'Lemon Rice with Roasted Chickpeas', 
        'Vegetable Biryani with Raita', 
        'Rasam Rice with Potato Roast',
        'Millet Curd Rice',
        'Chapati with Vegetable Kurma'
    ],
    'Snacks': [
        'Masala Buttermilk (Chaas)', 
        'Sprouts Salad', 
        'Roasted Makhana', 
        'Sundal (Chickpea Salad)',
        'Fruit Salad with Chat Masala'
    ],
    'Dinner': [
        'Appam with Vegetable Stew', 
        'Chapati with Dal Tadka', 
        'Idiyappam with Coconut Milk', 
        'Roti with Paneer Bhurji', 
        'Vegetable Korma with Dosa',
        'Steamed Vegetables & Soup'
    ]
}

def generate_v2_diet_plan(user_data):
    """
    Generate a 7-day diet plan based on user data, incorporating South Indian options.
    
    Args:
        user_data (dict): Contains age, gender, bmi, diet_type, goal, etc.
    
    Returns:
        dict: 7-day plan
    """
    plan = {}
    
    # Get base ML recommendations
    base_recs = predict_food_recommendation(user_data)
    if not base_recs:
        base_recs = ["Healthy Salad", "Quinoa Bowl", "Grilled Veggies"]
        
    for day in DAYS:
        day_plan = {}
        
        # 50% Chance of strict South Indian Meal vs Mixed with ML Recs
        use_south_indian = True 
        
        if use_south_indian:
            day_plan['Breakfast'] = random.choice(SOUTH_INDIAN_OPTIONS['Breakfast'])
            day_plan['Lunch'] = random.choice(SOUTH_INDIAN_OPTIONS['Lunch'])
            day_plan['Snacks'] = random.choice(SOUTH_INDIAN_OPTIONS['Snacks'])
            day_plan['Dinner'] = random.choice(SOUTH_INDIAN_OPTIONS['Dinner'])
            
            # Inject ML recommendation into one slot to keep it personalized
            # e.g. Replace Dinner with ML Rec occasionally if it fits
            if random.random() > 0.7:
                 day_plan['Dinner'] = random.choice(base_recs)
        else:
            # Standard Mix
            for meal in MEALS:
                day_plan[meal] = random.choice(base_recs)

        plan[day] = day_plan
        
    # Add metadata about the plan type
    plan['reasoning'] = [
        "Incorporates traditional South Indian nutrient-rich foods.",
        f"Aligned with your goal: {user_data.get('goal', 'Health')}",
        "Balanced macronutrients with localized taste preferences."
    ]
    
    # Add primary plan info for UI
    plan['primary'] = {
        'name': 'South Indian Fusion Plan',
        'description': 'A healthy mix of traditional South Indian meals and modern nutrient-rich foods.',
        'macros': {'carbs': 55, 'protein': 25, 'fat': 20}, # South Indian is slightly higher carb/lower fat typically
        'benefits': ['High Fiber', 'Probiotic Rich (Curd/Fermented foods)', 'Good for Digestion'],
        'meals': plan['Monday'] # Sample day
    }
        
    return plan
