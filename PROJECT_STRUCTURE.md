# Password Manager Security Enhancement — Project Structure

```
password-manager-project/
├── existing-approach/
│   ├── client/                    # React + TypeScript + Vite frontend
│   │   ├── src/
│   │   │   ├── components/        # UI components (PasswordForm, StrengthMeter, etc.)
│   │   │   ├── lib/               # Crypto utilities (AES-256-GCM, PBKDF2)
│   │   │   ├── App.tsx
│   │   │   └── main.tsx
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── vite.config.ts
│   │
│   └── server/                    # Express.js + TypeScript backend
│       ├── src/
│       │   ├── index.ts           # Express app entry
│       │   ├── db.ts              # Drizzle ORM + PostgreSQL connection
│       │   ├── schema.ts          # Database schema
│       │   └── routes.ts          # REST API routes
│       ├── package.json
│       ├── tsconfig.json
│       └── drizzle.config.ts
│
├── proposed-improvement/
│   ├── ml-model/                  # Python ML pipeline
│   │   ├── train_model.py         # Feature engineering + RF/XGBoost training
│   │   ├── evaluate_model.py      # Metrics, confusion matrix, ROC curves
│   │   ├── features.py            # Feature extraction functions
│   │   ├── serve_model.py         # Flask API to serve predictions
│   │   ├── export_onnx.py         # Export model to ONNX for browser use (optional)
│   │   └── requirements.txt
│   │
│   ├── hibp-integration/          # HIBP Pwned Passwords check
│   │   └── hibp_check.ts          # k-anonymity SHA-1 prefix check
│   │
│   └── argon2-benchmark/          # KDF benchmarking
│       ├── benchmark_kdf.py       # Python Argon2 vs PBKDF2 benchmarks
│       └── benchmark_kdf.js       # Browser-side JS benchmarks
│
├── datasets/                      # Downloaded datasets (not committed to git)
│   ├── README.md                  # Instructions for downloading datasets
│   └── .gitkeep
│
├── report/
│   ├── figures/                   # Generated graphs and screenshots
│   └── report.md                  # Full compiled report
│
├── PROJECT_STRUCTURE.md           # This file
└── README.md                      # Setup and run instructions
```

## Datasets to Download

| Dataset | Source | Size |
|---------|--------|------|
| Password Strength Classifier Dataset | [Kaggle (bhavikbb)](https://www.kaggle.com/datasets/bhavikbb/password-strength-classifier-dataset) | ~670k rows |
| RockYou wordlist | Kaggle or Kali Linux `/usr/share/wordlists/` | ~14M passwords |
| SecLists Common Passwords | [GitHub](https://github.com/danielmiessler/SecLists) | Various |
| HIBP Pwned Passwords | [API](https://api.pwnedpasswords.com/range/{first5SHA1}) | Live API |

