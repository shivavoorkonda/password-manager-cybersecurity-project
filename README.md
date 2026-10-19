# Password Manager Security Enhancement Project

## Enhancing Password Manager Security: ML-Based Strength Classification and Breach-Exposure Detection

**Course:** Cyber Security (Application-Based Project)  
**Base Paper:** "Password Manager" (IJRASET, Vol 13, Issue XII, Dec 2025, DOI: 10.22214/ijraset.2025.76363)

---

## Project Overview

This project implements and evaluates a zero-knowledge password manager, identifies its limitations, and proposes three improvements:
1. **ML-Based Password Strength Classifier** (Random Forest + XGBoost) to replace the paper's rule-based meter
2. **Privacy-Preserving Breach Check** using HIBP Pwned Passwords API with k-anonymity
3. **Argon2id vs PBKDF2 Benchmark** comparing key derivation function resistance

---

## Prerequisites

- **Node.js** 20 LTS or later — https://nodejs.org/
- **Python** 3.10+ — https://www.python.org/
- **PostgreSQL** 16 — https://www.postgresql.org/ (optional: the frontend works standalone with localStorage)
- **Git** — https://git-scm.com/

---

## Quick Start

### Step 1: Download Datasets

Download these files into `datasets/`:

| File | Source | Save As |
|------|--------|---------|
| Password Strength Dataset | [Kaggle (bhavikbb)](https://www.kaggle.com/datasets/bhavikbb/password-strength-classifier-dataset) | `datasets/password_strength.csv` |
| RockYou wordlist | [Kaggle](https://www.kaggle.com/datasets/wjburns/common-password-list-rockyoutxt) or Kali Linux | `datasets/rockyou.txt` |

### Step 2: Set Up the Frontend (Existing Approach)

```powershell
cd existing-approach/client
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

### Step 3: Set Up the Backend (Optional — frontend works standalone)

```powershell
# Create PostgreSQL database first
# psql -U postgres -c "CREATE DATABASE password_manager;"

cd existing-approach/server
copy .env.example .env
# Edit .env with your PostgreSQL credentials
npm install
npm run db:push
npm run dev
```

Server runs at `http://localhost:3001`.

### Step 4: Train the ML Model (Proposed Improvement)

```powershell
cd proposed-improvement/ml-model
pip install -r requirements.txt

# Train models (takes 5-15 minutes depending on hardware)
python train_model.py --dataset-path ../../datasets/password_strength.csv --rockyou-path ../../datasets/rockyou.txt

# Evaluate and generate figures
python evaluate_model.py

# Start the ML API server
python serve_model.py
```

ML API runs at `http://localhost:5000`.

### Step 5: Run KDF Benchmark

```powershell
cd proposed-improvement/argon2-benchmark
pip install argon2-cffi matplotlib numpy

python benchmark_kdf.py
```

Results and charts are saved to `report/figures/`.

---

## API Endpoints (ML Server)

| Method | Endpoint | Body | Returns |
|--------|----------|------|---------|
| POST | `/api/predict` | `{"password": "test123"}` | `{"strength": 0, "label": "weak", "confidence": 0.95}` |
| POST | `/api/check-breach` | `{"password": "password"}` | `{"breached": true, "count": 10434572}` |
| POST | `/api/analyze` | `{"password": "P@ssw0rd"}` | Combined analysis from all 4 methods |
| GET | `/health` | — | `{"status": "ok"}` |

---

## Screenshots to Capture for Report

1. Login/Registration screen
2. Password vault view with stored entries
3. Password generator with options
4. Strength meter showing rule-based vs zxcvbn side by side
5. Add password form
6. Database view showing encrypted ciphertext (pgAdmin or psql)
7. ML API response for a weak password (e.g., `P@ssw0rd1!`)
8. ML API response for a strong password
9. HIBP breach check response
10. Generated charts (confusion matrix, ROC curve, feature importance, comparison)
11. KDF benchmark bar chart

---

## Project Structure

```
password-manager-project/
├── existing-approach/
│   ├── client/          # React + TypeScript frontend (17 files)
│   └── server/          # Express.js + PostgreSQL backend (8 files)
├── proposed-improvement/
│   ├── ml-model/        # Python ML pipeline (5 files)
│   ├── hibp-integration/# TypeScript HIBP check module
│   └── argon2-benchmark/# KDF benchmarking script
├── datasets/            # Downloaded datasets (not in git)
├── report/figures/      # Generated charts and graphs
├── PROJECT_STRUCTURE.md
└── README.md            # This file
```

---

## Key Files

| File | Description |
|------|-------------|
| `client/src/lib/crypto.ts` | AES-256-GCM encryption + PBKDF2 key derivation |
| `client/src/lib/strengthChecker.ts` | Rule-based + zxcvbn strength checkers |
| `server/src/schema.ts` | PostgreSQL schema (Drizzle ORM) |
| `ml-model/features.py` | 15-feature extraction from passwords |
| `ml-model/train_model.py` | Random Forest + XGBoost training |
| `ml-model/evaluate_model.py` | Metrics, confusion matrix, ROC, comparison |
| `ml-model/serve_model.py` | Flask API with ML + HIBP endpoints |
| `hibp-integration/hibp_check.ts` | Client-side k-anonymity breach check |
| `argon2-benchmark/benchmark_kdf.py` | PBKDF2 vs Argon2id timing comparison |
