import csv
import json
import os
import hashlib
import requests
import joblib
import pandas as pd
from flask import Flask, request, jsonify
from features import extract_all_features
from zxcvbn import zxcvbn
import re

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024

# Load model on startup
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
DATASET_DIR = os.path.abspath(os.path.join(MODEL_DIR, '..', '..', '..', 'datasets'))
MODEL_DICTIONARY_PATH = os.path.join(MODEL_DIR, 'dictionary.txt')
DATASET_DICTIONARY_PATH = os.path.join(DATASET_DIR, 'dictionary.txt')
METADATA_PATH = os.path.join(MODEL_DIR, 'training_metadata.json')
COMPARISON_PATH = os.path.join(MODEL_DIR, 'model_comparison.csv')
DICTIONARY_PATH = (MODEL_DICTIONARY_PATH if os.path.isfile(MODEL_DICTIONARY_PATH)
                   else DATASET_DICTIONARY_PATH)
try:
    with open(DICTIONARY_PATH, 'r', encoding='utf-8', errors='ignore') as dictionary_file:
        dictionary = {line.strip().lower() for line in dictionary_file if line.strip()}
    print(f"Loaded {len(dictionary):,} dictionary entries.")
except OSError:
    dictionary = set()
    print(f"Dictionary unavailable at {DICTIONARY_PATH}; dictionary_hit will be zero.")
try:
    with open(METADATA_PATH, 'r', encoding='utf-8') as metadata_file:
        training_metadata = json.load(metadata_file)
except (OSError, json.JSONDecodeError):
    training_metadata = {}

def select_model_name():
    """Choose the highest macro-F1 model whose artifact is in this package."""
    available = training_metadata.get('available_models')
    if not isinstance(available, list):
        # Old model bundles may contain XGBoost only; never load an unrelated
        # Random Forest file left over from an earlier training run.
        available = ['xgb']
    scores = {}
    try:
        with open(COMPARISON_PATH, newline='', encoding='utf-8') as comparison_file:
            for row in csv.DictReader(comparison_file):
                model_name = row.get('Model', '').strip().lower()
                try:
                    score = float(row.get('Macro F1 (%)', ''))
                except (TypeError, ValueError):
                    continue
                if 'random forest' in model_name:
                    scores['rf'] = score
                elif 'xgboost' in model_name:
                    scores['xgb'] = score
    except OSError:
        pass
    candidates = [name for name in available if name in ('rf', 'xgb') and (
        (name == 'rf' and os.path.isfile(os.path.join(MODEL_DIR, 'rf_model.joblib')))
        or (name == 'xgb' and (
            os.path.isfile(os.path.join(MODEL_DIR, 'xgb_model.json'))
            or os.path.isfile(os.path.join(MODEL_DIR, 'xgb_model.joblib'))
        ))
    )]
    if not candidates:
        return None
    return max(candidates, key=lambda name: scores.get(name, float('-inf')))

model_name = select_model_name()
model = None
feature_names = None
if model_name:
    try:
        if model_name == 'xgb' and os.path.isfile(os.path.join(MODEL_DIR, 'xgb_model.json')):
            from xgboost import XGBClassifier
            model = XGBClassifier()
            model.load_model(os.path.join(MODEL_DIR, 'xgb_model.json'))
        else:
            model = joblib.load(os.path.join(MODEL_DIR, f'{model_name}_model.joblib'))
        feature_names = joblib.load(os.path.join(MODEL_DIR, 'feature_names.joblib'))
        print(f"Loaded {model_name.upper()} model with {len(feature_names)} features.")
    except Exception as e:
        print(f"Warning: Could not load the packaged model: {e}")
        model = None
        model_name = None
else:
    print("Warning: No packaged trained model found. Add a Kaggle model ZIP to models/.")

def rule_based_predict(password: str) -> int:
    """Match the existing React meter and group its five levels into weak/medium/strong."""
    if not password:
        return 0
    raw_score = int(len(password) >= 12)
    raw_score += int(bool(re.search(r'[A-Z]', password)))
    raw_score += int(bool(re.search(r'[a-z]', password)))
    raw_score += int(bool(re.search(r'[0-9]', password)))
    raw_score += int(bool(re.search(r'[^A-Za-z0-9]', password)))
    ui_score = min(4, int(raw_score * 4 / 5))
    if ui_score <= 1:
        return 0
    if ui_score == 2:
        return 1
    return 2

@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "model_loaded": model is not None,
        "model": model_name,
        "feature_count": len(feature_names) if feature_names else 0,
        "dictionary_entries": len(dictionary),
    })

def parse_password_payload():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('password'), str):
        return None, (jsonify({"error": "password must be a string"}), 400)
    if not data['password']:
        return None, (jsonify({"error": "password must not be empty"}), 400)
    return data['password'], None

@app.route('/api/predict', methods=['POST'])
def predict():
    password, error = parse_password_payload()
    if error:
        return error
    features = extract_all_features(password, dictionary)
    
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500
        
    # Ensure correct feature order
    X = pd.DataFrame([features])
    if feature_names:
        for fn in feature_names:
            if fn not in X.columns:
                X[fn] = 0
        X = X[feature_names]
        
    pred = int(model.predict(X)[0])
    probs = model.predict_proba(X)[0]
    confidence = float(probs[pred])
    
    labels = ["weak", "medium", "strong"]
    
    return jsonify({
        "strength": pred,
        "label": labels[pred],
        "confidence": confidence,
        "model": "Random Forest" if model_name == 'rf' else "XGBoost",
        "features": features
    })

@app.route('/api/check-breach', methods=['POST'])
def check_breach():
    password, error = parse_password_payload()
    if error:
        return error
    sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    
    try:
        response = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=5)
        if response.status_code == 200:
            for line in response.text.splitlines():
                if ':' not in line:
                    continue
                h, count = line.split(':', 1)
                if h == suffix:
                    return jsonify({"breached": True, "count": int(count)})
        if response.status_code != 200:
            return jsonify({"error": f"HIBP returned HTTP {response.status_code}"}), 502
        return jsonify({"breached": False, "count": 0})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    password, error = parse_password_payload()
    if error:
        return error
    
    # 1. Breach check
    breach_res = {"breached": False, "count": 0}
    try:
        sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]
        response = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=2)
        if response.status_code == 200:
            for line in response.text.splitlines():
                if ':' not in line:
                    continue
                h, count = line.split(':', 1)
                if h == suffix:
                    breach_res = {"breached": True, "count": int(count)}
                    break
        elif response.status_code != 200:
            breach_res = {"error": f"HIBP returned HTTP {response.status_code}"}
    except requests.RequestException:
        breach_res = {"error": "HIBP check unavailable"}
        
    # 2. Rule based
    rule_pred = rule_based_predict(password)
    
    # 3. zxcvbn
    z_res = zxcvbn(password)
    z_score = z_res['score']
    z_pred = 0 if z_score <= 1 else (1 if z_score <= 3 else 2)
    
    # 4. ML Model
    ml_res = {}
    if model is not None:
        features = extract_all_features(password, dictionary)
        X = pd.DataFrame([features])
        if feature_names:
            for fn in feature_names:
                if fn not in X.columns:
                    X[fn] = 0
            X = X[feature_names]
        pred = int(model.predict(X)[0])
        probabilities = model.predict_proba(X)[0]
        ml_res = {"strength": pred, "confidence": float(probabilities[pred]), "features": features}
        
    labels = ["weak", "medium", "strong"]
    
    return jsonify({
        "breach_check": breach_res,
        "rule_based": {"strength": rule_pred, "label": labels[rule_pred]},
        "zxcvbn": {"strength": z_pred, "label": labels[z_pred], "raw_score": z_score},
        "ml_model": {
            "strength": ml_res.get("strength", 0),
            "label": labels[ml_res.get("strength", 0)] if ml_res else "unknown",
            "confidence": ml_res.get("confidence"),
            "model": "Random Forest" if model_name == 'rf' else "XGBoost" if model_name else None,
        }
    })

if __name__ == '__main__':
    # The model endpoint accepts plaintext passwords; bind to loopback only.
    app.run(host='127.0.0.1', port=5000)
