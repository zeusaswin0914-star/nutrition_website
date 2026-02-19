"""
Diet Logic V2 for Enhanced Diet Recommendations
Provides gender-aware, age-specific, and severity-based diet plans.
COMPATIBLE with existing diet_plans.recommend_diet_plan() format.
"""

from typing import Dict, List, Optional, Any


# Diet plan templates with detailed meal plans
DIET_PLANS_V2 = {
    'balanced': {
        'emoji': '🥗',
        'name': 'Balanced Diet',
        'description': 'A balanced diet focusing on whole foods, adequate protein, and fiber.',
        'macros': {'carbs': 50, 'protein': 20, 'fat': 30},
        'benefits': ['Supports general health', 'Easy to follow', 'Suitable for most adults'],
        'meals': {
            'breakfast': 'Oatmeal with fruits and nuts',
            'lunch': 'Grilled chicken with quinoa and salad',
            'dinner': 'Baked fish with vegetables and brown rice',
            'snacks': 'Greek yogurt, fruits, nuts'
        }
    },
    'iron_rich': {
        'emoji': '🍖',
        'name': 'Iron-Rich Plan',
        'description': 'Increase iron-rich foods and pair with vitamin C for better absorption.',
        'macros': {'carbs': 45, 'protein': 25, 'fat': 30},
        'benefits': ['Supports hemoglobin recovery', 'Higher bioavailable iron sources', 'Addresses anemia'],
        'meals': {
            'breakfast': 'Fortified cereal with orange slices and eggs',
            'lunch': 'Beef/chicken salad with spinach and beans',
            'dinner': 'Lentil stew with vegetables and a citrus salad',
            'snacks': 'Dried apricots, pumpkin seeds, dark chocolate'
        }
    },
    'low_carb': {
        'emoji': '🥦',
        'name': 'Low-Carb Plan',
        'description': 'Lower carbohydrates and focus on fiber-rich vegetables and lean proteins.',
        'macros': {'carbs': 30, 'protein': 35, 'fat': 35},
        'benefits': ['Helps control blood glucose', 'Supports weight management', 'Reduces insulin spikes'],
        'meals': {
            'breakfast': 'Vegetable omelet with avocado',
            'lunch': 'Grilled salmon with leafy greens',
            'dinner': 'Stir-fried chicken with broccoli and cauliflower rice',
            'snacks': 'Nuts, cheese, cucumber sticks'
        }
    },
    'heart_healthy': {
        'emoji': '🐟',
        'name': 'Heart-Healthy Plan',
        'description': 'Focus on soluble fiber, omega-3s, and reduced saturated fat.',
        'macros': {'carbs': 45, 'protein': 20, 'fat': 35},
        'benefits': ['Lowers LDL cholesterol', 'Supports cardiovascular health', 'Rich in omega-3'],
        'meals': {
            'breakfast': 'Oats with berries and flaxseed',
            'lunch': 'Grilled mackerel with salad and quinoa',
            'dinner': 'Baked trout with steamed vegetables',
            'snacks': 'Almonds, walnuts, apple slices'
        }
    },
    'vitamin_boost': {
        'emoji': '🍊',
        'name': 'Vitamin Boost Plan',
        'description': 'Maximize vitamin intake with colorful fruits and vegetables.',
        'macros': {'carbs': 55, 'protein': 18, 'fat': 27},
        'benefits': ['Addresses vitamin deficiencies', 'Boosts immunity', 'Improves energy'],
        'meals': {
            'breakfast': 'Smoothie with berries, orange, and spinach',
            'lunch': 'Colorful salad with grilled chicken and citrus dressing',
            'dinner': 'Vegetable stir-fry with tofu and brown rice',
            'snacks': 'Fresh fruits, bell pepper strips, carrot sticks'
        }
    },
    'kidney_friendly': {
        'emoji': '💧',
        'name': 'Kidney-Friendly Plan',
        'description': 'Moderate protein and sodium to support kidney function.',
        'macros': {'carbs': 55, 'protein': 15, 'fat': 30},
        'benefits': ['Reduces kidney workload', 'Manages uric acid', 'Supports hydration'],
        'meals': {
            'breakfast': 'Rice porridge with berries',
            'lunch': 'Vegetable soup with small portion of chicken',
            'dinner': 'Steamed fish with rice and low-sodium vegetables',
            'snacks': 'Grapes, cucumber, rice cakes'
        }
    }
}

# Age-specific meal modifications
AGE_MODIFICATIONS = {
    'child': {
        'meal_size': 'smaller portions',
        'texture': 'softer textures preferred',
        'focus': ['calcium for bone development', 'iron for growth', 'protein for muscle development'],
        'avoid': ['excessive sugar', 'caffeine', 'processed foods']
    },
    'adult': {
        'meal_size': 'standard portions',
        'texture': 'regular',
        'focus': ['balanced nutrition', 'weight management', 'disease prevention'],
        'avoid': ['excess sodium', 'saturated fats', 'added sugars']
    },
    'senior': {
        'meal_size': 'moderate portions, more meals',
        'texture': 'easy to chew and digest',
        'focus': ['protein for muscle maintenance', 'calcium for bone health', 'B12 supplementation'],
        'avoid': ['hard-to-chew foods', 'high sodium', 'excess fat']
    }
}

# Gender-specific recommendations
GENDER_MODIFICATIONS = {
    'male': {
        'iron': 'standard iron needs (8mg/day)',
        'calories': 'higher calorie needs',
        'protein': 'higher protein for muscle mass'
    },
    'female': {
        'iron': 'higher iron needs (18mg/day, reproductive age)',
        'calories': 'moderate calorie needs',
        'calcium': 'extra calcium during pregnancy/menopause'
    }
}


def get_age_group(age: Optional[int]) -> str:
    """Determine age group from numeric age."""
    if age is None:
        return 'adult'
    elif age < 18:
        return 'child'
    elif age <= 65:
        return 'adult'
    else:
        return 'senior'


def select_primary_plan(lab_values: Dict[str, float], 
                        deficiencies: List[str] = None) -> str:
    """
    Select the most appropriate diet plan based on lab values.
    
    Args:
        lab_values: Dict of biomarker values
        deficiencies: Optional list of identified deficiencies
    
    Returns:
        Diet plan key (e.g., 'balanced', 'iron_rich')
    """
    if deficiencies is None:
        deficiencies = []
    
    # Extract key values with None fallbacks
    hgb = lab_values.get('HGB') or lab_values.get('HGP') or lab_values.get('hemoglobin')
    glu = lab_values.get('SGP') or lab_values.get('fasting_glucose')
    chol = lab_values.get('TCP') or lab_values.get('total_chol')
    uap = lab_values.get('UAP') or lab_values.get('uric_acid')
    
    # Priority-based selection
    
    # 1. Iron deficiency takes priority (anemia risk)
    if hgb is not None and hgb < 12:
        return 'iron_rich'
    if 'HGP' in deficiencies or 'HGB' in deficiencies or 'FEP' in deficiencies:
        return 'iron_rich'
    
    # 2. High glucose - low carb diet
    if glu is not None and glu > 140:
        return 'low_carb'
    if 'SGP' in deficiencies:
        return 'low_carb'
    
    # 3. High cholesterol - heart healthy
    if chol is not None and chol > 200:
        return 'heart_healthy'
    if 'TCP' in deficiencies or 'LCP' in deficiencies:
        return 'heart_healthy'
    
    # 4. Kidney issues - kidney friendly
    if uap is not None and uap > 7:
        return 'kidney_friendly'
    if 'UAP' in deficiencies or 'CEP' in deficiencies:
        return 'kidney_friendly'
    
    # 5. Vitamin deficiencies
    vitamin_markers = ['VAP', 'VEP', 'VCP', 'FOP']
    if any(v in deficiencies for v in vitamin_markers):
        return 'vitamin_boost'
    
    # Default to balanced
    return 'balanced'


def get_alternative_plans(primary_plan: str, lab_values: Dict[str, float]) -> List[Dict]:
    """
    Get alternative diet plans different from primary.
    """
    alternatives = []
    
    for plan_id, plan_data in DIET_PLANS_V2.items():
        if plan_id == primary_plan:
            continue
        
        alternatives.append({
            'id': plan_id,
            'emoji': plan_data['emoji'],
            'name': plan_data['name'],
            'macros': plan_data['macros'],
            'description': plan_data['description'][:50] + '...'
        })
    
    # Return top 3 alternatives
    return alternatives[:3]


def recommend_diet_plan_v2(lab_values: Dict[str, float] = None,
                           age: int = 30,
                           gender: str = None,
                           health_conditions: str = "",
                           deficiencies: List[str] = None) -> Dict[str, Any]:
    """
    Generate comprehensive diet recommendation.
    COMPATIBLE with existing diet_plans.recommend_diet_plan() output format.
    
    Args:
        lab_values: Dict of biomarker values
        age: Patient age
        gender: Patient gender ('male', 'female')
        health_conditions: Additional health conditions string
        deficiencies: List of identified deficiencies
    
    Returns:
        Dict with 'primary' and 'alternatives' matching existing format
    """
    if lab_values is None:
        lab_values = {}
    
    if deficiencies is None:
        deficiencies = []
    
    # Determine age group
    age_group = get_age_group(age)
    
    # Select primary diet plan
    primary_key = select_primary_plan(lab_values, deficiencies)
    primary_plan = DIET_PLANS_V2[primary_key].copy()
    
    # Add age-specific modifications
    age_mods = AGE_MODIFICATIONS.get(age_group, AGE_MODIFICATIONS['adult'])
    primary_plan['age_guidance'] = {
        'group': age_group,
        'meal_size': age_mods['meal_size'],
        'focus_nutrients': age_mods['focus'],
        'avoid': age_mods['avoid']
    }
    
    # Add gender-specific modifications
    if gender:
        gender_key = 'male' if gender.lower() in ['m', 'male', '1', 'man'] else 'female'
        gender_mods = GENDER_MODIFICATIONS.get(gender_key, GENDER_MODIFICATIONS['male'])
        primary_plan['gender_guidance'] = gender_mods
    
    # Add deficiency-specific details
    if deficiencies:
        primary_plan['addressing_deficiencies'] = deficiencies
    
    # Get alternatives
    alternatives = get_alternative_plans(primary_key, lab_values)
    
    return {
        'primary': primary_plan,
        'alternatives': alternatives
    }


# Alias for backward compatibility with existing import
recommend_diet_plan = recommend_diet_plan_v2


# List format for UI compatibility (matching diet_plans.DIET_PLANS)
DIET_PLANS = [
    {'id': key, 'name': data['name'], 'macros': data['macros']}
    for key, data in DIET_PLANS_V2.items()
]


if __name__ == '__main__':
    # Test diet logic
    print("Testing Diet Logic V2...")
    
    # Test case 1: Low hemoglobin (anemia)
    result = recommend_diet_plan_v2(
        lab_values={'HGP': 10.5, 'SGP': 95, 'TCP': 180},
        age=30,
        gender='female'
    )
    print(f"\nTest 1 - Low Hemoglobin:")
    print(f"  Primary Plan: {result['primary']['name']}")
    print(f"  Emoji: {result['primary']['emoji']}")
    
    # Test case 2: High glucose
    result = recommend_diet_plan_v2(
        lab_values={'HGP': 14.5, 'SGP': 180, 'TCP': 200},
        age=55,
        gender='male'
    )
    print(f"\nTest 2 - High Glucose:")
    print(f"  Primary Plan: {result['primary']['name']}")
    
    # Test case 3: High cholesterol
    result = recommend_diet_plan_v2(
        lab_values={'HGP': 14.0, 'SGP': 95, 'TCP': 250},
        age=60,
        gender='male'
    )
    print(f"\nTest 3 - High Cholesterol:")
    print(f"  Primary Plan: {result['primary']['name']}")
    
    # Test case 4: Balanced (no issues)
    result = recommend_diet_plan_v2(
        lab_values={'HGP': 14.0, 'SGP': 90, 'TCP': 180},
        age=35,
        gender='female'
    )
    print(f"\nTest 4 - Balanced:")
    print(f"  Primary Plan: {result['primary']['name']}")
    
    print("\n✓ Diet logic tests completed!")
