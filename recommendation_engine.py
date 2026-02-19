"""AI-powered personalized nutrition recommendations based on lab values."""


def get_recommendations_for_assessment(assessments, age_category, health_conditions=""):
    """
    Generate personalized nutrition recommendations based on lab assessments.
    
    Args:
        assessments: List of lab value assessments from ocr_helper.assess_lab_values()
        age_category: Age group (toddler, child, teen, adult, senior)
        health_conditions: Additional health conditions provided by user
        
    Returns:
        List of personalized recommendations
    """
    recommendations = []
    
    # Map test names to recommendation templates
    low_test_reco = {
        'Hemoglobin': {
            'issue': 'Low hemoglobin may indicate anemia',
            'foods': ['Red meat', 'Spinach', 'Lentils', 'Beans', 'Fortified cereals', 'Pumpkin seeds'],
            'supplements': ['Iron supplement (consult doctor)', 'Vitamin C (enhances iron absorption)'],
            'actions': ['Eat iron-rich foods with vitamin C', 'Avoid tea/coffee with meals', 'Cook in cast iron pan']
        },
        'Iron': {
            'issue': 'Low iron stores may affect energy and development',
            'foods': ['Beef', 'Chicken', 'Fish', 'Beans', 'Dark leafy greens', 'Dried apricots'],
            'supplements': ['Iron supplement', 'Vitamin C supplement'],
            'actions': ['Increase heme iron sources', 'Pair iron foods with citrus fruits', 'Avoid excess calcium with meals']
        },
        'Vitamin D': {
            'issue': 'Low vitamin D affects bone health and immunity',
            'foods': ['Fatty fish (salmon, mackerel)', 'Egg yolks', 'Fortified milk', 'Mushrooms exposed to sunlight'],
            'supplements': ['Vitamin D3 supplement'],
            'actions': ['Increase sun exposure (15-30 min daily)', 'Consume fortified dairy products', 'Consider D3 supplementation']
        },
        'Calcium': {
            'issue': 'Low calcium affects bone development and strength',
            'foods': ['Milk', 'Yogurt', 'Cheese', 'Broccoli', 'Leafy greens', 'Fortified plant-based milks'],
            'supplements': ['Calcium supplement'],
            'actions': ['Consume 3 servings of dairy daily', 'Pair with vitamin D', 'Include weight-bearing exercises']
        },
        'Albumin': {
            'issue': 'Low albumin may indicate protein malnutrition',
            'foods': ['Chicken', 'Fish', 'Eggs', 'Milk', 'Yogurt', 'Beans', 'Nuts'],
            'supplements': ['Protein-rich supplement drinks'],
            'actions': ['Increase protein intake at each meal', 'Include lean meats, dairy, and legumes', 'Consult nutritionist']
        },
        'Protein': {
            'issue': 'Low protein affects muscle and tissue development',
            'foods': ['Chicken breast', 'Fish', 'Eggs', 'Milk products', 'Tofu', 'Beans', 'Nuts'],
            'supplements': ['Protein powder'],
            'actions': ['Eat protein at every meal', 'Include animal and plant sources', 'Aim for 0.8-1g per kg body weight']
        }
    }
    
    high_test_reco = {
        'Glucose': {
            'issue': 'High glucose levels increase diabetes risk',
            'foods': ['Whole grains', 'Vegetables', 'Legumes', 'Berries', 'Nuts', 'Greek yogurt'],
            'supplements': ['Chromium', 'Cinnamon'],
            'actions': ['Reduce simple sugars and refined carbs', 'Increase fiber intake', 'Exercise regularly', 'Monitor portion sizes']
        },
        'Total Cholesterol': {
            'issue': 'High cholesterol increases cardiovascular disease risk',
            'foods': ['Oats', 'Olive oil', 'Avocado', 'Fatty fish', 'Nuts', 'Berries'],
            'supplements': ['Omega-3 (fish oil)', 'Fiber supplement'],
            'actions': ['Replace saturated fats with unsaturated', 'Increase soluble fiber', 'Exercise 30 min daily', 'Reduce processed foods']
        },
        'Ldl': {
            'issue': 'High LDL (bad cholesterol) is harmful to heart',
            'foods': ['Fatty fish', 'Olive oil', 'Almonds', 'Oat bran', 'Beans', 'Garlic'],
            'supplements': ['Omega-3 supplement', 'Plant sterols'],
            'actions': ['Eat more omega-3 sources', 'Reduce saturated fat', 'Increase oats and beans', 'Cut trans fats entirely']
        },
        'Triglycerides': {
            'issue': 'High triglycerides raise heart disease risk',
            'foods': ['Fish (salmon, sardines)', 'Olive oil', 'Whole grains', 'Berries', 'Leafy greens'],
            'supplements': ['Omega-3 (EPA/DHA)', 'Niacin'],
            'actions': ['Reduce refined carbs and sugar', 'Limit alcohol', 'Exercise regularly', 'Maintain healthy weight']
        },
        'Hemoglobin': {
            'issue': 'High hemoglobin may indicate dehydration or polycythemia',
            'foods': ['Water-rich foods', 'Fruits', 'Vegetables', 'Broth'],
            'supplements': [],
            'actions': ['Increase water intake', 'Reduce salt intake', 'Check hydration status', 'Consult doctor']
        }
    }
    
    # Generate recommendations based on assessments
    for assessment in assessments:
        test_name = assessment['test']
        status = assessment['status']
        
        if status == 'LOW' and test_name in low_test_reco:
            reco = low_test_reco[test_name]
            recommendations.append({
                'test': test_name,
                'status': status,
                'issue': reco['issue'],
                'foods': reco['foods'],
                'supplements': reco['supplements'],
                'actions': reco['actions']
            })
        elif status == 'HIGH' and test_name in high_test_reco:
            reco = high_test_reco[test_name]
            recommendations.append({
                'test': test_name,
                'status': status,
                'issue': reco['issue'],
                'foods': reco['foods'],
                'supplements': reco['supplements'],
                'actions': reco['actions']
            })
    
    # Age-specific guidance
    age_guidance = get_age_specific_guidance(age_category)
    
    return {
        'test_recommendations': recommendations,
        'age_guidance': age_guidance,
        'general_tips': get_general_nutrition_tips(age_category),
        'follow_up': 'Consult with a healthcare provider or registered dietitian for personalized medical advice.'
    }


def get_age_specific_guidance(age_category):
    """Return age-specific nutrition guidance."""
    guidance = {
        'toddler': {
            'focus': 'Critical growth and brain development (ages 1-3)',
            'key_nutrients': ['Iron', 'Calcium', 'Vitamin D', 'Protein', 'Zinc'],
            'daily_meals': '3 meals + 2-3 snacks',
            'tips': [
                'Introduce a variety of foods to develop taste preferences',
                'Offer whole milk (until age 2) for brain development',
                'Include iron-rich foods to prevent anemia',
                'Serve soft, age-appropriate portions',
                'Watch for food allergies'
            ]
        },
        'child': {
            'focus': 'Sustained growth and active lifestyle (ages 4-8)',
            'key_nutrients': ['Calcium', 'Iron', 'Protein', 'Vitamins A, C, D'],
            'daily_meals': '3 meals + 1-2 snacks',
            'tips': [
                'Model healthy eating habits',
                'Offer nutrient-dense foods regularly',
                'Limit added sugars and salt',
                'Ensure calcium intake for strong bones',
                'Include physical activity with meals'
            ]
        },
        'teen': {
            'focus': 'Rapid growth, hormonal changes, and future health (ages 9-18)',
            'key_nutrients': ['Calcium', 'Iron', 'Protein', 'Vitamin D', 'Iodine'],
            'daily_meals': '3 meals + 1-2 snacks',
            'tips': [
                'Adolescents need increased calories and nutrients',
                'Emphasize bone-building foods (dairy, fortified plants)',
                'Provide iron-rich foods (especially important for girls)',
                'Support healthy weight and body image',
                'Encourage physical activity and water intake'
            ]
        },
        'adult': {
            'focus': 'Maintaining health and preventing chronic diseases (ages 19-65)',
            'key_nutrients': ['Protein', 'Fiber', 'Antioxidants', 'Omega-3s', 'Whole grains'],
            'daily_meals': '3 meals (with balanced macronutrients)',
            'tips': [
                'Focus on whole foods over processed options',
                'Balance macronutrients: protein, healthy fats, complex carbs',
                'Increase dietary fiber for digestive health',
                'Monitor sodium and added sugars',
                'Maintain regular physical activity and hydration'
            ]
        },
        'senior': {
            'focus': 'Maintaining independence and managing age-related conditions (65+)',
            'key_nutrients': ['Protein', 'Calcium', 'Vitamin D', 'Vitamin B12', 'Fiber'],
            'daily_meals': '3 meals (easier to chew, digest)',
            'tips': [
                'Choose nutrient-dense foods due to reduced calorie needs',
                'Include protein to maintain muscle mass',
                'Ensure adequate calcium and vitamin D for bone health',
                'Increase fiber to prevent constipation',
                'Stay hydrated (thirst mechanism decreases with age)',
                'Consider softer preparations if chewing is difficult'
            ]
        }
    }
    
    return guidance.get(age_category, guidance['adult'])


def get_general_nutrition_tips(age_category):
    """Return general nutrition tips for all ages."""
    return [
        '🥗 Eat a variety of colorful fruits and vegetables (at least 5 servings daily)',
        '🥛 Include protein sources at each meal (meat, fish, eggs, dairy, legumes)',
        '🌾 Choose whole grains over refined grains when possible',
        '💧 Drink adequate water throughout the day (half your body weight in ounces)',
        '🚫 Limit added sugars, salt, and ultra-processed foods',
        '⏰ Eat regular meals and snacks to maintain stable blood sugar',
        '🏃 Combine nutrition with regular physical activity',
        '😴 Ensure adequate sleep (affects metabolism and health)',
        '📋 Keep a food diary to track patterns and identify deficiencies',
        '👨‍⚕️ Consult healthcare providers for personalized nutrition plans'
    ]


def generate_meal_plan_recommendation(recommendations, age_category):
    """Generate a sample meal plan based on deficiencies found."""
    meal_plans = {
        'toddler': {
            'breakfast': ['Oatmeal with mashed banana and whole milk', 'Soft scrambled eggs with toast', 'Fortified cereal with milk'],
            'mid_morning': ['Soft cheese cubes', 'Yogurt', 'Apple puree'],
            'lunch': ['Ground turkey with vegetables', 'Pasta with mild tomato sauce', 'Lentil soup'],
            'afternoon': ['Whole grain crackers with cheese', 'Berries', 'Milk'],
            'dinner': ['Soft-cooked chicken with sweet potato', 'Fish with rice', 'Bean and vegetable stew']
        },
        'child': {
            'breakfast': ['Oatmeal with berries', 'Scrambled eggs with whole wheat toast', 'Whole grain cereal'],
            'mid_morning': ['Apple with almond butter', 'Cheese stick', 'Yogurt'],
            'lunch': ['Chicken sandwich on whole wheat', 'Turkey and bean chili', 'Tuna salad'],
            'afternoon': ['Hummus with vegetables', 'Trail mix', 'Fruit smoothie'],
            'dinner': ['Baked salmon with broccoli', 'Lean beef tacos', 'Lentil and vegetable stew']
        },
        'teen': {
            'breakfast': ['Greek yogurt with granola and berries', 'Whole wheat pancakes', 'Vegetable omelet'],
            'mid_morning': ['Banana with peanut butter', 'Nuts and dried fruit', 'Protein bar'],
            'lunch': ['Grilled chicken breast with quinoa', 'Vegetable-packed sandwich', 'Tuna and rice bowl'],
            'afternoon': ['Greek yogurt with nuts', 'Fruit and cheese', 'Protein shake'],
            'dinner': ['Salmon fillet with sweet potato and broccoli', 'Lean ground turkey with whole wheat pasta', 'Stir-fried tofu with vegetables']
        },
        'adult': {
            'breakfast': ['Vegetable and cheese omelet', 'Overnight oats with chia seeds', 'Greek yogurt with nuts'],
            'mid_morning': ['Mixed nuts and berries', 'Protein smoothie', 'Whole grain crackers with hummus'],
            'lunch': ['Grilled chicken with quinoa and vegetables', 'Salmon salad', 'Chickpea curry with brown rice'],
            'afternoon': ['Almonds and apple', 'Greek yogurt', 'Vegetable and hummus'],
            'dinner': ['Lean beef stir-fry with vegetables', 'Baked fish with roasted vegetables', 'Lentil and vegetable soup']
        },
        'senior': {
            'breakfast': ['Soft-cooked scrambled eggs', 'Oatmeal with mashed berries', 'Yogurt with soft granola'],
            'mid_morning': ['Banana with yogurt', 'Soft cheese', 'Applesauce'],
            'lunch': ['Ground turkey with soft vegetables', 'Fish and sweet potato', 'Chicken soup'],
            'afternoon': ['Custard or pudding', 'Yogurt', 'Soft fruit'],
            'dinner': ['Slow-cooked stew', 'Baked salmon with vegetables', 'Lentil soup with bread']
        }
    }
    
    return meal_plans.get(age_category, meal_plans['adult'])
