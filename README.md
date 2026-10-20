# Secure Password Manager project

Application-based cybersecurity project using the IJRASET paper “Password Manager” as an application-level baseline: Mahesh Kanjikar et al., Volume 13, Issue XII, December 2025, DOI [10.22214/ijraset.2025.76363](https://doi.org/10.22214/ijraset.2025.76363).

The paper describes a password manager and says it includes strength analysis, but it does not define that algorithm or publish classifier accuracy/F1 results. This project adds an app rule meter, zxcvbn, a Random Forest/XGBoost experiment, and a Have I Been Pwned (HIBP) lookup. Do not label the project metrics as paper results.

**Submission report:** [Markdown source](report/ACADEMIC_PROJECT_REPORT.md) | [PDF](output/pdf/secure_password_manager_project_report.pdf). The report follows the instructor's nine sections and records the implementation and evaluation limits.

## What is in this repository

- **React browser vault:** encrypts vault entries with AES-256-GCM and derives the key with PBKDF2-HMAC-SHA256 (600,000 iterations). Encrypted entries are stored in this browser's `localStorage`.
- **Strength panel:** shows the app's rule meter and zxcvbn, and calls the local Flask ML service for an optional trained model prediction.
- **HIBP check:** browser-side SHA-1 k-anonymity range lookup; only the first five hash characters are sent to HIBP.
- **Node/PostgreSQL backend:** separate scaffold; the current frontend vault does not use it for login, storage, or sync.
- **Argon2id benchmark:** standalone PBKDF2-vs-Argon2id timing script. The vault still uses PBKDF2.

This is a class prototype, not an audited production password manager. The ML service receives the password in plaintext over loopback. Do not expose it to a network or enter real account passwords during demos.

## System architecture

The diagram summarizes the browser vault, the local strength-analysis service, and the HIBP range lookup. It also marks the Node/PostgreSQL scaffold as separate because the current browser-vault flow does not use it.

![System architecture of the Secure Password Manager](report/figures/system_architecture.png)

## Latest supplied model comparison

These values came from the `model_comparison.csv` in the ZIP supplied by the project owner. Training used source-derived labels and a held-out split; these numbers are not paper scores or measurements of real-world crack resistance.

| Method | Accuracy (%) | Macro F1 (%) |
|---|---:|---:|
| Existing app rule meter | 69.45 | 62.63 |
| zxcvbn | 84.29 | 84.19 |
| Random Forest | 95.83 | 95.82 |
| XGBoost | 86.65 | 86.07 |

The earlier ZIP omitted the top-scoring Random Forest artifact. The new ZIP at `password-manager-kaggle-model (2).zip` includes RF and portable XGBoost JSON; both artifacts, the 17-feature order, metadata, and the matching dictionary passed integrity checks. The RF model is now installed locally and the API smoke check selected it successfully. Its metadata reports scikit-learn 1.6.1, so use the pinned dependency in `proposed-improvement/ml-model/requirements.txt` when setting up the service. The experiment's common-password lists supply weak labels by source membership, while the strength CSV supplies its own labels, so the evaluation measures agreement with these labels and this split.

## Run the frontend and local ML service

Prerequisites: Node.js 20+, Python 3.10+, and Git. PostgreSQL is not needed for the browser vault or ML panel.

### 1. Start the ML service

In PowerShell, from the repository root:

```powershell
cd proposed-improvement/ml-model
python -m pip install -r requirements.txt
python serve_model.py
```

Keep this terminal open. Visit `http://127.0.0.1:5000/health`. For ML to work, the response must show `"model_loaded": true`; also note the selected model and dictionary entry count. If it says false, the frontend can still run, but its ML panel will show an error until a compatible trained artifact is installed.

### 2. Start the React app

Open a second PowerShell window at the repository root:

```powershell
cd existing-approach/client
npm install
npm run dev
```

Open `http://localhost:5173`. Create a demo vault, add a fake test credential, and confirm the rule meter, zxcvbn, ML result (when loaded), and HIBP status separately. HIBP requires internet access. The vault is local to this browser profile; clearing site data deletes it.

### 3. Check frontend and backend separately

- **Frontend build/type check:** from `existing-approach/client`, run `node node_modules/typescript/bin/tsc --noEmit` and `npm run build`.
- **ML API:** while `serve_model.py` runs, open `http://127.0.0.1:5000/health`. A fake input can be sent with:

  ```powershell
  Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/api/predict -ContentType 'application/json' -Body '{"password":"Example-only-NotARealSecret-482!"}'
  ```

- **Node/PostgreSQL scaffold (optional):** this is not the backend used by the browser vault. It needs a PostgreSQL database and configured `.env` values before it can run. Do not present it as integrated until the frontend is changed to call it and that end-to-end flow is verified.

## Train in Kaggle

Open [`kaggle_password_model_training.ipynb`](proposed-improvement/ml-model/kaggle_password_model_training.ipynb) in Kaggle. Use **Add Data** to attach:

1. `/kaggle/input/datasets/bhavikbb/password-strength-classifier-dataset`
2. `/kaggle/input/datasets/wjburns/common-password-list-rockyoutxt`
3. `/kaggle/input/datasets/shivamb/10000-most-common-passwords`
4. `/kaggle/input/datasets/joebeachcapital/top-10-million-passwords`

Then choose **Run All**. The notebook discovers inputs under `/kaggle/input`, saves checkpoints through preparation/training/evaluation/packaging, and creates `/kaggle/working/password-manager-kaggle-model.zip`. Download that ZIP from Kaggle's Output panel. It should contain `rf_model.joblib`, portable `xgb_model.json`, `feature_names.joblib`, `training_metadata.json`, `model_comparison.csv`, and the matching `dictionary.txt`. Keep the notebook and output private because the dictionary contains password strings. Do not put raw password lists or the dictionary in a public GitHub commit.

For local integration, extract the ZIP into `proposed-improvement/ml-model/models/`, replacing the model artifacts as a matching set. Restart `python serve_model.py`, verify `model_loaded` and `model` at `/health`, then use the UI. Do not mix files from different training runs.

The Kaggle datasets and label/split limitations are described in [`datasets/README.md`](datasets/README.md). The detailed implementation audit is [`README_CYBER_DOMAIN_EXPERT.md`](README_CYBER_DOMAIN_EXPERT.md).

## Optional components

### Node/PostgreSQL scaffold

The Node server at `existing-approach/server` is currently separate from the local browser vault. Its configuration requires PostgreSQL, a `DATABASE_URL`, and a strong `SESSION_SECRET`. The service must not be exposed publicly with development settings.

### Argon2id benchmark

The script at `proposed-improvement/argon2-benchmark/benchmark_kdf.py` is a separate CPU timing experiment. Install its dependencies with `python -m pip install -r requirements.txt` and run `python benchmark_kdf.py` from that directory. The current run on Windows 11 (Intel processor; Python version and platform details are recorded in `report/figures/kdf_benchmark_results.json`) measured median PBKDF2-HMAC-SHA256 at 600,000 iterations as 368.45 ms and Argon2id at 65,536 KiB, t=3, p=1 as 190.27 ms. This compares local derivation latency for the chosen configurations; it does not measure GPU cracking performance or equivalent work. The vault still uses PBKDF2.

## Project map

```text
existing-approach/client/                 React + TypeScript app and local browser vault
existing-approach/server/                 Separate Express/PostgreSQL scaffold
proposed-improvement/ml-model/            Kaggle notebook, feature extraction, Flask API
proposed-improvement/hibp-integration/    Browser HIBP range lookup
proposed-improvement/argon2-benchmark/    Standalone KDF benchmark
datasets/                                 Existing tracked research inputs and notes
report/                                   Academic project report
```

The supplied comparison's Random Forest artifact is installed and was verified through the local Flask API. Its 95.83% accuracy and 95.82% macro-F1 are preliminary results on this source-labelled split, not paper results or real-world crackability measurements. For a live demo, stop any older service already using port 5000 before starting the bundled service so the UI reaches the current artifact.
