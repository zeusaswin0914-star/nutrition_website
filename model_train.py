
# model_train.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib

def generate_synthetic(n=1200, seed=1):
    rng = np.random.RandomState(seed)
    age = rng.randint(18, 75, size=n)
    sex = rng.choice([0,1], size=n)  # 0 female, 1 male
    weight = rng.normal(70, 15, size=n).clip(40, 130)
    height = rng.normal(165, 10, size=n).clip(140, 200)
    activity = rng.choice([0,1,2], size=n)  # 0 sedentary,1 moderate,2 active

    hemoglobin = rng.normal(14 - 1.5*(1-sex), 1.2, size=n)
    ferritin = rng.normal(80, 40, size=n).clip(5, 400)
    vit_d = rng.normal(25, 10, size=n).clip(4, 80)
    b12 = rng.normal(350, 120, size=n).clip(100, 1200)
    fasting_glucose = rng.normal(95, 20, size=n).clip(60, 300)
    hba1c = (fasting_glucose/150)*5.5 + rng.normal(0,0.4,size=n)
    total_chol = rng.normal(180, 40, size=n).clip(100, 350)
    ldl = (total_chol*0.6 + rng.normal(0,20,size=n)).clip(50,300)
    hdl = rng.normal(50, 12, size=n).clip(20,100)
    triglycerides = rng.normal(120,60,size=n).clip(30,800)

    # calorie target
    bmr = 10*weight + 6.25*height - 5*age + (5 - 161*(1-sex))
    activity_factor = np.array([1.2,1.45,1.65])[activity]
    calories = (bmr * activity_factor * (1 + (0.02*(hba1c-5.5)))) + rng.normal(0,150,size=n)

    df = pd.DataFrame({
        "age":age,"sex":sex,"weight":weight,"height":height,"activity":activity,
        "hemoglobin":hemoglobin,"ferritin":ferritin,"vit_d":vit_d,"b12":b12,
        "fasting_glucose":fasting_glucose,"hba1c":hba1c,
        "total_chol":total_chol,"ldl":ldl,"hdl":hdl,"triglycerides":triglycerides,
        "calories":calories
    })
    return df

def train_and_save():
    # Load cleaned biomarker data
    df = pd.read_csv("lab_clean_processed.csv")

    n = len(df)
    rng = np.random.RandomState(42)
    # Synthetically generate demographics
    df["age"] = rng.randint(18, 75, size=n)
    df["sex"] = rng.choice([0, 1], size=n)  # 0=female, 1=male
    df["weight"] = rng.normal(70, 15, size=n).clip(40, 130)
    df["height"] = rng.normal(165, 10, size=n).clip(140, 200)
    df["activity"] = rng.choice([0, 1, 2], size=n)  # 0=sedentary, 1=moderate, 2=active

    # Calculate synthetic calorie target using Mifflin-St Jeor
    bmr = 10 * df["weight"] + 6.25 * df["height"] - 5 * df["age"] + (5 - 161 * (1 - df["sex"]))
    activity_factor = np.array([1.2, 1.45, 1.65])[df["activity"]]
    df["calories"] = bmr * activity_factor + rng.normal(0, 150, size=n)

    # Use all columns except 'calories' as features
    X = df.drop(columns=["calories"])
    y = df["calories"]
    num_cols = X.columns.tolist()

    X_train, X_test, y_train, y_test = train_test_split(X[num_cols], y, test_size=0.2, random_state=1)

    model = make_pipeline(
        StandardScaler(),
        RandomForestRegressor(n_estimators=100, random_state=1)
    )

    model.fit(X_train, y_train)

    # Save model, feature names, and medians
    joblib.dump(
        (model, num_cols, df[num_cols].median().to_dict()),
        "calorie_model.pkl"
    )

    print("✔ calorie_model.pkl created successfully!")

if __name__ == "__main__":
    train_and_save()
