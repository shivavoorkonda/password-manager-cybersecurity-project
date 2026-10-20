"""
evaluate_model.py - Evaluate password strength models and generate figures.

Compares 4 approaches: Rule-based, zxcvbn, Random Forest, XGBoost
Evaluates on both standard test split AND clean multi-source test set.
"""

import argparse
import os
import re
import pandas as pd
import numpy as np
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, roc_curve, auc
)
from sklearn.preprocessing import label_binarize
from sklearn.model_selection import train_test_split
from zxcvbn import zxcvbn
from features import extract_all_features


def rule_based_predict(password: str) -> int:
    """Map the current React rule meter to weak/medium/strong (0/1/2)."""
    if not password:
        return 0
    raw_score = int(len(password) >= 12)
    raw_score += int(bool(re.search(r'[A-Z]', password)))
    raw_score += int(bool(re.search(r'[a-z]', password)))
    raw_score += int(bool(re.search(r'[0-9]', password)))
    raw_score += int(bool(re.search(r'[^A-Za-z0-9]', password)))
    ui_score = min(4, raw_score * 4 // 5)
    if ui_score <= 1:
        return 0
    if ui_score == 2:
        return 1
    return 2


def zxcvbn_predict(password: str) -> int:
    """zxcvbn scores 0-4 mapped to 0-2."""
    try:
        res = zxcvbn(password if password else "")
        z = res['score']
        if z <= 1: return 0
        if z <= 3: return 1
        return 2
    except:
        return 0


def evaluate(y_true, y_pred):
    """Compute accuracy and macro F1."""
    acc = accuracy_score(y_true, y_pred)
    _, _, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='macro', zero_division=0)
    _, _, per_f1, _ = precision_recall_fscore_support(y_true, y_pred, average=None, labels=[0,1,2], zero_division=0)
    return {'acc': acc, 'f1': f1, 'per_f1': per_f1}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset-path', type=str, default='../../datasets/combined_train.csv')
    parser.add_argument('--clean-test-path', type=str, default='../../datasets/clean_test.csv')
    parser.add_argument('--dict-path', type=str, default='../../datasets/dictionary.txt')
    parser.add_argument('--models-dir', type=str, default='models')
    parser.add_argument('--figures-dir', type=str, default='../../report/figures')
    args = parser.parse_args()

    figures_dir = args.figures_dir
    os.makedirs(figures_dir, exist_ok=True)

    # Load dictionary
    dictionary = set()
    try:
        with open(args.dict_path, 'r', encoding='utf-8', errors='ignore') as f:
            dictionary = {line.strip().lower() for line in f if line.strip()}
        print(f"Dictionary: {len(dictionary):,} entries")
    except FileNotFoundError:
        print("No dictionary found, proceeding without.")

    # Load models
    print("Loading models...")
    rf_model = joblib.load(os.path.join(args.models_dir, 'rf_model.joblib'))
    xgb_model = joblib.load(os.path.join(args.models_dir, 'xgb_model.joblib'))
    feature_names = joblib.load(os.path.join(args.models_dir, 'feature_names.joblib'))
    print("  Models loaded.")

    # ===== EVALUATION 1: Standard test split =====
    print("\n" + "="*60)
    print("EVALUATION 1: Standard Test Split")
    print("="*60)

    df = pd.read_csv(args.dataset_path, on_bad_lines='skip')
    df['password'] = df['password'].fillna('').astype(str)
    df = df.dropna(subset=['strength'])
    df['strength'] = df['strength'].astype(int)

    print(f"Extracting features for {len(df):,} passwords...")
    X = pd.DataFrame([extract_all_features(p, dictionary) for p in df['password']])
    y = df['strength'].values

    _, X_temp, _, y_temp = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
    _, X_test, _, y_test = train_test_split(X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42)
    passwords_test = df.iloc[X_test.index]['password'].values

    rf_preds = rf_model.predict(X_test)
    xgb_preds = xgb_model.predict(X_test)
    rf_probs = rf_model.predict_proba(X_test)
    xgb_probs = xgb_model.predict_proba(X_test)

    print("Running rule-based and zxcvbn...")
    rule_preds = np.array([rule_based_predict(p) for p in passwords_test])
    zxcvbn_preds = np.array([zxcvbn_predict(p) for p in passwords_test])

    results = {
        'Rule-Based': evaluate(y_test, rule_preds),
        'zxcvbn': evaluate(y_test, zxcvbn_preds),
        'Random Forest': evaluate(y_test, rf_preds),
        'XGBoost': evaluate(y_test, xgb_preds),
    }

    # ===== EVALUATION 2: Clean multi-source test set =====
    clean_results = None
    try:
        clean_df = pd.read_csv(args.clean_test_path, on_bad_lines='skip')
        clean_df['password'] = clean_df['password'].fillna('').astype(str)
        clean_df = clean_df.dropna(subset=['strength'])
        clean_df['strength'] = clean_df['strength'].astype(int)

        print(f"\n{'='*60}")
        print(f"EVALUATION 2: Clean Multi-Source Test ({len(clean_df):,} passwords)")
        print(f"{'='*60}")
        if 'source' in clean_df.columns:
            print("Sources:", dict(clean_df['source'].value_counts()))

        X_clean = pd.DataFrame([extract_all_features(p, dictionary) for p in clean_df['password']])
        y_clean = clean_df['strength'].values
        pw_clean = clean_df['password'].values

        rf_clean = rf_model.predict(X_clean)
        xgb_clean = xgb_model.predict(X_clean)
        rule_clean = np.array([rule_based_predict(p) for p in pw_clean])
        zxcvbn_clean = np.array([zxcvbn_predict(p) for p in pw_clean])

        clean_results = {
            'Rule-Based': evaluate(y_clean, rule_clean),
            'zxcvbn': evaluate(y_clean, zxcvbn_clean),
            'Random Forest': evaluate(y_clean, rf_clean),
            'XGBoost': evaluate(y_clean, xgb_clean),
        }
    except FileNotFoundError:
        print(f"\n[SKIP] Clean test set not found at {args.clean_test_path}")

    # ===== GENERATE FIGURES =====
    print(f"\nGenerating figures to {figures_dir}/...")

    # 1. Confusion matrices
    for preds, name, fname in [(rf_preds, 'Random Forest', 'confusion_matrix_rf.png'),
                                (xgb_preds, 'XGBoost', 'confusion_matrix_xgb.png')]:
        cm = confusion_matrix(y_test, preds, labels=[0,1,2])
        plt.figure(figsize=(8,6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['Weak','Medium','Strong'],
                    yticklabels=['Weak','Medium','Strong'])
        plt.title(f'{name} - Confusion Matrix', fontsize=14)
        plt.ylabel('True'); plt.xlabel('Predicted')
        plt.tight_layout()
        plt.savefig(os.path.join(figures_dir, fname), dpi=150)
        plt.close()
        print(f"  Saved {fname}")

    # 2. ROC curves
    y_bin = label_binarize(y_test, classes=[0,1,2])
    colors = ['#e74c3c','#f39c12','#27ae60']
    labels = ['Weak','Medium','Strong']
    plt.figure(figsize=(10,8))
    for i in range(3):
        fpr, tpr, _ = roc_curve(y_bin[:,i], rf_probs[:,i])
        plt.plot(fpr, tpr, color=colors[i], linestyle='-', linewidth=2,
                 label=f'RF {labels[i]} (AUC={auc(fpr,tpr):.3f})')
        fpr2, tpr2, _ = roc_curve(y_bin[:,i], xgb_probs[:,i])
        plt.plot(fpr2, tpr2, color=colors[i], linestyle='--', linewidth=2,
                 label=f'XGB {labels[i]} (AUC={auc(fpr2,tpr2):.3f})')
    plt.plot([0,1],[0,1],'k--',alpha=0.5)
    plt.xlabel('FPR'); plt.ylabel('TPR')
    plt.title('ROC-AUC (One-vs-Rest)', fontsize=14)
    plt.legend(loc='lower right'); plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'roc_curve.png'), dpi=150)
    plt.close()
    print("  Saved roc_curve.png")

    # 3. Feature importance
    fig, axes = plt.subplots(1, 2, figsize=(16,8))
    for ax, model, title, color in [(axes[0], rf_model, 'Random Forest', '#3498db'),
                                     (axes[1], xgb_model, 'XGBoost', '#e67e22')]:
        imp = model.feature_importances_
        idx = np.argsort(imp)[-15:]
        ax.barh(range(len(idx)), imp[idx], color=color)
        ax.set_yticks(range(len(idx)))
        ax.set_yticklabels([feature_names[i] for i in idx])
        ax.set_title(f'{title} - Top 15 Features')
        ax.set_xlabel('Importance')
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'feature_importance.png'), dpi=150)
    plt.close()
    print("  Saved feature_importance.png")

    # 4. Comparison bar chart
    use_results = clean_results if clean_results else results
    chart_title = 'Clean Test Set' if clean_results else 'Standard Test'
    names = list(use_results.keys())
    accs = [use_results[n]['acc']*100 for n in names]
    f1s = [use_results[n]['f1']*100 for n in names]
    x = np.arange(len(names)); w = 0.35
    fig, ax = plt.subplots(figsize=(12,6))
    b1 = ax.bar(x-w/2, accs, w, label='Accuracy (%)', color='#3498db')
    b2 = ax.bar(x+w/2, f1s, w, label='Macro F1 (%)', color='#e67e22')
    for b in b1:
        ax.text(b.get_x()+b.get_width()/2., b.get_height()+0.5, f'{b.get_height():.1f}',
                ha='center', fontsize=10)
    for b in b2:
        ax.text(b.get_x()+b.get_width()/2., b.get_height()+0.5, f'{b.get_height():.1f}',
                ha='center', fontsize=10)
    ax.set_ylabel('Score (%)'); ax.set_title(f'Model Comparison ({chart_title})', fontsize=14)
    ax.set_xticks(x); ax.set_xticklabels(names); ax.legend()
    ax.set_ylim(0,110); ax.grid(axis='y',alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'comparison_bar_chart.png'), dpi=150)
    plt.close()
    print("  Saved comparison_bar_chart.png")

    # ===== PRINT TABLES =====
    print(f"\n{'='*80}")
    print("TABLE 7.1: Standard Test Split")
    print(f"{'='*80}")
    print(f"| {'Model':<16} | {'Accuracy':>9} | {'Macro F1':>9} |")
    print(f"|{'-'*18}|{'-'*11}|{'-'*11}|")
    for n, m in results.items():
        print(f"| {n:<16} | {m['acc']*100:>8.2f}% | {m['f1']*100:>8.2f}% |")

    print(f"\nPer-Class F1:")
    print(f"| {'Model':<16} | {'Weak':>8} | {'Medium':>8} | {'Strong':>8} |")
    print(f"|{'-'*18}|{'-'*10}|{'-'*10}|{'-'*10}|")
    for n, m in results.items():
        print(f"| {n:<16} | {m['per_f1'][0]*100:>7.2f}% | {m['per_f1'][1]*100:>7.2f}% | {m['per_f1'][2]*100:>7.2f}% |")

    if clean_results:
        print(f"\n{'='*80}")
        print("TABLE 7.1b: Clean Multi-Source Test Set")
        print(f"{'='*80}")
        print(f"| {'Model':<16} | {'Accuracy':>9} | {'Macro F1':>9} |")
        print(f"|{'-'*18}|{'-'*11}|{'-'*11}|")
        for n, m in clean_results.items():
            print(f"| {n:<16} | {m['acc']*100:>8.2f}% | {m['f1']*100:>8.2f}% |")

        print(f"\nPer-Class F1 (Clean):")
        print(f"| {'Model':<16} | {'Weak':>8} | {'Medium':>8} | {'Strong':>8} |")
        print(f"|{'-'*18}|{'-'*10}|{'-'*10}|{'-'*10}|")
        for n, m in clean_results.items():
            print(f"| {n:<16} | {m['per_f1'][0]*100:>7.2f}% | {m['per_f1'][1]*100:>7.2f}% | {m['per_f1'][2]*100:>7.2f}% |")

    print(f"\n{'='*80}")
    print(f"Figures saved to: {os.path.abspath(figures_dir)}")
    print("Copy the tables above into Section 7 of your report.")
    print(f"{'='*80}")


if __name__ == '__main__':
    main()
