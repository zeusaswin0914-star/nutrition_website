"""
Model Training V2 for Health Status Classification
Trains multiple ML models and selects the best performer.
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
import warnings
warnings.filterwarnings('ignore')

# Try to import XGBoost (optional)
try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("[WARN] XGBoost not available. Skipping XGBoost model.")

# Feature columns used for training
FEATURE_COLUMNS = ['HGP', 'SGP', 'UAP', 'CEP', 'NAPSI', 'SKPSI', 'CLPSI', 
                   'TBP', 'VAP', 'VEP', 'VCP', 'FOP', 'FEP', 'TCP']

TARGET_COLUMN = 'health_status'


def load_processed_data(data_path: str = None) -> tuple:
    """
    Load preprocessed data and split into features/target.
    """
    if data_path is None:
        data_path = Path(__file__).parent / 'processed_data_v2.csv'
    
    print(f"[LOAD] Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    
    # Select available feature columns
    available_features = [c for c in FEATURE_COLUMNS if c in df.columns]
    print(f"  Using {len(available_features)} features: {available_features}")
    
    X = df[available_features].copy()
    y = df[TARGET_COLUMN].copy()
    
    # Encode target labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    print(f"  Classes: {list(label_encoder.classes_)}")
    print(f"  Class distribution: {dict(zip(label_encoder.classes_, np.bincount(y_encoded)))}")
    
    return X, y_encoded, label_encoder, available_features


def get_models():
    """
    Define models to train and compare.
    """
    models = {
        'LogisticRegression': LogisticRegression(
            C=1.0,
            max_iter=1000,
            class_weight='balanced',
            random_state=42
        ),
        'RandomForest': RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        ),
        'GradientBoosting': GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
    }
    
    if XGBOOST_AVAILABLE:
        models['XGBoost'] = XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            use_label_encoder=False,
            eval_metric='mlogloss'
        )
    
    return models


def train_and_evaluate_models(X, y, label_encoder):
    """
    Train all models and evaluate with cross-validation.
    """
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    print(f"\n[SPLIT] Train: {len(X_train)} samples, Test: {len(X_test)} samples")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Get models
    models = get_models()
    results = {}
    
    print("\n" + "=" * 70)
    print("MODEL TRAINING AND EVALUATION")
    print("=" * 70)
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    for name, model in models.items():
        print(f"\n[TRAIN] {name}...")
        
        # Train
        model.fit(X_train_scaled, y_train)
        
        # Predict
        y_train_pred = model.predict(X_train_scaled)
        y_test_pred = model.predict(X_test_scaled)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=cv, scoring='accuracy')
        
        # Metrics
        train_acc = accuracy_score(y_train, y_train_pred)
        test_acc = accuracy_score(y_test, y_test_pred)
        precision = precision_score(y_test, y_test_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_test_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_test_pred, average='weighted', zero_division=0)
        
        results[name] = {
            'model': model,
            'scaler': scaler,
            'train_accuracy': train_acc,
            'test_accuracy': test_acc,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'y_test_pred': y_test_pred
        }
        
        print(f"  Train Accuracy: {train_acc:.4f}")
        print(f"  Test Accuracy:  {test_acc:.4f}")
        print(f"  CV Accuracy:    {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")
        print(f"  Precision:      {precision:.4f}")
        print(f"  Recall:         {recall:.4f}")
        print(f"  F1 Score:       {f1:.4f}")
    
    return results, X_test, y_test, scaler


def select_best_model(results: dict) -> str:
    """
    Select the best model based on test accuracy and F1 score.
    Prioritize interpretability for healthcare applications.
    """
    print("\n" + "=" * 70)
    print("MODEL COMPARISON SUMMARY")
    print("=" * 70)
    
    # Print comparison table
    print(f"\n{'Model':<20} {'Test Acc':<10} {'CV Mean':<10} {'F1 Score':<10} {'Precision':<10} {'Recall':<10}")
    print("-" * 70)
    
    for name, metrics in results.items():
        print(f"{name:<20} {metrics['test_accuracy']:.4f}     {metrics['cv_mean']:.4f}     "
              f"{metrics['f1_score']:.4f}     {metrics['precision']:.4f}      {metrics['recall']:.4f}")
    
    print("-" * 70)
    
    # Select best based on weighted score (accuracy + F1)
    # Slight preference for interpretable models in healthcare
    interpretability_bonus = {
        'LogisticRegression': 0.02,  # Most interpretable
        'RandomForest': 0.01,        # Feature importance available
        'GradientBoosting': 0.00,
        'XGBoost': 0.00
    }
    
    best_name = None
    best_score = -1
    
    for name, metrics in results.items():
        # Combined score: 50% accuracy, 30% F1, 20% CV stability
        score = (
            0.50 * metrics['test_accuracy'] +
            0.30 * metrics['f1_score'] +
            0.20 * (1 - metrics['cv_std'])  # Lower std = more stable
        )
        score += interpretability_bonus.get(name, 0)
        
        if score > best_score:
            best_score = score
            best_name = name
    
    return best_name


def save_model(results: dict, best_name: str, feature_columns: list, 
               label_encoder, output_path: str = None) -> str:
    """
    Save the best model along with metadata.
    """
    if output_path is None:
        output_path = Path(__file__).parent / 'model_v2.pkl'
    
    best_result = results[best_name]
    
    # Create model artifact
    model_artifact = {
        'model': best_result['model'],
        'scaler': best_result['scaler'],
        'feature_columns': feature_columns,
        'label_encoder': label_encoder,
        'model_name': best_name,
        'metrics': {
            'accuracy': best_result['test_accuracy'],
            'f1_score': best_result['f1_score'],
            'precision': best_result['precision'],
            'recall': best_result['recall'],
            'cv_mean': best_result['cv_mean'],
            'cv_std': best_result['cv_std']
        }
    }
    
    # Get medians for imputation during inference
    data_path = Path(__file__).parent / 'processed_data_v2.csv'
    if data_path.exists():
        df = pd.read_csv(data_path)
        available_features = [c for c in feature_columns if c in df.columns]
        model_artifact['medians'] = df[available_features].median().to_dict()
    
    joblib.dump(model_artifact, output_path)
    print(f"\n[SAVE] Model saved to {output_path}")
    
    return str(output_path)


def print_classification_report(results: dict, best_name: str, 
                               y_test: np.ndarray, label_encoder):
    """
    Print detailed classification report for best model.
    """
    y_pred = results[best_name]['y_test_pred']
    
    print("\n" + "=" * 70)
    print(f"CLASSIFICATION REPORT - {best_name}")
    print("=" * 70)
    
    report = classification_report(
        y_test, y_pred,
        target_names=label_encoder.classes_,
        zero_division=0
    )
    print(report)
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"{'':>15}", end='')
    for cls in label_encoder.classes_:
        print(f"{cls:>12}", end='')
    print()
    
    for i, row in enumerate(cm):
        print(f"{label_encoder.classes_[i]:>15}", end='')
        for val in row:
            print(f"{val:>12}", end='')
        print()


def train_model_v2():
    """
    Main training pipeline.
    """
    print("=" * 70)
    print("ML MODEL TRAINING V2")
    print("=" * 70)
    
    # First, ensure preprocessed data exists
    processed_path = Path(__file__).parent / 'processed_data_v2.csv'
    if not processed_path.exists():
        print("[INFO] Preprocessed data not found. Running preprocessing...")
        from data_preprocessing_v2 import preprocess_nhanes_data
        preprocess_nhanes_data()
    
    # Load data
    X, y, label_encoder, feature_columns = load_processed_data()
    
    # Train and evaluate models
    results, X_test, y_test, scaler = train_and_evaluate_models(X, y, label_encoder)
    
    # Select best model
    best_name = select_best_model(results)
    print(f"\n[OK] BEST MODEL SELECTED: {best_name}")
    print(f"  Accuracy: {results[best_name]['test_accuracy']:.4f}")
    print(f"  F1 Score: {results[best_name]['f1_score']:.4f}")
    
    # Print classification report
    print_classification_report(results, best_name, y_test, label_encoder)
    
    # Save model
    model_path = save_model(results, best_name, feature_columns, label_encoder)
    
    # Generate justification
    print("\n" + "=" * 70)
    print("MODEL SELECTION JUSTIFICATION")
    print("=" * 70)
    print(f"""
Selected Model: {best_name}

Reasoning:
1. Achieved {results[best_name]['test_accuracy']:.2%} test accuracy
2. F1 Score of {results[best_name]['f1_score']:.4f} indicates good balance 
   between precision and recall
3. Cross-validation mean accuracy of {results[best_name]['cv_mean']:.2%} 
   with low variance (+/-{results[best_name]['cv_std']*2:.2%}) shows stability
4. Healthcare applications benefit from {"interpretable models that allow " if 'Logistic' in best_name else ""}
   medical professionals to understand predictions

Model File: {model_path}
""")
    
    return results, best_name


if __name__ == '__main__':
    results, best_name = train_model_v2()
    print("\n[DONE] Model training completed successfully!")
