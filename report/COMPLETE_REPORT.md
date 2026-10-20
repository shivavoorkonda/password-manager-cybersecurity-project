# Secure Password Manager: Application-Based Cybersecurity Project

**Project type:** Application-based cybersecurity project
**Base paper:** Mahesh Kanjikar et al., â€œPassword Manager,â€ IJRASET, Vol. 13, Issue XII, December 2025, DOI: [10.22214/ijraset.2025.76363](https://doi.org/10.22214/ijraset.2025.76363)
**Implementation:** [`shivavoorkonda/password-manager-cybersecurity-project`](https://github.com/shivavoorkonda/password-manager-cybersecurity-project)

> **Results status:** The supplied Kaggle ZIP reports held-out model metrics, documented below. Its highest-scoring Random Forest artifact was missing and its XGBoost pickle did not load in the local environment, so those metrics do not mean the best model is installed. Rerun the corrected notebook to produce the installable model bundle. No HIBP timing or KDF benchmark result is claimed here.

## 1. Introduction

### 1.1 Topic, background, and motivation

This project is a **Secure Password Manager**: a browser application for creating, organizing, and protecting account credentials in an encrypted local vault. Password managers address password reuse and the difficulty of remembering a unique password for every service. Their security depends on both protecting stored credentials and helping users recognize weak or previously exposed passwords.

The selected IJRASET paper describes a password-manager application and discusses password-strength analysis. The paper does not specify the strength algorithm or publish a classifier evaluation. This project examines the repository implementation and proposes additional strength-analysis and breach-awareness capabilities as extensions to the password-manager application.

### 1.2 Problem statement and objectives

**Problem:** A password manager can encrypt saved credentials but still give limited guidance about a weak or breached password. A strength label is useful only when its method and evaluation are clearly described.

Objectives:

1. Review the base paper and distinguish its stated design from claims that it does not make.
2. Describe the actual Secure Password Manager repository and its security boundaries.
3. Evaluate the appâ€™s existing rule-based and zxcvbn strength baselines against proposed Random Forest and XGBoost classifiers.
4. Add breach exposure checking using the Have I Been Pwned (HIBP) range API, which uses a five-character SHA-1 prefix.
5. Report reproducible results with dataset provenance, split design, metrics, and limitations.

## 2. Base paper and existing approach

**Publication date and scope:** IJRASET lists this paper in Volume 13, Issue XII (December 2025), with a publication date of 13 December 2025 and pages 1492–1498. The nine-page paper covers the password-security problem, objectives and scope, related work, methodology, conclusion, and future work. It describes a Secure Password Manager with AES-256, PBKDF2, a master password, client-side encryption, password generation and strength analysis, category organization, search, auto-lock, and import/export. Its methodology describes requirements and system design, frontend/backend work, encryption, database integration, categories of testing, deployment options, and refinements based on initial feedback.

The paper says strength analysis is a feature, but does **not** name its algorithm or say it is rule-based. It does not mention zxcvbn or a trained classifier, give training datasets, specify an AES mode or PBKDF2 iteration count, or provide numerical password-strength metrics. It lists testing types but does not publish quantitative classifier results. Its future-work section does suggest machine learning for suspicious login patterns, weak passwords, or repeated brute-force attempts. That is a basis for proposing an ML extension, not a classifier method or score to reproduce.

The main text describes React/TypeScript, Node.js/Express, PostgreSQL, and Drizzle ORM. The conclusion instead describes Python with Flask/FastAPI and SQLite/MySQL. This is an inconsistency in the paper, so this report records both claims rather than treating one stack as definitive.

The base paper, â€œPassword Manager,â€ describes a password-manager application, including password management, encryption, key derivation, and password-strength analysis. Its main text describes a React/TypeScript, Node.js, and PostgreSQL architecture and refers to AES-256 and PBKDF2. It does **not** identify a rule-based strength algorithm, mention zxcvbn or an ML classifier, provide training datasets, or report password-strength accuracy or macro-F1 scores. Its conclusion describes a different Python/Flask and SQLite/MySQL stack, which conflicts with the stack in the main text. The paper also discusses machine learning as a possible future direction for detecting suspicious activity and weak passwords.

Consequently, this project does not claim to reproduce a paper classifier or improve on paper-reported classifier scores. The comparison is between the paperâ€™s described application-level features and the actual repository, and between strength estimators implemented in this project.

## 3. Paper-to-project comparison

| Area | Base paper states | This repository implements / project adds |
|---|---|---|
| Project purpose | Password-manager application | **Secure Password Manager** browser application |
| Password strength | Strength analysis is mentioned; algorithm and measured performance are not specified | Existing rule-based and zxcvbn meters; proposed RF/XGBoost classifier trained and evaluated by the Kaggle notebook |
| ML training | No classifier, dataset, or accuracy result is reported; ML appears as future work | Four user-selected Kaggle sources, feature extraction, held-out evaluation, and comparison among the app rule meter, zxcvbn, RF, and XGBoost |
| Breach awareness | No HIBP integration is described | HIBP range check; browser sends only the first five characters of the SHA-1 hash to the range endpoint |
| Encryption and key derivation | Paper refers to AES-256 and PBKDF2; implementation parameters are not fully specified | Browser Web Crypto API uses AES-256-GCM and PBKDF2-HMAC-SHA256 with 600,000 iterations |
| Vault storage / architecture | Main text describes Node.js and PostgreSQL; conclusion gives a conflicting Python/Flask and SQLite/MySQL stack | Current frontend stores encrypted vault data in browser `localStorage`; backend scaffolding exists but the frontend vault flow is not connected to it |
| Argon2id | Not identified as a deployed feature in the paper | A separate script benchmarks PBKDF2 and Argon2id; this is **not** a migration of the app vault to Argon2id |
| Quantitative results | No password-classifier accuracy or macro-F1 is reported | Supplied Kaggle run: app rules 69.45/62.63, zxcvbn 84.29/84.19, RF 95.84/95.82, XGBoost 86.65/86.07 (accuracy/macro-F1, percent) |

This comparison is the projectâ€™s baseline analysis. It avoids assigning an invented â€œpaper accuracyâ€ to the base article. The paperâ€™s strength-analysis description is too high-level for a direct algorithm-for-algorithm reproduction.

## 4. Current implementation and experiment design

### 4.1 Secure Password Manager

The React/TypeScript frontend encrypts vault data in the browser using Web Crypto API AES-GCM and derives a key with PBKDF2-HMAC-SHA256 (600,000 iterations). The current vault data is persisted in `localStorage`. Although backend code and database scaffolding are present, the frontendâ€™s vault persistence path currently uses local storage; the report therefore does not describe the running application as a deployed Node/PostgreSQL vault.

The strength UI includes the existing rule meter and zxcvbn. The ML service is a separate local Flask service. When ML analysis is enabled, the password is sent in plaintext to that service over loopback for inference. The HIBP check is separate: it sends a truncated password hash prefix to the HIBP range API. Because local ML inference receives the password, do not describe the combined configuration as strictly zero-knowledge.

### 4.2 Proposed improvement

The proposed improvement is an additional data-driven strength estimate for the Secure Password Manager, plus breach exposure feedback. The notebook trains Random Forest and XGBoost on engineered password features and compares their outputs with the appâ€™s rule meter and zxcvbn. This does not replace vault encryption, and classifier output is advisory; it is not proof that a password is safe against every attack.

### 4.3 Data sources and validation

The Kaggle notebook is designed to use the four datasets supplied by the student:

1. `bhavikbb/password-strength-classifier-dataset` â€” labeled password-strength examples.
2. `wjburns/common-password-list-rockyoutxt` â€” common-password list.
3. `shivamb/10000-most-common-passwords` â€” common-password list.
4. `joebeachcapital/top-10-million-passwords` â€” Top 10 Million / SecLists-based password list.

The common-password lists provide source-derived weak examples; they are not a complete measure of guessability. The classifier datasetâ€™s labels are inherited from that dataset and may not be independent ground truth. The corrected notebook holds out a portion of unique weak-list examples before training and dictionary construction, and keeps known weak-list entries from receiving conflicting classifier labels. Scores therefore measure agreement with this experimentâ€™s labels and split, not real-world crack time or universal password safety.

## 5. Results and analysis

### 5.1 Classifier comparison from supplied Kaggle run

| Model | Accuracy | Macro F1 | Weak F1 | Medium F1 | Strong F1 |
|---|---:|---:|---:|---:|---:|
| App rule-based meter | 69.45% | 62.63% | Not in supplied summary | Not in supplied summary | Not in supplied summary |
| zxcvbn | 84.29% | 84.19% | Not in supplied summary | Not in supplied summary | Not in supplied summary |
| Random Forest | **95.84%** | **95.82%** | Not in supplied summary | Not in supplied summary | Not in supplied summary |
| XGBoost | 86.65% | 86.07% | Not in supplied summary | Not in supplied summary | Not in supplied summary |

The supplied ZIP includes summary metrics and source/split metadata. Per-class reports were not included, so per-class F1 is not inferred.

The supplied Kaggle ZIP's `model_comparison.csv` provides the accuracy and macro-F1 values shown above. Its metadata records 300,000 training rows and 15,000 evaluation rows, with held-out weak-list examples and held-out labeled medium/strong examples. The supplied summary does not include per-class reports, so per-class F1 values are not inferred. These are results for this experiment's source-derived labels and split; they are not paper results or real-world crackability scores.

Random Forest outperformed the app rule meter by 26.39 percentage points in accuracy and zxcvbn by 11.55 points. Its macro-F1 was 33.19 points above the rule meter and 11.64 points above zxcvbn (rounded from the supplied CSV). XGBoost did not match Random Forest in this run. This supports an improvement on this experiment's evaluation split only, not a comparison with paper-reported metrics.

**Model artifact limitation:** The supplied ZIP contains the XGBoost artifact and score table, but no `rf_model.joblib`, despite Random Forest being the top-scoring model. The RF result can be reported, but that RF model cannot be installed in the app from this ZIP. The corrected notebook now packages both model artifacts for a reproducible app update.

### 5.2 Other evaluation

The HIBP feature can be checked functionally with test inputs, but report breach counts and network latency only after a documented live run. Likewise, the Argon2 benchmark script produces machine-dependent timing measurements; add results only from a new local execution and include hardware/software details. The app still uses PBKDF2: benchmark results do not mean Argon2id is integrated.

## 6. Limitations and future work

- Dataset labels are source-derived and may encode collection or labeling biases.
- Common-password lists are incomplete and are not a substitute for attacker-specific guessability models.
- A random or stratified holdout does not necessarily test performance on passwords from a genuinely new population.
- The local ML endpoint receives plaintext passwords. A future browser-side inference design could reduce that exposure.
- The current vault persistence is browser `localStorage`; backend integration, threat modeling, recovery behavior, and deployment hardening need further work.
- HIBP range checking depends on network availability and does not reveal whether a password has appeared in every breach.
- Argon2id is benchmark-only at present; changing the vault KDF would require a versioned migration and recovery plan.

Future work should first validate the corrected experiment and improve label/split quality, then assess browser-side inference and connect a carefully reviewed backend if persistent multi-device vault storage is a project requirement.

## 7. Conclusion

This project is a Secure Password Manager with an encrypted browser vault and additional password-strength and breach-awareness components. The base paper is used as an application-level reference, not as a source of classifier scores: it does not specify a strength algorithm or report accuracy and macro-F1. In the supplied project experiment, Random Forest had the highest reported accuracy (95.84%) and macro-F1 (95.82%) among the four compared methods. This is an improvement over the project's rule and zxcvbn baselines on that held-out, source-labeled split only. The supplied ZIP omitted the RF artifact and its XGBoost pickle was incompatible locally, so rerun the corrected Kaggle notebook before presenting a live ML demonstration.

## References

1. M. Kanjikar, A. Yekkele, D. Wale, N. Sharma, and N. Wadikar, â€œPassword Manager,â€ *International Journal for Research in Applied Science & Engineering Technology*, vol. 13, no. XII, Dec. 2025, DOI: [10.22214/ijraset.2025.76363](https://doi.org/10.22214/ijraset.2025.76363).
2. D. L. Wheeler, â€œzxcvbn: Low-Budget Password Strength Estimation,â€ USENIX Security Symposium, 2016.
3. Have I Been Pwned, [Pwned Passwords API](https://haveibeenpwned.com/Passwords).
4. Kaggle dataset: [Password Strength Classifier Dataset](https://www.kaggle.com/datasets/bhavikbb/password-strength-classifier-dataset).
5. Kaggle dataset: [Common Password List (rockyou.txt)](https://www.kaggle.com/datasets/wjburns/common-password-list-rockyoutxt).
6. Kaggle dataset: [10,000 Most Common Passwords](https://www.kaggle.com/datasets/shivamb/10000-most-common-passwords).
7. Kaggle dataset: [Top 10 Million Passwords](https://www.kaggle.com/datasets/joebeachcapital/top-10-million-passwords).
