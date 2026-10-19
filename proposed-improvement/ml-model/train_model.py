"""
train_model.py - Train password strength classifier models.

Trains Random Forest and XGBoost on combined_train.csv with dictionary-corrected labels.
"""

import argparse
import os
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import xgboost as xgb
import joblib

from features import extract_all_features


def load_dictionary(dict_path: str) -> set:
    """Load merged dictionary."""
    dictionary = set()
    try:
        with open(dict_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                stripped = line.strip().lower()
                if stripped:
                    dictionary.add(stripped)
        print(f"Loaded dictionary: {len(dictionary):,} entries from {dict_path}")
    except FileNotFoundError:
        print(f"Warning: Dictionary not found at {dict_path}.")
    return dictionary


def prepare_data(df: pd.DataFrame, dictionary_set: set) -> tuple:
    """Extract features for all passwords and return X and y."""
    features_list = []

    df = df.copy()
    df['password'] = df['password'].fillna('').astype(str)
    df = df.dropna(subset=['strength'])
    df['strength'] = df['strength'].astype(int)

    total = len(df)
    print(f"Extracting features for {total:,} passwords...")
    for i, pwd in enumerate(df['password']):
        if (i + 1) % 100000 == 0:
            print(f"  Progress: {i+1:,}/{total:,} ({(i+1)/total*100:.1f}%)")
        feats = extract_all_features(pwd, dictionary_set)
        features_list.append(feats)

    X = pd.DataFrame(features_list)
    y = df['strength'].values

    return X, y


def main():
    parser = argparse.ArgumentParser(description='Train password strength models.')
    parser.add_argument('--dataset-path', type=str,
                        default='../../datasets/combined_train.csv',
                        help='Path to training dataset')
    parser.add_argument('--dict-path', type=str,
                        default='../../datasets/dictionary.txt',
                        help='Path to merged dictionary')
    parser.add_argument('--output-dir', type=str, default='models',
                        help='Directory to save trained models')

    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Loading dataset from {args.dataset_path}...")
    try:
        df = pd.read_csv(args.dataset_path, on_bad_lines='skip')
    except FileNotFoundError:
        fallback = '../../datasets/password_strength.csv'
        print(f"Not found. Trying fallback: {fallback}")
        df = pd.read_csv(fallback, on_bad_lines='skip')

    df['password'] = df['password'].fillna('').astype(str)
    df = df.dropna(subset=['strength'])
    df['strength'] = df['strength'].astype(int)

    print(f"Dataset loaded: {len(df):,} rows")
    for cls in sorted(df['strength'].unique()):
        count = (df['strength'] == cls).sum()
        label = {0: 'Weak', 1: 'Medium', 2: 'Strong'}.get(cls, f'Class {cls}')
        print(f"  {label} ({cls}): {count:,} ({count/len(df)*100:.1f}%)")

    # Load dictionary
    dictionary = load_dictionary(args.dict_path)

    # Extract features
    X, y = prepare_data(df, dictionary)

    # Split: 70% train, 15% validation, 15% test
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.3, stratify=y, random_state=42
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42
    )

    print(f"\nSplit sizes:")
    print(f"  Train: {X_train.shape[0]:,}")
    print(f"  Val:   {X_val.shape[0]:,}")
    print(f"  Test:  {X_test.shape[0]:,}")

    # Train Random Forest
    print("\n" + "="*60)
    print("Training Random Forest (n_estimators=200, max_depth=20)...")
    print("="*60)
    rf_model = RandomForestClassifier(
        n_estimators=200, max_depth=20, random_state=42, n_jobs=-1
    )
    rf_model.fit(X_train, y_train)

    rf_test_preds = rf_model.predict(X_test)
    print("\nRandom Forest - Test Set:")
    print(classification_report(y_test, rf_test_preds, target_names=['Weak', 'Medium', 'Strong']))

    # Train XGBoost
    print("\n" + "="*60)
    print("Training XGBoost (n_estimators=200, max_depth=8, lr=0.1)...")
    print("="*60)
    xgb_model = xgb.XGBClassifier(
        n_estimators=200, max_depth=8, learning_rate=0.1,
        random_state=42, n_jobs=-1, eval_metric='mlogloss'
    )
    xgb_model.fit(X_train, y_train)

    xgb_test_preds = xgb_model.predict(X_test)
    print("\nXGBoost - Test Set:")
    print(classification_report(y_test, xgb_test_preds, target_names=['Weak', 'Medium', 'Strong']))

    # Feature Importance
    print("\n" + "="*60)
    print("Top 15 Feature Importances (Random Forest)")
    print("="*60)
    importances = rf_model.feature_importances_
    indices = np.argsort(importances)[::-1]
    feature_names = list(X.columns)
    for i in range(min(15, len(feature_names))):
        print(f"  {i+1:2d}. {feature_names[indices[i]]:<25s} {importances[indices[i]]:.4f}")

    # Save models
    print(f"\nSaving models to {args.output_dir}/...")
    joblib.dump(rf_model, os.path.join(args.output_dir, 'rf_model.joblib'))
    joblib.dump(xgb_model, os.path.join(args.output_dir, 'xgb_model.joblib'))
    joblib.dump(feature_names, os.path.join(args.output_dir, 'feature_names.joblib'))

    print("\n" + "="*60)
    print("Training complete! Models saved.")
    print("="*60)


if __name__ == '__main__':
    main()
