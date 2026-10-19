# Datasets

## How to Download

### 1. Password Strength Classifier Dataset (Required)
- Go to: https://www.kaggle.com/datasets/bhavikbb/password-strength-classifier-dataset
- Download `data.csv`
- Place it in this folder as `password_strength.csv`

### 2. RockYou Wordlist (Required for dictionary features)
- Search Kaggle for "rockyou.txt" and download, OR
- On Kali Linux: `cp /usr/share/wordlists/rockyou.txt.gz ./ && gunzip rockyou.txt.gz`
- Place it in this folder as `rockyou.txt`

### 3. SecLists Common Passwords (Recommended)
```bash
git clone --depth 1 https://github.com/danielmiessler/SecLists.git
# Use files from SecLists/Passwords/Common-Credentials/
```

### 4. HIBP Pwned Passwords (No download needed)
- Used via live API: `https://api.pwnedpasswords.com/range/{first5SHA1}`
- No dataset download required

## Important Notes
- **Never commit these datasets to git** — add this folder to `.gitignore`
- These datasets contain leaked/common passwords for research purposes only
- Do not use any of these passwords for actual accounts

