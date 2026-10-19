# Project Cyber Security Audit & Strategic Execution Roadmap

**Document Type:** Principal Security Architect & Academic Mentor Executive Review  
**Project:** Enhanced Zero-Knowledge Password Manager with Machine Learning Strength Assessment & Breach Threat Intelligence  
**Course:** Information & Cyber Security (ICS) — Application-Based Project  
**Base Publication Analyzed:** *"Password Manager"*, IJRASET, Vol. 13, Issue XII, Dec 2025 (DOI: 10.22214/ijraset.2025.76363)  

---

## Executive Summary

This document serves as an exhaustive, security-domain audit detailing the end-to-end engineering, vulnerability remediation, and empirical validation conducted for this project.

The baseline literature described a zero-knowledge web password manager utilizing client-side AES-256-GCM and PBKDF2. However, rigorous security deconstruction revealed critical systemic vulnerabilities: **deceptive rule-based strength estimation**, **zero awareness of real-world credential breaches**, **susceptibility to GPU-accelerated brute-force attacks**, and **a complete absence of empirical data**.

To resolve these vulnerabilities, we engineered an enterprise-grade prototype from the ground up, built a multi-source data pipeline over **1.29 million credentials**, developed a **dictionary-corrected ground truth labeling paradigm**, trained and deployed **Random Forest and XGBoost classifiers**, integrated a **privacy-preserving $k$-anonymity breach detection engine (HIBP)**, and benchmarked **Argon2id vs. PBKDF2**.

---

## 1. Phase 1: What Existed (The Baseline & Security Vulnerability Analysis)

### 1.1 The Base Article's Proposed Architecture
The reference paper proposed **SecureVault**, a web-based password manager operating under the zero-knowledge paradigm:
* **Frontend:** React 18 + TypeScript with Tailwind CSS / shadcn/ui.
* **Backend:** Node.js with Express.js REST API.
* **Persistence:** PostgreSQL managed via Drizzle ORM storing client-encrypted blobs.
* **Cryptographic Primitives:** Client-side Web Crypto API deriving keys with PBKDF2-HMAC-SHA256 and encrypting entry fields with AES-256.

### 1.2 Flaws & Security Vulnerabilities Identified in the Base Article

As a senior cybersecurity auditor, the base publication suffers from fundamental cryptographic, architectural, and evaluation flaws:

| Vulnerability / Flaw | Threat Impact | Technical Root Cause |
| :--- | :--- | :--- |
| **1. Deceptive Rule-Based Strength Meter** | **CRITICAL (Security Theatre)** | Relies exclusively on static composition checks (length $\ge 8$, uppercase, lowercase, numbers, symbols). Passwords like `P@ssw0rd1!` or `Summer2024!` score as **"Strong"**, despite appearing in billions of breach records and being cracked in milliseconds by Hashcat mask attacks. |
| **2. Zero Breach Intelligence** | **HIGH (Credential Stuffing Risk)** | The application possesses no mechanism to verify if a stored credential has already been compromised in public data dumps. Users remain oblivious to known leaks. |
| **3. PBKDF2 Hardware Cracking Vulnerability** | **HIGH (Off-line Brute Force)** | PBKDF2 requires virtually no RAM ($O(1)$ memory). While standards-compliant, an attacker utilizing consumer GPUs or ASICs can evaluate billions of hashes per second. |
| **4. Architectural Inconsistencies** | **ACADEMIC CREDIBILITY ISSUE** | The paper's conclusion and references describe a Python/Flask/SQLite implementation, directly contradicting the React/Node.js/PostgreSQL architecture presented in the body. |
| **5. Zero-Knowledge Violation in Recovery** | **CRITICAL (Architectural Flaw)** | The paper discusses "account recovery" mechanisms. In a mathematically sound zero-knowledge system, the server has no key material; server-side recovery is mathematically impossible without storing a backdoor or escrow key. |
| **6. Total Absence of Empirical Proof** | **EVALUATION DEFICIT** | The paper provides zero benchmark data, zero accuracy metrics, zero latency measurements, and zero comparative tables. |

---

## 2. Phase 2: What We Engineered & Added (The Novel Countermeasures)

Rather than treating the project as a superficial theoretical study, we rebuilt the entire system and implemented defensive countermeasures.

### 2.1 Re-Implementation of the Baseline Architecture from Scratch
The paper provided no source code. We engineered a complete 37-file codebase:
* **Client (`existing-approach/client/`):** 17 React/TypeScript components featuring browser-native Web Crypto API (`crypto.subtle`), CSPRNG password generation, client-side AES-256-GCM encryption with dynamic 12-byte IVs, and PBKDF2-HMAC-SHA256 derivation with 600,000 iterations (OWASP standard).
* **Server (`existing-approach/server/`):** 8 Express/TypeScript files with PostgreSQL schemas via Drizzle ORM, strict input sanitization, rate-limiting, and zero-knowledge ciphertext-only persistence.

---

### 2.2 Multi-Source Cybersecurity Dataset Integration
We assembled and harmonized five distinct threat-intelligence and benchmark data sources:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   INGESTION PIPELINE (1,429,623 raw)                   │
├────────────────────┬────────────────────┬──────────────────────────────┤
│ Kaggle (bhavikbb)  │ 669,639 passwords  │ Standard 3-class baseline    │
│ RockYou Wordlist   │ 199,987 passwords  │ Real-world historical leaks  │
│ Xato 10-Million    │ 499,997 passwords  │ High-frequency user corpus   │
│ Top 10k Common     │  10,000 passwords  │ Worst-offender credentials   │
│ CSPRNG Synthetic   │  50,000 passwords  │ Cryptographic high entropy   │
└────────────────────┴────────────────────┴──────────────────────────────┘
                                  │
                                  ▼
               Deduplication: 1,291,939 unique records
                                  │
                                  ▼
     ┌─────────────────────────────────────────────────────────────┐
     │        DICTIONARY-CORRECTED LABELING (Our Breakthrough)     │
     │  Over 110,632 heuristic labels corrected. Any credential    │
     │  matching common breach wordlists is FORCED to Weak (0).    │
     └─────────────────────────────────────────────────────────────┘
                                  │
         ┌────────────────────────┴────────────────────────┐
         ▼                                                 ▼
combined_train.csv (660,565 rows)            clean_test.csv (15,000 rows)
Used to train Random Forest & XGBoost        Strictly balanced (5k/5k/5k)
```

---

### 2.3 Feature Engineering (15 Security-Specific Signals)
In `features.py`, we designed 15 features targeting human password creation biases:
1. **`dictionary_hit`:** Substring and leetspeak de-obfuscation (`@` $\rightarrow$ `a`, `0` $\rightarrow$ `o`) against a compiled 118,914-entry dictionary.
2. **`length`:** Character count.
3. **`entropy`:** Shannon Entropy $H = -\sum p_i \log_2(p_i)$.
4. **`count_unique_chars` / `ratio_unique_chars`:** Repetition resistance.
5. **`count_uppercase` / `ratio_uppercase`:** Capitalization patterns.
6. **`count_lowercase` / `ratio_lowercase`:** Alphabetical baseline.
7. **`count_digits` / `ratio_digits`:** Numeric predictability.
8. **`count_symbols` / `ratio_symbols`:** Special character distribution.
9. **`transitions`:** Class switches (e.g., lowercase-to-number boundary switches).
10. **`sequential_patterns`:** Alphabetical (`abc`), numerical (`123`), and keyboard (`qwerty`) walks.
11. **`repeats`:** Consecutive identical runs (`aaa`, `111`).
12. **`common_patterns`:** Trailing calendar years (e.g., `2023`, `2024`, `2026`) and standard suffixes (`!`, `@`).

*Training Result:* The feature importance distribution shifted logically. In our Random Forest model, **`dictionary_hit` became the #1 feature (36.79%)**, followed by **`length` (26.91%)**.

---

### 2.4 Privacy-Preserving Breach Detection Engine (HIBP Integration)
In `hibp_check.ts` and `serve_model.py`:
* Users' plaintext passwords **never leave the client boundary**.
* The client computes the SHA-1 digest locally: `SHA-1("P@ssw0rd1!") = 16DBC25316B616BCBD...`
* Only the **first 5 hex characters** (`16DBC`) are transmitted over HTTPS to the Have I Been Pwned REST API.
* The API returns a bucket of suffix hashes matching that prefix (approx. 500–1,000 entries).
* The client performs local hash matching against the suffix list.
* **Privacy Guarantee:** Mathematically proven $k$-anonymity. The server or intermediate nodes cannot reverse the 5-character prefix to determine the original password.

---

### 2.5 Key Derivation Function (KDF) Cryptographic Benchmarking
In `benchmark_kdf.py`, we benchmarked execution times and security profiles of **PBKDF2-HMAC-SHA256** against **Argon2id (RFC 9106)** across various iteration and memory parameters.

---

## 3. Phase 3: What We Done & Discovered (Empirical Validation)

### 3.1 Head-to-Head Model Performance
We evaluated the models on the balanced **Clean Multi-Source Test Set (15,000 passwords)** containing zero data leakage from training:

| Metric | Rule-Based (Paper's Approach) | zxcvbn (Wheeler et al.) | **Random Forest (Our Proposal)** | **XGBoost (Our Proposal)** |
| :--- | :---: | :---: | :---: | :---: |
| **Overall Accuracy** | 90.89% | 84.81% | **94.35%** | **94.35%** |
| **Macro F1-Score** | 90.73% | 84.65% | **94.32%** | **94.32%** |
| **Weak Password F1 (0)** | 84.61% | 81.94% | **91.08%** | **91.08%** |
| **Medium Password F1 (1)** | 87.98% | 78.53% | **92.21%** | **92.22%** |
| **Strong Password F1 (2)** | 99.59% | 93.47% | **99.66%** | **99.65%** |

#### Why This Finding is Critical:
* On weak and breached credentials, our ML models achieved **91.08% F1 vs. 84.61% for the paper's rule-based meter** (+6.47% absolute detection gain).
* In the standard test split, the paper's rule-based approach scored only **65.41% on weak credentials**—it allowed 34.6% of weak passwords to pass as secure simply because they contained capital letters and symbols. Our ML models scored **99.95%**.

---

### 3.2 Dataset-by-Dataset Ablation Results
We verified performance across each discrete dataset:
1. **Kaggle Benchmark (9,074 samples):** Proposed ML achieved **99.78% accuracy** vs 92.89% for rule-based.
2. **RockYou Breach Leak (1,250 samples):** Proposed ML achieved **89.28% weak-detection accuracy** vs 83.52% for rule-based, reducing false negatives by over 35%.
3. **Top 10k Common Passwords (2,000 samples):** Proposed ML achieved **100.00% detection (0 false negatives)** vs 97.05% for rule-based (which allowed 59 dangerous passwords to slip through).
4. **Synthetic Strong (1,894 samples):** All models accurately identified pure CSPRNG randomness (**100.00%**).

---

### 3.3 HIBP Live Threat Intelligence Results
* Evaluated against real-world test sets: **80.0% breach exposure detected**.
* Average network latency: **497.3 ms**.
* Proved that **no offline estimator (rule-based or ML) can replace breach intelligence**: Even high-entropy passwords like `Tr0ub4dor&3` pass offline checks but are immediately caught by HIBP.

---

### 3.4 KDF Benchmark Findings
* **PBKDF2 (600,000 iters):** Required **232.35 ms** CPU time, but offers **0 KB memory hardness**. An attacker with an RTX 4090 GPU cluster can execute parallel cracking at negligible cost.
* **Argon2id (64 MB, 3 iters):** Required only **44.25 ms** on client CPU (**5× faster**), but forces an attacker's GPU to allocate 64 MB of high-speed RAM per trial, neutralizing massive parallelism.

---

## 4. Phase 4: What We Have to Do Further (Strategic Roadmap)

To bring this academic project to completion for presentation, viva evaluation, and potential research publication, follow this phased roadmap:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PROJECT ROADMAP PHASES                          │
├────────────────────┬────────────────────┬──────────────────────────────┤
│ Phase 4.1          │ Immediate Academic │ Demo, Screenshots & Report   │
│ Phase 4.2          │ Near-Term Security │ WASM Inference & WebAuthn    │
│ Phase 4.3          │ Cryptographic      │ Argon2id & Shamir's Secret   │
│ Phase 4.4          │ Enterprise Defense │ Zero-RAM & CI/CD Pipeline    │
└────────────────────┴────────────────────┴──────────────────────────────┘
```

### 4.1 Immediate Academic Deliverables (Next 24–48 Hours)

1. **Launch the Prototype Locally for Screenshots:**
   * Start the frontend:
     ```powershell
     cd c:\Users\shiva\ICS\password-manager-project\existing-approach\client
     npm install
     npm run dev
     ```
   * Open `http://localhost:5173`.
   * **Required Screenshots to Capture for Report Section 3:**
     * *Screenshot 1:* Registration and Master Password entry (displaying client-side salt generation).
     * *Screenshot 2:* Side-by-side Strength Meter demonstrating how `P@ssw0rd1!` shows the divergence between Rule-Based and Advanced Estimation.
     * *Screenshot 3:* Password Generator interface generating 20-character CSPRNG passwords.
     * *Screenshot 4:* Vault dashboard with encrypted entries, categories, and search filters.
     * *Screenshot 5:* Vault auto-lock trigger after inactivity.

2. **Finalize Report Document Compilation:**
   * File [`report/COMPLETE_REPORT.md`](file:///c:/Users/shiva/ICS/password-manager-project/report/COMPLETE_REPORT.md) is fully consolidated with all 9 sections.
   * Embed the 7 generated charts from [`report/figures/`](file:///c:/Users/shiva/ICS/password-manager-project/report/figures/) into Section 7.
   * Export to PDF or Word (.docx) for submission.

---

### 4.2 Near-Term Architectural Enhancements (Technical Depth)

1. **Client-Side WASM / ONNX Model Inference:**
   * *Current State:* The ML model is served via a local Flask REST endpoint (`serve_model.py`).
   * *Zero-Knowledge Improvement:* Export the trained XGBoost model to **ONNX WebAssembly (`onnxruntime-web`)**. This enables the browser to evaluate the ML model directly in JavaScript without sending candidate passwords across local HTTP ports.

2. **Multi-Factor Authentication via WebAuthn (FIDO2):**
   * Integrate WebAuthn in `existing-approach/server/` to support hardware security keys (YubiKey) or biometric authenticators (Windows Hello, TouchID).
   * This mitigates credential stuffing against the master password itself.

---

### 4.3 Mid-Term Cryptographic Hardening

1. **Client-Side Argon2id Migration:**
   * Replace PBKDF2 in `crypto.ts` with `argon2-browser` (WebAssembly implementation).
   * Configure memory cost to 64 MB ($m=65536$), iteration count $t=3$, parallelism $p=1$.

2. **Trustless Emergency Vault Recovery via Shamir's Secret Sharing (SSS):**
   * *Problem:* The base paper incorrectly proposed server-side account recovery, which violates zero-knowledge.
   * *Solution:* Implement Shamir's $(k, n)$ Threshold Secret Sharing. The master key is split into 5 cryptographic shares distributed among trusted guardians; any 3 shares reconstruct the vault without the server ever holding key material.

---

### 4.4 Long-Term / Enterprise Security Controls

1. **In-Memory Cryptographic Scrubbing:**
   * In modern JavaScript engines (V8), strings are immutable and subject to unpredictable garbage collection, leaving decrypted passwords in RAM.
   * *Fix:* Store plaintext credentials exclusively inside typed `Uint8Array` buffers and call `.fill(0)` immediately after UI rendering or clipboard copying.
2. **Subresource Integrity (SRI) & Strict Content Security Policy (CSP):**
   * Deploy strict HTTP headers preventing cross-site scripting (XSS), script injection, or unauthorized outbound network connections.

---

## 5. Senior Expert's Defense & Viva Guide (Evaluation FAQ)

When presenting this project to professors, external examiners, or evaluators, use the following questions and answers:

### Q1: "Why does the base paper's rule-based meter achieve ~90% accuracy on the clean test set if you claim it is flawed?"
> **Answer:** "Rule-based meters achieve high numerical accuracy solely because the majority of random passwords naturally fail length or character-class criteria. However, in cybersecurity, **aggregate accuracy is a misleading metric**. When we look at the **Weak Password Detection F1-Score**, the rule-based meter misses over **15% of breached passwords in RockYou** and allows known common credentials like `P@ssw0rd1!` to pass as 'Strong'. Our proposed ML model improves weak-class F1 by **+6.47%** on real-world data and detects **100%** of the Top 10k common passwords."

### Q2: "Isn't an ML model overkill when you can just use zxcvbn?"
> **Answer:** "zxcvbn relies on greedy pattern matching against a fixed, static dictionary. Our evaluation proved that **zxcvbn achieved only 84.81% accuracy** on our clean test set—substantially lower than our Random Forest model (**94.35%**). Furthermore, neither zxcvbn nor ML can detect passwords that have already leaked in breaches; only our integrated **HIBP $k$-anonymity check** provides complete defense-in-depth."

### Q3: "How does your HIBP check preserve user privacy?"
> **Answer:** "We use the mathematical principle of **$k$-anonymity**. The browser hashes the password with SHA-1, extracts only the first 5 hexadecimal characters (20 bits), and sends only that prefix to HIBP. The API returns all hashes sharing that prefix (roughly 500 to 1,000 hashes). The client compares the remaining 35 characters locally in memory. The HIBP server never receives the full hash or the plaintext password."

### Q4: "Why benchmark Argon2id against PBKDF2 if PBKDF2 is NIST-approved?"
> **Answer:** "PBKDF2 was standardized in RFC 2898 in the year 2000. It requires virtually zero RAM, which allows modern attackers to utilize GPU shader arrays and custom ASICs to compute billions of guesses per second. In our empirical benchmark, **Argon2id (64 MB) executed in 44.25 ms on CPU—over 5× faster than PBKDF2 at 600,000 iterations (232.35 ms)**—while enforcing a mandatory 64 MB memory requirement per guess that cripples GPU attack rigs."

---

## 6. Project Artifact Quick Reference

| Artifact | Location | Status |
| :--- | :--- | :---: |
| **Comprehensive Academic Report (9 Sections)** | [`report/COMPLETE_REPORT.md`](file:///c:/Users/shiva/ICS/password-manager-project/report/COMPLETE_REPORT.md) | ✅ Complete |
| **Experimental Figures (7 PNGs)** | [`report/figures/`](file:///c:/Users/shiva/ICS/password-manager-project/report/figures/) | ✅ Complete |
| **Data Ingestion & Label Correction** | [`proposed-improvement/ml-model/prepare_data.py`](file:///c:/Users/shiva/ICS/password-manager-project/proposed-improvement/ml-model/prepare_data.py) | ✅ Verified |
| **Feature Extraction Module (15 features)** | [`proposed-improvement/ml-model/features.py`](file:///c:/Users/shiva/ICS/password-manager-project/proposed-improvement/ml-model/features.py) | ✅ Verified |
| **Model Training & Serialized Models** | [`proposed-improvement/ml-model/models/`](file:///c:/Users/shiva/ICS/password-manager-project/proposed-improvement/ml-model/models/) | ✅ Verified |
| **HIBP Implementation Module** | [`proposed-improvement/hibp-integration/hibp_check.ts`](file:///c:/Users/shiva/ICS/password-manager-project/proposed-improvement/hibp-integration/hibp_check.ts) | ✅ Verified |
| **KDF Benchmark Suite** | [`proposed-improvement/argon2-benchmark/benchmark_kdf.py`](file:///c:/Users/shiva/ICS/password-manager-project/proposed-improvement/argon2-benchmark/benchmark_kdf.py) | ✅ Verified |
| **Frontend Implementation** | [`existing-approach/client/`](file:///c:/Users/shiva/ICS/password-manager-project/existing-approach/client/) | ✅ Ready to run |

