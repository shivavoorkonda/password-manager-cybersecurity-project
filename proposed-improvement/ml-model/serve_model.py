import csv
import json
import os
import hashlib
import requests
import joblib
import pandas as pd
import secrets
import string
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
        if model_name == 'rf' and hasattr(model, 'n_jobs'):
            # A single interactive prediction gains nothing from a worker pool;
            # keep inference reliable on Windows and constrained environments.
            model.n_jobs = 1
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


def _model_result(password: str):
    """Classify a password without retaining or logging it."""
    if model is None:
        return None
    features = extract_all_features(password, dictionary)
    frame = pd.DataFrame([features])
    if feature_names:
        for name in feature_names:
            if name not in frame.columns:
                frame[name] = 0
        frame = frame[feature_names]
    prediction_input = frame.to_numpy() if model_name == 'rf' else frame
    prediction = int(model.predict(prediction_input)[0])
    probabilities = model.predict_proba(prediction_input)[0]
    return {
        "strength": prediction,
        "confidence": float(probabilities[prediction]),
        "features": features,
    }


def _parse_password_tokens(password: str) -> dict:
    """Separate a password into non-sensitive structural components."""
    return {
        "words": re.findall(r'[A-Za-z]+', password),
        "numbers": re.findall(r'\d+', password),
        "symbols": re.findall(r'[^A-Za-z0-9]', password),
        "original": password,
    }


_ALPHABET = string.ascii_letters + string.digits
_SYMBOLS = '!#$%&*+-=?@^_'


def _random_token(length: int = 5) -> str:
    return ''.join(secrets.choice(_ALPHABET) for _ in range(length))


def _leet(value: str) -> str:
    substitutions = {'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '$', 't': '7'}
    return ''.join(substitutions.get(char.lower(), char) for char in value)


def _mutate_password(tokens: dict, strategy: int) -> str:
    """Create a style-preserving candidate with CSPRNG-generated additions."""
    words = ''.join(tokens['words']) or 'Secure'
    numbers = ''.join(tokens['numbers']) or str(secrets.randbelow(9000) + 1000)
    symbols = ''.join(tokens['symbols']) or secrets.choice(_SYMBOLS)
    title_word = words[:1].upper() + words[1:]
    tail = secrets.choice(_SYMBOLS) + _random_token(secrets.choice(range(4, 7)))
    if strategy == 0:
        return f'{title_word}{symbols}{numbers}{tail}'
    if strategy == 1:
        return f'{_leet(words)}{secrets.choice(_SYMBOLS)}{numbers}{tail}'
    if strategy == 2:
        return f'{secrets.choice(_SYMBOLS)}{_random_token(4)}_{title_word}{symbols}{numbers}'
    if strategy == 3:
        shuffled_word = ''.join(
            char.upper() if secrets.randbelow(2) else char.lower() for char in words
        )
        return f'{numbers}{secrets.choice(_SYMBOLS)}{shuffled_word}{symbols}{tail}'
    year = str(2000 + secrets.randbelow(27))
    return f'{title_word[:1]}{secrets.choice(_SYMBOLS)}{title_word[1:]}{year}_{_random_token(6)}'


def _validate_candidate(candidate: str):
    """Return only candidates the installed model calls Strong at >= 85%."""
    result = _model_result(candidate)
    if result and result['strength'] == 2 and result['confidence'] >= 0.85:
        return {"password": candidate, "label": "strong", "confidence": result['confidence']}
    return None

@app.route('/api/predict', methods=['POST'])
def predict():
    password, error = parse_password_payload()
    if error:
        return error
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500
    result = _model_result(password)
    labels = ["weak", "medium", "strong"]
    return jsonify({
        "strength": result['strength'],
        "label": labels[result['strength']],
        "confidence": result['confidence'],
        "model": "Random Forest" if model_name == 'rf' else "XGBoost",
        "features": result['features']
    })


@app.route('/api/recommend', methods=['POST'])
def recommend():
    """Return up to three style-preserving, model-validated suggestions."""
    password, error = parse_password_payload()
    if error:
        return error
    if model is None:
        return jsonify({"error": "Model not loaded"}), 503

    input_result = _model_result(password)
    tokens = _parse_password_tokens(password)
    recommendations = []
    seen = {password}
    for strategy in range(5):
        for _ in range(10):
            candidate = _mutate_password(tokens, strategy)
            if candidate in seen:
                continue
            seen.add(candidate)
            validated = _validate_candidate(candidate)
            if validated:
                recommendations.append(validated)
                break
        if len(recommendations) == 3:
            break

    labels = ["weak", "medium", "strong"]
    return jsonify({
        "input_strength": {
            "label": labels[input_result['strength']],
            "confidence": input_result['confidence'],
        },
        "recommendations": recommendations,
        "strategy": "Kept your base word and numbers; added length and unpredictable characters.",
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
    ml_res = _model_result(password)
        
    labels = ["weak", "medium", "strong"]
    ml_pred = ml_res.get('strength') if ml_res else None
    if breach_res.get('breached'):
        consensus = 0
    elif ml_pred is None:
        consensus = z_pred
    elif ml_pred == 0:
        consensus = 0
    elif ml_pred == 2 and z_pred == 2:
        consensus = 2
    else:
        consensus = 1
    
    return jsonify({
        "breach_check": breach_res,
        "rule_based": {"strength": rule_pred, "label": labels[rule_pred]},
        "zxcvbn": {"strength": z_pred, "label": labels[z_pred], "raw_score": z_score},
        "ml_model": {
            "strength": ml_res.get("strength", 0),
            "label": labels[ml_res.get("strength", 0)] if ml_res else "unknown",
            "confidence": ml_res.get("confidence"),
            "model": "Random Forest" if model_name == 'rf' else "XGBoost" if model_name else None,
        },
        "consensus": {
            "strength": consensus,
            "label": labels[consensus],
            "ml_available": ml_pred is not None,
        },
    })

if __name__ == '__main__':
    # The model endpoint accepts plaintext passwords; bind to loopback only.
    app.run(host='127.0.0.1', port=5000)
