# Security and project audit

This file records what the repository implements and what the evidence supports. It is an implementation audit, not a claim that the prototype is production-ready.

## Base paper

The reference is Mahesh Kanjikar et al., “Password Manager,” IJRASET, Volume 13, Issue XII, December 2025, DOI [10.22214/ijraset.2025.76363](https://doi.org/10.22214/ijraset.2025.76363). The paper describes a password-manager application with encryption, key derivation, password generation, strength analysis, categories, search, auto-lock, and import/export. It does not specify the strength-analysis algorithm, provide training data, or publish accuracy/F1 results. Its main text describes a React/Node/PostgreSQL stack, while its conclusion names a Python/Flask and SQLite/MySQL stack. Treat this as an application-level reference; there is no paper classifier score to reproduce.

## What this repository currently implements

- **Browser vault:** `existing-approach/client` encrypts each vault entry with Web Crypto AES-256-GCM. A key is derived from the master password using PBKDF2-HMAC-SHA256 with 600,000 iterations. Encrypted entries are stored in browser `localStorage`; they are not sent to the Node/PostgreSQL service.
- **Strength feedback:** the UI compares its simple composition/length meter, zxcvbn, and a local Flask ML endpoint when a model artifact is available. The current artifact can be older than the latest Kaggle run. ML sends the password in plaintext to the local service over loopback.
- **HIBP:** the browser hashes the password locally with SHA-1 and sends the first five hex characters to the Pwned Passwords range endpoint; it compares returned suffixes in the browser. This reduces the information sent to HIBP, but does not mean the entire app is zero-knowledge or that HIBP has no metadata about the request.
- **Node/PostgreSQL service:** this is a separate scaffold. The current browser vault does not use it for authentication or persistence. Do not claim that the running app stores ciphertext in PostgreSQL.
- **Argon2id:** the repository has a standalone CPU timing script. In the recorded local run, PBKDF2-HMAC-SHA256 at 600,000 iterations had a 368.45 ms median and Argon2id at 65,536 KiB/t=3/p=1 had a 190.27 ms median. These parameter sets are not equivalent-work comparisons, and timing does not establish GPU cracking resistance. The vault still uses PBKDF2.

## Latest supplied Kaggle result

The ZIP supplied by the project owner reported the following held-out metrics. They are from source-derived labels and this notebook's split, not paper results or a real-world crackability measurement.

| Method | Accuracy (%) | Macro F1 (%) |
|---|---:|---:|
| Existing app rule meter | 69.45 | 62.63 |
| zxcvbn | 84.29 | 84.19 |
| Random Forest | 95.84 | 95.82 |
| XGBoost | 86.65 | 86.07 |

That ZIP did not contain the Random Forest model artifact, even though Random Forest scored highest. Its XGBoost pickle also failed to load in the local environment. Therefore these numbers can be reported as the ZIP's evaluation output, but neither model from that ZIP is ready to install. The updated Kaggle notebook packages Random Forest and portable XGBoost JSON. Run it again before replacing the app model.

## Dataset and evaluation limits

The notebook uses the four Kaggle inputs documented in `README.md`. Common-password lists supply weak examples by source membership. The strength-classifier CSV supplies its own labels. These labels are convenient for a reproducible class project but are not independently verified ground truth. Held-out scores measure agreement with those labels on the chosen split; they do not predict a universal time-to-crack or prove every “strong” password is safe.

The feature extractor has 17 features. A dictionary hit is based on exact match or a limited trailing-digit normalization; it is not general leetspeak or breach-corpus matching. Report the split, source labels, counts, and metrics together.

## How to verify the running prototype

1. Start the ML API from `proposed-improvement/ml-model` with `python serve_model.py`.
2. Check `http://127.0.0.1:5000/health`. `model_loaded` must be `true` for ML predictions; note the selected model and dictionary count.
3. Start the React app from `existing-approach/client` with `npm run dev` and open `http://localhost:5173`.
4. Create a demo vault and add a **fake test credential**, never a real password. Check the rule meter, zxcvbn, ML status, and HIBP result separately.
5. Treat the Node/PostgreSQL scaffold as a separate component unless you explicitly integrate it into the client and verify that end-to-end flow.

## Security limitations to disclose

- This is a class prototype, not a production password manager or audited zero-knowledge service.
- The local ML endpoint receives the entered password in plaintext. Keep it bound to loopback and do not expose it on a network.
- Browser `localStorage` is accessible to scripts running in the same origin; XSS can undermine the vault while it is unlocked.
- Browser-only storage has no automatic backup or synchronization. Clearing browser storage can destroy the vault.
- HIBP reports matches in its corpus, not every compromise; an unavailable check is not evidence of safety.
- The Kaggle labels, data sources, and train/test construction limit what the reported model metrics establish.
- Argon2id is not the vault KDF. Do not quote benchmark timings or GPU-resistance claims without a reproducible run and platform details.

## Correct claims for a project presentation

- The base paper describes an application, not a measured password classifier. This project adds and evaluates its own comparison.
- The supplied Kaggle result has Random Forest as the highest-scoring candidate, but its corresponding artifact was missing from the supplied ZIP. The updated notebook must be run to produce a usable bundle.
- The app combines browser encryption, strength feedback, and a browser-side HIBP range lookup. The Node backend is currently separate, and local ML inference receives plaintext over loopback.
- Argon2id is a benchmark-only comparison; PBKDF2 remains in the vault implementation.
