"""
Model Evaluation V2 for Health Status Classification
Generates detailed evaluation metrics and comparison visualizations.
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_curve, auc
)
import warnings
warnings.filterwarnings('ignore')

# Try to import matplotlib for visualizations
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("[WARN] Matplotlib not available. Skipping visualizations.")


def load_model_artifact(model_path: str = None):
    """
    Load the trained model artifact.
    """
    if model_path is None:
        model_path = Path(__file__).parent / 'model_v2.pkl'
    
    if not Path(model_path).exists():
        raise FileNotFoundError(f"Model not found at {model_path}. Run model_training_v2.py first.")
    
    artifact = joblib.load(model_path)
    return artifact


def evaluate_model(artifact: dict):
    """
    Comprehensive model evaluation with detailed metrics.
    """
    print("=" * 70)
    print("MODEL EVALUATION REPORT V2")
    print("=" * 70)
    
    model = artifact['model']
    scaler = artifact['scaler']
    feature_columns = artifact['feature_columns']
    label_encoder = artifact['label_encoder']
    metrics = artifact.get('metrics', {})
    
    print(f"\n[MODEL] {artifact.get('model_name', 'Unknown')}")
    print(f"[FEATURES] {len(feature_columns)} features used")
    print(f"[CLASSES] {list(label_encoder.classes_)}")
    
    # Print stored metrics
    print("\n" + "-" * 50)
    print("STORED EVALUATION METRICS")
    print("-" * 50)
    
    for metric_name, value in metrics.items():
        if isinstance(value, float):
            print(f"  {metric_name}: {value:.4f}")
    
    # Load test data for additional evaluation
    data_path = Path(__file__).parent / 'processed_data_v2.csv'
    if data_path.exists():
        df = pd.read_csv(data_path)
        available_features = [c for c in feature_columns if c in df.columns]
        
        X = df[available_features]
        y = label_encoder.transform(df['health_status'])
        
        _, X_test, _, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42
        )
        
        X_test_scaled = scaler.transform(X_test)
        y_pred = model.predict(X_test_scaled)
        
        # Classification report
        print("\n" + "-" * 50)
        print("DETAILED CLASSIFICATION REPORT")
        print("-" * 50)
        print(classification_report(
            y_test, y_pred,
            target_names=label_encoder.classes_,
            zero_division=0
        ))
        
        # Confusion matrix
        print("\nCONFUSION MATRIX")
        print("-" * 50)
        cm = confusion_matrix(y_test, y_pred)
        
        # Header
        print(f"{'Predicted →':>15}", end='')
        for cls in label_encoder.classes_:
            print(f"{cls:>12}", end='')
        print()
        print("Actual ↓")
        
        for i, row in enumerate(cm):
            print(f"{label_encoder.classes_[i]:>15}", end='')
            for val in row:
                print(f"{val:>12}", end='')
            print()
        
        # Per-class metrics
        print("\n" + "-" * 50)
        print("PER-CLASS PERFORMANCE")
        print("-" * 50)
        
        for i, cls in enumerate(label_encoder.classes_):
            tp = cm[i, i]
            fp = cm[:, i].sum() - tp
            fn = cm[i, :].sum() - tp
            tn = cm.sum() - tp - fp - fn
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            
            print(f"\n{cls}:")
            print(f"  True Positives:  {tp}")
            print(f"  False Positives: {fp}")
            print(f"  False Negatives: {fn}")
            print(f"  Precision:       {precision:.4f}")
            print(f"  Recall:          {recall:.4f}")
            print(f"  Specificity:     {specificity:.4f}")
    
    return metrics


def print_feature_importance(artifact: dict):
    """
    Print feature importance if available.
    """
    model = artifact['model']
    feature_columns = artifact['feature_columns']
    
    print("\n" + "-" * 50)
    print("FEATURE IMPORTANCE")
    print("-" * 50)
    
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        print("\nRanked Features (by importance):")
        for i, idx in enumerate(indices):
            if idx < len(feature_columns):
                print(f"  {i+1}. {feature_columns[idx]}: {importances[idx]:.4f}")
    
    elif hasattr(model, 'coef_'):
        # For logistic regression
        print("\nFeature Coefficients (absolute values):")
        coefs = np.abs(model.coef_).mean(axis=0)  # Average across classes
        indices = np.argsort(coefs)[::-1]
        
        for i, idx in enumerate(indices):
            if idx < len(feature_columns):
                print(f"  {i+1}. {feature_columns[idx]}: {coefs[idx]:.4f}")
    else:
        print("  Feature importance not available for this model type.")


def save_evaluation_plots(artifact: dict, output_dir: str = None):
    """
    Generate and save evaluation visualizations.
    """
    if not MATPLOTLIB_AVAILABLE:
        print("[SKIP] Matplotlib not available for visualizations.")
        return
    
    if output_dir is None:
        output_dir = Path(__file__).parent
    
    model = artifact['model']
    feature_columns = artifact['feature_columns']
    label_encoder = artifact['label_encoder']
    scaler = artifact['scaler']
    
    # Load data
    data_path = Path(__file__).parent / 'processed_data_v2.csv'
    if not data_path.exists():
        print("[SKIP] No data file for generating plots.")
        return
    
    df = pd.read_csv(data_path)
    available_features = [c for c in feature_columns if c in df.columns]
    
    X = df[available_features]
    y = label_encoder.transform(df['health_status'])
    
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    X_test_scaled = scaler.transform(X_test)
    y_pred = model.predict(X_test_scaled)
    
    # Confusion matrix plot
    fig, ax = plt.subplots(figsize=(8, 6))
    cm = confusion_matrix(y_test, y_pred)
    im = ax.imshow(cm, cmap='Blues')
    
    ax.set_xticks(np.arange(len(label_encoder.classes_)))
    ax.set_yticks(np.arange(len(label_encoder.classes_)))
    ax.set_xticklabels(label_encoder.classes_)
    ax.set_yticklabels(label_encoder.classes_)
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')
    ax.set_title(f'Confusion Matrix - {artifact.get("model_name", "V2 Model")}')
    
    for i in range(len(label_encoder.classes_)):
        for j in range(len(label_encoder.classes_)):
            ax.text(j, i, str(cm[i, j]), ha='center', va='center', color='black')
    
    plt.colorbar(im, ax=ax)
    plt.tight_layout()
    
    cm_path = Path(output_dir) / 'confusion_matrix_v2.png'
    plt.savefig(cm_path, dpi=150)
    plt.close()
    print(f"\n[PLOT] Saved confusion matrix to {cm_path}")
    
    # Feature importance plot (if available)
    if hasattr(model, 'feature_importances_'):
        fig, ax = plt.subplots(figsize=(10, 6))
        importances = model.feature_importances_
        indices = np.argsort(importances)
        
        ax.barh(range(len(indices)), importances[indices], color='steelblue')
        ax.set_yticks(range(len(indices)))
        ax.set_yticklabels([feature_columns[i] if i < len(feature_columns) else f'Feature_{i}' 
                           for i in indices])
        ax.set_xlabel('Importance')
        ax.set_title('Feature Importance')
        plt.tight_layout()
        
        fi_path = Path(output_dir) / 'feature_importance_v2.png'
        plt.savefig(fi_path, dpi=150)
        plt.close()
        print(f"[PLOT] Saved feature importance to {fi_path}")


def compare_with_v1():
    """
    Compare V2 model performance with V1 model if available.
    """
    v1_path = Path(__file__).parent.parent / 'calorie_model.pkl'
    v2_path = Path(__file__).parent / 'model_v2.pkl'
    
    print("\n" + "=" * 70)
    print("VERSION COMPARISON")
    print("=" * 70)
    
    if v1_path.exists():
        try:
            v1_artifact = joblib.load(v1_path)
            print("\n[V1 Model] Found calorie_model.pkl")
            print("  Type: Regression (calorie prediction)")
            # V1 is a regression model, direct comparison not possible
            print("  Note: V1 is a regression model, V2 is classification.")
            print("  V2 provides categorical health status instead of numeric calories.")
        except:
            print("[V1] Could not load V1 model for comparison.")
    else:
        print("[V1] No V1 model found for comparison.")
    
    if v2_path.exists():
        v2_artifact = joblib.load(v2_path)
        metrics = v2_artifact.get('metrics', {})
        print(f"\n[V2 Model] model_v2.pkl")
        print(f"  Type: Classification (health status)")
        print(f"  Model: {v2_artifact.get('model_name', 'Unknown')}")
        print(f"  Accuracy: {metrics.get('accuracy', 'N/A')}")
        print(f"  F1 Score: {metrics.get('f1_score', 'N/A')}")
    
    print("\n[IMPROVEMENT] V2 provides:")
    print("  - Multi-class health status (Normal/At Risk/Deficient)")
    print("  - Clinically interpretable categories")
    print("  - Gender and age-aware normalization")
    print("  - Proper sentinel value handling from NHANES data")


def run_evaluation():
    """
    Main evaluation pipeline.
    """
    # Load model
    try:
        artifact = load_model_artifact()
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        print("[INFO] Please run model_training_v2.py first.")
        return
    
    # Evaluate model
    evaluate_model(artifact)
    
    # Feature importance
    print_feature_importance(artifact)
    
    # Save plots
    save_evaluation_plots(artifact)
    
    # Compare with V1
    compare_with_v1()
    
    print("\n" + "=" * 70)
    print("✓ EVALUATION COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    run_evaluation()
