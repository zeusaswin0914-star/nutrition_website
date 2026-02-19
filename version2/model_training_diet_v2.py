"""
Diet Recommendation Model Training V2

Trains a multi-label or multi-output model to recommend food items based on:
- Health Goal (Weight Loss, Gain, Maintenance)
- Dietary Restrictions (Vegetarian, Vegan, None)
- Nutritional needs (Calorie deficit/surplus)

If external dataset is missing, generates a high-quality synthetic dataset of 1000+ food items.
"""

import pandas as pd
import numpy as np
import joblib
import logging
import os
import random
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
MODEL_PATH = r"c:\Users\USER\project\version2\diet_model_v2.pkl"
DIET_DATA_PATH = r"c:\Users\USER\project\version2\diet_dataset.csv"

# Synthetic Data Generation (Fallback)
COMMON_FOODS = {
    'Vegetarian': [
        ('Spinach Salad', 150, 10, 5, 2, 'Weight Loss'),
        ('Oatmeal with Berries', 250, 40, 5, 8, 'Maintenance'),
        ('Lentil Soup', 300, 45, 18, 5, 'Weight Loss'),
        ('Quinoa Bowl', 400, 60, 15, 10, 'Muscle Gain'),
        ('Greek Yogurt Parfait', 200, 20, 15, 6, 'Weight Loss'),
        ('Paneer Tikka', 350, 10, 20, 25, 'Muscle Gain'),
        ('Chickpea Curry', 380, 50, 12, 12, 'Maintenance'),
        ('Brown Rice & Veggies', 320, 65, 8, 4, 'Weight Loss'),
        ('Avocado Toast', 280, 30, 8, 15, 'Maintenance'),
        ('Protein Shake (Whey)', 180, 5, 25, 2, 'Muscle Gain'),
        ('Vegetable Stir Fry', 220, 25, 5, 10, 'Weight Loss'),
        ('Tofu Scramble', 260, 10, 20, 15, 'Weight Loss'),
        ('Dal Tadka', 250, 35, 12, 8, 'Maintenance'),
        ('Rajma Masala', 300, 40, 14, 9, 'Muscle Gain'),
        ('Vegetable Biryani', 450, 70, 9, 15, 'Maintenance'),
    ],
    'Vegan': [
        ('Kale Smoothie', 180, 35, 5, 2, 'Weight Loss'),
        ('Tofu Stir Fry', 280, 20, 18, 12, 'Weight Loss'),
        ('Vegan Chili', 320, 45, 15, 8, 'Maintenance'),
        ('Seitan Steak', 350, 15, 40, 10, 'Muscle Gain'),
        ('Hummus & Carrots', 200, 20, 6, 10, 'Weight Loss'),
        ('Soy Milk Smoothie', 190, 25, 12, 4, 'Maintenance'),
        ('Lentil Loaf', 310, 30, 18, 10, 'Muscle Gain'),
        ('Fruit Salad', 120, 30, 1, 0, 'Weight Loss'),
        ('Chia Pudding', 220, 20, 8, 12, 'Maintenance'),
        ('Peanut Butter Banana Toast', 350, 40, 10, 16, 'Muscle Gain'),
    ],
    'Non-Vegetarian': [
        ('Grilled Chicken Breast', 250, 0, 50, 5, 'Weight Loss'),
        ('Salmon Fillet', 350, 0, 40, 20, 'Maintenance'),
        ('Chicken Curry', 400, 15, 35, 20, 'Muscle Gain'),
        ('Egg White Omelet', 150, 2, 20, 5, 'Weight Loss'),
        ('Tuna Salad', 220, 5, 30, 8, 'Weight Loss'),
        ('Turkey Sandwich', 320, 35, 25, 10, 'Maintenance'),
        ('Beef Steak', 500, 0, 45, 35, 'Muscle Gain'),
        ('Fish Tacos', 380, 35, 25, 15, 'Maintenance'),
        ('Chicken Biryani', 550, 60, 30, 20, 'Muscle Gain'),
        ('Shrimp Stir Fry', 280, 10, 35, 10, 'Weight Loss'),
        ('Boiled Eggs', 140, 1, 12, 10, 'Weight Loss'),
        ('Chicken Tikka', 320, 8, 40, 14, 'Muscle Gain'),
    ]
}

def generate_synthetic_data(n_samples=2000):
    """Generate a synthetic dataset for diet recommendation."""
    logger.info("Generating synthetic diet data...")
    data = []
    
    # Categories
    goals = ['Weight Loss', 'Maintenance', 'Muscle Gain']
    diets = ['Vegetarian', 'Vegan', 'Non-Vegetarian']
    
    for _ in range(n_samples):
        # Randomly pick user profile
        age = random.randint(18, 70)
        gender = random.choice([0, 1])
        weight = random.randint(50, 120)
        height = random.randint(150, 190)
        bmi = weight / ((height/100)**2)
        
        diet_type = random.choice(diets)
        target_goal = random.choice(goals)
        
        # Select food based on rules
        # Logic: If Weight Loss, pick lower calorie/high protein
        # If Muscle Gain, pick high protein/calorie surplus
        
        # Valid foods for this diet type
        valid_foods = COMMON_FOODS['Vegetarian'] # Base
        if diet_type == 'Vegan':
            valid_foods = COMMON_FOODS['Vegan'] + [f for f in COMMON_FOODS['Vegetarian'] if 'Paneer' not in f[0] and 'Yogurt' not in f[0] and 'Whey' not in f[0]] 
        elif diet_type == 'Non-Vegetarian':
            valid_foods = COMMON_FOODS['Vegetarian'] + COMMON_FOODS['Non-Vegetarian']
            
        # Filter by goal (soft filter)
        goal_foods = [f for f in valid_foods if f[5] == target_goal]
        if not goal_foods: goal_foods = valid_foods
        
        selected_food = random.choice(goal_foods)
        
        # Features: Age, Gender, BMI, Goal(Encoded), Diet(Encoded)
        # Target: Food Name (Multi-class)
        
        data.append({
            'age': age,
            'gender': gender,
            'bmi': bmi,
            'diet_type': diet_type,
            'goal': target_goal,
            'recommended_food': selected_food[0],
            'calories': selected_food[1],
            'protein': selected_food[2],
            'fats': selected_food[3],
            'carbs': selected_food[4]
        })
        
    return pd.DataFrame(data)

def train_diet_model():
    """Train the diet recommendation model."""
    
    # 1. Get Data
    if os.path.exists(DIET_DATA_PATH):
        df = pd.read_csv(DIET_DATA_PATH)
    else:
        df = generate_synthetic_data(2000)
        df.to_csv(DIET_DATA_PATH, index=False)
        
    logger.info(f"Training on {len(df)} samples")
    
    # 2. Preprocessing
    # Transform categorical features
    # Diet Type: Veg=0, Vegan=1, Non-Veg=2
    diet_map = {'Vegetarian': 0, 'Vegan': 1, 'Non-Vegetarian': 2}
    df['diet_encoded'] = df['diet_type'].map(diet_map)
    
    # Goal: Loss=0, Maint=1, Gain=2
    goal_map = {'Weight Loss': 0, 'Maintenance': 1, 'Muscle Gain': 2}
    df['goal_encoded'] = df['goal'].map(goal_map)
    
    X = df[['age', 'gender', 'bmi', 'diet_encoded', 'goal_encoded']]
    y = df['recommended_food']
    
    # 3. Train Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. Models
    # Since it's a classification problem (choosing a food item from list)
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100),
        'XGBoost': XGBClassifier(eval_metric='mlogloss', use_label_encoder=False) if 'XGBClassifier' in globals() else None,
        'KNN': KNeighborsClassifier(n_neighbors=5)
    }
    
    # For XGBoost we need to encode target labels to integers
    # Let's use LabelEncoder for y
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    y_train_enc = le.fit_transform(y_train)
    y_test_enc = le.transform(y_test)
    
    best_acc = 0
    best_model = None
    best_name = ""
    
    for name, model in models.items():
        if model is None: continue
        
        logger.info(f"Training {name}...")
        try:
            model.fit(X_train, y_train_enc)
            acc = model.score(X_test, y_test_enc)
            logger.info(f"{name} Accuracy: {acc:.4f}")
            
            if acc > best_acc:
                best_acc = acc
                best_model = model
                best_name = name
        except Exception as e:
            logger.error(f"Error training {name}: {e}")
            
    # 5. Save Model
    if best_model:
        logger.info(f"Best Diet Model: {best_name} (Acc: {best_acc:.4f})")
        
        pipeline = {
            'model': best_model,
            'label_encoder': le,
            'diet_map': diet_map,
            'goal_map': goal_map,
            'model_name': best_name
        }
        
        joblib.dump(pipeline, MODEL_PATH)
        logger.info(f"Diet model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_diet_model()
