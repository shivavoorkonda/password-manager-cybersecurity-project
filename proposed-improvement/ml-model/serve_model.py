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
DICTIONARY_PATH = os.path.join(DATASET_DIR, 'dictionary.txt')
try:
    with open(DICTIONARY_PATH, 'r', encoding='utf-8', errors='ignore') as dictionary_file:
        dictionary = {line.strip().lower() for line in dictionary_file if line.strip()}
    print(f"Loaded {len(dictionary):,} dictionary entries.")
except OSError:
    dictionary = set()
    print(f"Dictionary unavailable at {DICTIONARY_PATH}; dictionary_hit will be zero.")
try:
    xgb_model = joblib.load(os.path.join(MODEL_DIR, 'xgb_model.joblib'))
    feature_names = joblib.load(os.path.join(MODEL_DIR, 'feature_names.joblib'))
    print("Model loaded successfully.")
except Exception as e:
    print(f"Warning: Model not found. Did you run train_model.py? Error: {e}")
    xgb_model = None
    feature_names = None

def rule_based_predict(password: str) -> int:
    score = 0
    if len(password) >= 8: score += 1
    if len(password) >= 12: score += 1
    if re.search(r'[A-Z]', password): score += 1
    if re.search(r'[a-z]', password): score += 1
    if re.search(r'\d', password): score += 1
    if re.search(r'[^A-Za-z0-9]', password): score += 1
    if score < 3: return 0
    if score < 5: return 1
    return 2

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

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
    
    if xgb_model is None:
        return jsonify({"error": "Model not loaded"}), 500
        
    # Ensure correct feature order
    X = pd.DataFrame([features])
    if feature_names:
        for fn in feature_names:
            if fn not in X.columns:
                X[fn] = 0
        X = X[feature_names]
        
    pred = int(xgb_model.predict(X)[0])
    probs = xgb_model.predict_proba(X)[0]
    confidence = float(probs[pred])
    
    labels = ["weak", "medium", "strong"]
    
    return jsonify({
        "strength": pred,
        "label": labels[pred],
        "confidence": confidence,
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
    if xgb_model:
        features = extract_all_features(password, dictionary)
        X = pd.DataFrame([features])
        if feature_names:
            for fn in feature_names:
                if fn not in X.columns:
                    X[fn] = 0
            X = X[feature_names]
        pred = int(xgb_model.predict(X)[0])
        ml_res = {"strength": pred, "features": features}
        
    labels = ["weak", "medium", "strong"]
    
    return jsonify({
        "breach_check": breach_res,
        "rule_based": {"strength": rule_pred, "label": labels[rule_pred]},
        "zxcvbn": {"strength": z_pred, "label": labels[z_pred], "raw_score": z_score},
        "ml_model": {"strength": ml_res.get("strength", 0), "label": labels[ml_res.get("strength", 0)] if ml_res else "unknown"}
    })

if __name__ == '__main__':
    # The model endpoint accepts plaintext passwords; bind to loopback only.
    app.run(host='127.0.0.1', port=5000)
