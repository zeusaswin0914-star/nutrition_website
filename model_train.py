
# model_train.py
import argparse
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    accuracy_score,
    f1_score,
    confusion_matrix,
)
import matplotlib.pyplot as plt
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

def train_and_save(data_path: str, label_col: str, classification: bool = False, threshold: float | None = None):
    """
    Train a model using a real label column from `data_path`.

    - If `classification` is False: performs regression and saves regression metrics/plots.
    - If `classification` is True: binarizes using `threshold` (median if None) and trains a classifier,
      reporting accuracy, F1 and confusion matrix.
    """
    df = pd.read_csv(data_path)

    if label_col not in df.columns:
        print(f"ERROR: label column '{label_col}' not found in {data_path}")
        print("Please provide a labeled CSV with the target column (no synthetic data will be used).")
        sys.exit(1)

    # Keep only numeric features for modelling; warn if any non-numeric columns are dropped
    y = df[label_col]
    X = df.drop(columns=[label_col])
    numeric_X = X.select_dtypes(include=[np.number]).copy()
    dropped = set(X.columns) - set(numeric_X.columns)
    if dropped:
        print(f"Note: dropped non-numeric columns: {sorted(dropped)}")

    # Drop rows with missing values in features or label
    keep = numeric_X.columns.tolist() + [label_col]
    df_clean = df[keep].dropna()
    if df_clean.empty:
        print("ERROR: no rows remain after dropping NA values in features/label. Check your CSV.")
        sys.exit(1)

    X_clean = df_clean[numeric_X.columns]
    y_clean = df_clean[label_col]

    X_train, X_test, y_train, y_test = train_test_split(X_clean, y_clean, test_size=0.2, random_state=1)

    if classification:
        from sklearn.ensemble import RandomForestClassifier

        if threshold is None:
            threshold = y_train.median()
            print(f"Binarizing labels using median threshold: {threshold}")

        y_train_bin = (y_train >= threshold).astype(int)
        y_test_bin = (y_test >= threshold).astype(int)

        model = make_pipeline(StandardScaler(), RandomForestClassifier(n_estimators=100, random_state=1))
        model.fit(X_train, y_train_bin)

        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)

        train_acc = accuracy_score(y_train_bin, y_train_pred)
        test_acc = accuracy_score(y_test_bin, y_test_pred)
        test_f1 = f1_score(y_test_bin, y_test_pred)
        cm = confusion_matrix(y_test_bin, y_test_pred)

        print("\n" + "=" * 60)
        print("CLASSIFICATION METRICS (BINARY)")
        print("=" * 60)
        print(f"Train Accuracy: {train_acc:.4f}")
        print(f"Test Accuracy : {test_acc:.4f}")
        print(f"Test F1 Score : {test_f1:.4f}")
        print("Confusion Matrix (test):")
        print(cm)
        print("=" * 60 + "\n")

        # Save confusion matrix plot
        fig, ax = plt.subplots(figsize=(5, 4))
        im = ax.imshow(cm, cmap='Blues')
        ax.set_xlabel('Predicted')
        ax.set_ylabel('Actual')
        ax.set_title('Confusion Matrix (test)')
        for (i, j), val in np.ndenumerate(cm):
            ax.text(j, i, int(val), ha='center', va='center', color='black')
        plt.colorbar(im, ax=ax)
        plt.tight_layout()
        plt.savefig('confusion_matrix.png', dpi=200, bbox_inches='tight')
        print("✔ Saved: confusion_matrix.png")

    else:
        model = make_pipeline(StandardScaler(), RandomForestRegressor(n_estimators=100, random_state=1))
        model.fit(X_train, y_train)

        y_train_pred = model.predict(X_train)
        y_test_pred = model.predict(X_test)

        train_mse = mean_squared_error(y_train, y_train_pred)
        train_rmse = np.sqrt(train_mse)
        train_mae = mean_absolute_error(y_train, y_train_pred)
        train_r2 = r2_score(y_train, y_train_pred)

        test_mse = mean_squared_error(y_test, y_test_pred)
        test_rmse = np.sqrt(test_mse)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        test_r2 = r2_score(y_test, y_test_pred)

        print("\n" + "=" * 60)
        print("REGRESSION METRICS - CALORIE PREDICTION")
        print("=" * 60)
        print(f"R² Score (Train):      {train_r2:.4f}")
        print(f"MSE (Train Loss):      {train_mse:.2f}")
        print(f"RMSE (Train Loss):     {train_rmse:.2f} calories")
        print(f"MAE (Train Error):     {train_mae:.2f} calories")
        print(f"\nR² Score (Test):       {test_r2:.4f}")
        print(f"MSE (Validation Loss): {test_mse:.2f}")
        print(f"RMSE (Validation Loss):{test_rmse:.2f} calories")
        print(f"MAE (Test Error):      {test_mae:.2f} calories")
        print("=" * 60 + "\n")

        # Visualizations
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Model Performance Metrics - Calorie Prediction', fontsize=16, fontweight='bold')

        # Train actual vs predicted
        ax = axes[0, 0]
        ax.scatter(y_train, y_train_pred, alpha=0.6, color='blue', edgecolors='k', linewidth=0.5)
        ax.plot([y_train.min(), y_train.max()], [y_train.min(), y_train.max()], 'r--', lw=2)
        ax.set_xlabel('Actual Calories')
        ax.set_ylabel('Predicted Calories')
        ax.set_title(f'Train: Actual vs Predicted (R²={train_r2:.4f})')
        ax.grid(True, alpha=0.3)

        # Test actual vs predicted
        ax = axes[0, 1]
        ax.scatter(y_test, y_test_pred, alpha=0.6, color='green', edgecolors='k', linewidth=0.5)
        ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
        ax.set_xlabel('Actual Calories')
        ax.set_ylabel('Predicted Calories')
        ax.set_title(f'Test: Actual vs Predicted (R²={test_r2:.4f})')
        ax.grid(True, alpha=0.3)

        # Train residuals
        ax = axes[1, 0]
        residuals_train = y_train - y_train_pred
        ax.scatter(y_train_pred, residuals_train, alpha=0.6, color='blue', edgecolors='k', linewidth=0.5)
        ax.axhline(y=0, color='r', linestyle='--')
        ax.set_xlabel('Predicted Calories')
        ax.set_ylabel('Residuals')
        ax.set_title(f'Train Residuals (RMSE={train_rmse:.2f})')
        ax.grid(True, alpha=0.3)

        # Test residuals
        ax = axes[1, 1]
        residuals_test = y_test - y_test_pred
        ax.scatter(y_test_pred, residuals_test, alpha=0.6, color='green', edgecolors='k', linewidth=0.5)
        ax.axhline(y=0, color='r', linestyle='--')
        ax.set_xlabel('Predicted Calories')
        ax.set_ylabel('Residuals')
        ax.set_title(f'Test Residuals (RMSE={test_rmse:.2f})')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('model_performance_metrics.png', dpi=300, bbox_inches='tight')
        print('✔ Saved: model_performance_metrics.png')

        # Summary bar plot
        fig, ax = plt.subplots(figsize=(10, 5))
        metrics_names = ['R2', 'RMSE', 'MAE']
        train_vals = [train_r2, train_rmse, train_mae]
        test_vals = [test_r2, test_rmse, test_mae]
        x = np.arange(len(metrics_names))
        width = 0.35
        bars1 = ax.bar(x - width/2, train_vals, width, label='Train', color='skyblue', edgecolor='black')
        bars2 = ax.bar(x + width/2, test_vals, width, label='Test', color='lightgreen', edgecolor='black')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics_names)
        ax.set_title('Model Performance Comparison')
        ax.legend()
        for bars in [bars1, bars2]:
            for bar in bars:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., h, f'{h:.2f}', ha='center', va='bottom', fontsize=9)
        plt.tight_layout()
        plt.savefig('model_metrics_comparison.png', dpi=300, bbox_inches='tight')
        print('✔ Saved: model_metrics_comparison.png')

    # Save model, feature names, and medians
    num_cols = X_clean.columns.tolist()
    joblib.dump((model, num_cols, df_clean[num_cols].median().to_dict()), 'calorie_model.pkl')
    print('✔ Saved: calorie_model.pkl')


def parse_args():
    p = argparse.ArgumentParser(description='Train model using real labels (no synthetic data).')
    p.add_argument('--data', default='lab_clean_processed.csv', help='Path to CSV with features and label')
    p.add_argument('--label', default='calories', help='Name of the target/label column')
    p.add_argument('--classify', action='store_true', help='Run binary classification (requires --label)')
    p.add_argument('--threshold', type=float, default=None, help='Threshold to binarize numeric label (if classifying). Defaults to train median')
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    train_and_save(args.data, args.label, classification=args.classify, threshold=args.threshold)
