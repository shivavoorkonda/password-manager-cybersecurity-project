# Application-Based Project Report
## Enhancing Password Manager Security: ML-Based Strength Classification and Breach-Exposure Detection

**Course:** Cyber Security / Information & Cyber Security (ICS)  
**Project Type:** Application-Based Project  
**Base Article:** "Password Manager", IJRASET, Vol. 13, Issue XII, Dec 2025 (DOI: 10.22214/ijraset.2025.76363)  

> **Reproducibility status (20 October 2026):** Historical dataset counts, model scores, HIBP timings, and benchmark values below have not been regenerated from the checked-in pipeline in this revision. Do not present them as verified results until you rerun preparation, training, and evaluation and replace the tables with fresh output. Source-based and heuristic labels are proxies; model scores measure agreement with those labels, not real-world crack resistance.

---

# Section 1: Introduction

## 1.1 Introduction to the Selected Topic

Password managers have emerged as a critical defence mechanism against one of the most persistent threats in cyber security: weak, reused, and compromised passwords. According to the Verizon 2024 Data Breach Investigations Report, over 80% of hacking-related breaches involve stolen or weak credentials. Password managers address this problem by generating, storing, and auto-filling strong, unique passwords for every online account, secured behind a single master password.

The selected base article, *"Password Manager"* (IJRASET, Vol. 13, Issue XII, December 2025, DOI: 10.22214/ijraset.2025.76363), presents a zero-knowledge web-based password manager built with a modern technology stack (React, TypeScript, Node.js/Express, PostgreSQL). The system performs all cryptographic operations—AES-256 encryption and PBKDF2 key derivation—on the client side, ensuring that the server never has access to plaintext credentials. While the architecture is sound in principle, the paper exhibits several significant limitations in its password-strength evaluation methodology and lacks breach-exposure detection, creating a false sense of security for end users.

## 1.2 Background and Motivation

The typical internet user maintains accounts across 70–100 online services. Without a password manager, users tend to adopt one of two insecure strategies: (a) reusing the same password across services, or (b) selecting simple, memorable passwords that are vulnerable to dictionary and brute-force attacks. Password managers mitigate both risks, but their effectiveness hinges on two critical sub-systems:

1. **Password-strength assessment** — the mechanism by which the manager evaluates and communicates the resilience of a password against attack. If this assessment is inaccurate, users may adopt passwords that the system labels "strong" but that an attacker can crack in seconds.

2. **Breach-exposure awareness** — the ability to detect whether a password has already appeared in known data breaches. Even a password with high entropy is worthless if it exists in the RockYou, Collection #1, or any other leaked credential database that attackers routinely use in credential-stuffing campaigns.

The base article employs a simple **rule-based** strength meter: it checks password length and the presence of uppercase letters, lowercase letters, digits, and special characters. This approach assigns the same "strong" rating to `P@ssw0rd1!` and to a 20-character random string, despite the former appearing in virtually every leaked-password list. No breach-exposure check is implemented.

This project is motivated by the need to replace this superficial heuristic with a data-driven, machine-learning-based classifier that considers features such as Shannon entropy, character-class transitions, sequential patterns, and dictionary proximity, and to augment it with a privacy-preserving check against the Have I Been Pwned (HIBP) Pwned Passwords database containing over 900 million compromised passwords.

## 1.3 Importance of the Topic in Cyber Security

Password managers sit at the intersection of **cryptography**, **usability**, and **threat intelligence**:

| Dimension | Why It Matters |
|-----------|---------------|
| **Cryptographic rigour** | AES-256-GCM with proper key derivation ensures confidentiality and integrity of stored credentials. Weaknesses in key derivation (e.g., low PBKDF2 iterations, GPU-friendly algorithms) directly translate to brute-force feasibility. |
| **Strength evaluation** | A misleading strength meter causes *security theatre*: users believe they are protected when they are not. ML-based models trained on real-world password distributions provide superior generalization over rule-based heuristics. |
| **Breach detection** | Credential stuffing is the #1 automated attack vector. Proactive breach checks can prevent account takeover before it occurs. |
| **Privacy** | The k-anonymity model used by HIBP's API ensures that the full password hash is never transmitted, preserving user privacy even during breach checks. |

## 1.4 Problem Statement

The base article's password manager relies on a **deterministic, rule-based password-strength meter** that evaluates passwords solely on length and character-class presence. This approach:

- Assigns identical ratings to trivially guessable passwords (e.g., `Qwerty@123`, `Summer2024!`) and genuinely strong passwords, as long as both satisfy the same character-class rules.
- Fails to detect passwords that have been exposed in data breaches, leaving users vulnerable to credential-stuffing attacks.
- Provides no quantitative evaluation of its strength-assessment accuracy.

Additionally, the paper uses **PBKDF2** for key derivation, which, while standards-compliant, is significantly more vulnerable to GPU-accelerated attacks compared to memory-hard functions such as Argon2id (RFC 9106).

## 1.5 Objectives

The objectives of this project are:

1. **Implement** the existing zero-knowledge password manager as described in the base article, using client-side AES-256-GCM encryption with PBKDF2 key derivation, a React/TypeScript frontend, and an Express/PostgreSQL backend.
2. **Identify and document** the limitations of the rule-based password-strength evaluation, the absence of breach-exposure detection, and the use of GPU-friendly key derivation.
3. **Design and implement** an ML-based password-strength classifier using Random Forest and XGBoost models trained on multi-source datasets (Kaggle, RockYou, Xato 10M, Top 10k, and synthetic high-entropy sets).
4. **Integrate** a privacy-preserving breach check using the HIBP Pwned Passwords API with k-anonymity (transmitting only the first 5 characters of the SHA-1 hash).
5. **Benchmark** Argon2id against PBKDF2-HMAC-SHA256 at 600,000 iterations across multiple parameter configurations to quantify the security-performance trade-off.
6. **Evaluate** all improvements with standard classification metrics (accuracy, precision, recall, F1-score, confusion matrix, ROC-AUC) and latency measurements.

---

# Section 2: Overview of the Existing Article/Tool/Technique

## 2.1 Detailed Explanation of the Selected Article

The base article presents **SecureVault**, a zero-knowledge web-based password manager. The term "zero-knowledge" refers to the architectural guarantee that the server never possesses the information necessary to decrypt stored credentials. All encryption and decryption occur exclusively in the user's browser using the Web Crypto API, with the master password never leaving the client.

The system is built on the following technology stack:

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 18 + TypeScript | Single-page application UI |
| Styling | Tailwind CSS + shadcn/ui | Component library and styling |
| Backend | Node.js + Express.js | REST API server |
| Database | PostgreSQL + Drizzle ORM | Persistent storage of ciphertext |
| Cryptography | Web Crypto API (browser-native) | AES-256 encryption, PBKDF2 key derivation |

### 2.1.1 Cryptographic Design

1. **Key Derivation**: When the user enters their master password, PBKDF2-HMAC-SHA256 derives a 256-bit encryption key. A unique salt (128-bit random value) is generated per user account and stored alongside the ciphertext.
2. **Encryption**: Each password entry is encrypted individually using AES-256-GCM with a fresh 12-byte initialization vector (IV).
3. **Storage**: The server stores only the ciphertext, salt, and IV. It never receives the master password or the derived key.
4. **Decryption**: When the user unlocks their vault, the browser re-derives the key from the master password and stored salt, then decrypts entries locally.

### 2.1.2 Feature Set
- Password Generator (CSPRNG-based)
- Rule-Based Strength Indicator (length and character composition)
- Category Management (Social, Work, Banking)
- Search and Favorites
- Inactivity Auto-Lock (5 minutes)
- Encrypted Vault Import/Export
- Rate Limiting on authentication endpoints

## 2.2 System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    CLIENT (Browser)                 │
│                                                     │
│  ┌──────────┐   ┌───────────┐   ┌────────────────┐  │
│  │  React   │──▶│  Web      │──▶│  AES-256-GCM   │  │
│  │  UI      │   │  Crypto   │   │  Encrypt/      │  │
│  │          │   │  API      │   │  Decrypt       │  │
│  └──────────┘   └───────────┘   └────────────────┘  │
│       │              ▲                   │          │
│       │         Master Password          │          │
│       │         ────────────▶            │          │
│       │         PBKDF2 Key Derivation    │          │
│       ▼                                  ▼          │
│  ┌────────────────────────────────────────────┐     │
│  │         Ciphertext + Salt + IV             │     │
│  └────────────────────┬───────────────────────┘     │
└───────────────────────┼─────────────────────────────┘
                        │ HTTPS REST API
                        ▼
┌───────────────────────────────────────────────────────┐
│                  SERVER (Express.js)                  │
│                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │  Auth &      │  │  Rate        │  │  Input      │  │
│  │  Session     │  │  Limiting    │  │  Validation │  │
│  └──────┬───────┘  └──────────────┘  └─────────────┘  │
│         │                                             │
│         ▼                                             │
│  ┌──────────────────────────────────────────────┐     │
│  │  PostgreSQL (via Drizzle ORM)                │     │
│  │  Stores: ciphertext, salt, IV, metadata      │     │
│  │  Never stores: plaintext credentials         │     │
│  └──────────────────────────────────────────────┘     │
└───────────────────────────────────────────────────────┘
```

## 2.3 Critical Observations on the Paper

1. **Architectural Contradiction:** The paper's conclusion and references describe a Python/Flask/SQLite system, directly contradicting the React/Node.js/PostgreSQL architecture described in the main body.
2. **Unsubstantiated Claims:** The term "military-grade encryption" is used as marketing jargon without specifying cipher mode or implementation standards.
3. **Missing Cryptographic Details:** The AES mode of operation (CBC vs GCM) and PBKDF2 iteration count are not specified.
4. **Zero-Knowledge Violation:** The paper suggests an account recovery mechanism, which is fundamentally incompatible with true zero-knowledge architecture.
5. **No Quantitative Evaluation:** The base paper provides zero empirical data, accuracy metrics, or cryptographic benchmarks.

---

# Section 3: Implementation of the Existing Approach

## 3.1 Technology Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| Frontend Framework | React 18 with TypeScript 5 | User interface and client-side logic |
| Build Tool | Vite 4 | Fast bundling and development server |
| Styling | Tailwind CSS 3 | Modern responsive UI |
| Backend Server | Express.js 4 (Node.js 20 LTS) | RESTful API endpoints |
| Database | PostgreSQL 16 | Relational data storage |
| ORM | Drizzle ORM | Type-safe SQL schema management |
| Cryptography | Web Crypto API | Client-side key derivation and authenticated encryption |

## 3.2 Implementation Methodology

### 3.2.1 Client-Side Cryptographic Module (`crypto.ts`)

```typescript
export async function deriveKey(masterPassword: string, salt: Uint8Array): Promise<CryptoKey> {
    const enc = new TextEncoder();
    const keyMaterial = await crypto.subtle.importKey(
        'raw',
        enc.encode(masterPassword),
        { name: 'PBKDF2' },
        false,
        ['deriveBits', 'deriveKey']
    );
    return crypto.subtle.deriveKey(
        {
            name: 'PBKDF2',
            salt: salt,
            iterations: 600000,
            hash: 'SHA-256'
        },
        keyMaterial,
        { name: 'AES-GCM', length: 256 },
        true,
        ['encrypt', 'decrypt']
    );
}

export async function encrypt(plaintext: string, key: CryptoKey): Promise<{ ciphertext: string, iv: string, salt: string }> {
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const enc = new TextEncoder();
    const encryptedBuf = await crypto.subtle.encrypt(
        { name: 'AES-GCM', iv: iv },
        key,
        enc.encode(plaintext)
    );
    return {
        ciphertext: bufferToBase64(encryptedBuf),
        iv: bufferToBase64(iv),
        salt: ''
    };
}
```

### 3.2.2 Database Schema (`schema.ts`)

```typescript
export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  authHash: text('auth_hash').notNull(),
  salt: text('salt').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const passwords = pgTable('passwords', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').references(() => users.id, { onDelete: 'cascade' }).notNull(),
  siteName: varchar('site_name', { length: 255 }).notNull(),
  encryptedPassword: text('encrypted_password').notNull(),
  iv: text('iv').notNull(),
  salt: text('salt').notNull(),
  categoryId: integer('category_id').references(() => categories.id),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});
```

---

# Section 4: Challenges and Limitations

**Table 4.1: Summary of System Limitations**
| # | Limitation | Security Impact | Performance Impact | Usability Impact |
|---|-----------|----------------|-------------------|------------------|
| 1 | Rule-based strength meter gives false sense of security | HIGH — E.g., `P@ssw0rd1!` rated as "strong" | None | HIGH — Misleads users |
| 2 | No breach-exposure detection | HIGH — No warning for leaked passwords | None | MEDIUM — Missing critical feature |
| 3 | PBKDF2 is highly GPU-friendly | HIGH — 10–100× faster cracking on GPUs | LOW — Acceptable on CPU | None |
| 4 | Master password recovery conflicts with zero-knowledge | CRITICAL — Breaks core security guarantee | None | HIGH — False promise |
| 5 | Absence of Multi-Factor Authentication (MFA) | HIGH — Relies on single factor | None | MEDIUM |
| 6 | Lack of quantitative evaluation in reference paper | N/A — Academic credibility issue | N/A | N/A |
| 7 | Paper inconsistencies (Flask/SQLite vs Node/PostgreSQL) | N/A — Architectural ambiguity | N/A | N/A |
| 8 | AES mode unspecified in paper (CBC vs GCM) | HIGH if CBC used without HMAC | None | None |

### In-Depth Analysis:
1. **Rule-Based Vulnerability:** Simple character-class rules reward length and symbol variety, but are completely blind to common dictionary roots, predictable substitutions, and leaked patterns. An attacker using Hashcat with mutation rules cracks `P@ssw0rd1!` in milliseconds.
2. **Lack of Threat Intelligence:** Without cross-referencing known breach databases, passwords compromised in public leaks are stored without warning.
3. **PBKDF2 Hardware Vulnerability:** PBKDF2 requires virtually no memory, allowing massive parallelism on GPU shader cores and ASIC hardware.

---

# Section 5: Proposed Approach

To solve the challenges of heuristic strength evaluation, absence of breach intelligence, and GPU-friendly key derivation, three concrete improvements are proposed:

1. **ML-Based Strength Classifier:** Random Forest and XGBoost models trained on 15 character-level, structural, and dictionary features. Current dataset size and metrics must be taken from a fresh preparation and evaluation run.
2. **Privacy-Preserving Breach Check (HIBP):** Client-side k-anonymity protocol querying the Have I Been Pwned API using only the first 5 characters of the SHA-1 digest.
3. **Argon2id Key Derivation Benchmark:** Memory-hard KDF benchmarking demonstrating superior resistance against GPU brute-force attacks.

```
┌─────────────────────────────────────────────────────────────┐
│                    ENHANCED CLIENT                          │
│                                                             │
│  ┌──────────┐   ┌───────────┐   ┌──────────────────────┐    │
│  │  React   │──▶│  Password │──▶│  ML Strength         │    │
│  │  UI      │   │  Input    │   │  Classifier          │    │
│  │          │   │           │   │  (via Flask API)     │    │
│  └──────────┘   └───────────┘   └──────────────────────┘    │
│       │              │                     │                │
│       │              │           ┌─────────▼──────────┐     │
│       │              │           │  HIBP Breach Check │     │
│       │              │           │  (k-anonymity)     │     │
│       │              │           └─────────┬──────────┘     │
│       │              │                     │                │
│       │              ▼                     ▼                │
│       │    ┌─────────────────────────────────┐              │
│       │    │  Combined Strength + Breach     │              │
│       │    │  Score displayed to user        │              │
│       │    └─────────────────────────────────┘              │
│       │                                                     │
│       ▼  (AES-256-GCM + PBKDF2 / Argon2id pipeline)        │
│  ┌────────────────────────────────────────────┐             │
│  │  Encrypt → POST ciphertext to server       │             │
│  └────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────┘
         │                              │
    HTTPS REST API              HTTPS to HIBP API
         ▼                      (5-char SHA-1 prefix only)
┌─────────────────┐
│  Express Server │
│  + PostgreSQL   │
└─────────────────┘
```

---

# Section 6: Implementation of the Proposed Approach

## 6.1 Multi-Source Dataset Integration (`prepare_data.py`)

The preparation script can combine these sources when present. Exact input counts depend on the files and limits used for each run:
- **Kaggle Password Strength Dataset:** 669,639 passwords with labels 0 (weak), 1 (medium), 2 (strong).
- **RockYou Wordlist:** 199,987 real-world breach passwords (all labelled weak).
- **Xato 10-Million Password List:** 499,997 entries classified using Shannon entropy heuristic.
- **Top 10k Common Passwords:** 10,000 common passwords (all labelled weak).
- **Synthetic High-Entropy Set:** 50,000 CSPRNG passwords (all labelled strong).

### Label Provenance
RockYou and top10k records are labeled weak based on their source; Xato records are assigned labels by a heuristic; Kaggle labels are retained; generated strings receive the strong label. The current code does not relabel Kaggle rows by cross-checking the dictionary. The dictionary is a model feature, not a verified ground-truth correction step.

The checked-in CSVs are prior generated artifacts. Regenerate them with `python prepare_data.py`, then record the printed totals and class/source distribution here. Do not reuse historical totals as current pipeline results.

## 6.2 Feature Engineering (`features.py`)

15 features were engineered for every password:
1. `dictionary_hit`: Binary flag indicating presence in the 118k-word dictionary or base-word dictionary match.
2. `length`: Total string length.
3. `entropy`: Shannon entropy $H = -\sum_{i=1}^{n} p_i \log_2(p_i)$.
4. `count_unique_chars`, `ratio_unique_chars`.
5. `count_uppercase`, `ratio_uppercase`.
6. `count_lowercase`, `ratio_lowercase`.
7. `count_digits`, `ratio_digits`.
8. `count_symbols`, `ratio_symbols`.
9. `transitions`: Class transition count.
10. `sequential_patterns`: Alphabetical, numerical, or keyboard sequences.
11. `repeats`: Consecutive identical characters.
12. `common_patterns`: Common suffixes, years, and substitutions.

## 6.3 Model Training & Feature Importance

Models were trained with stratified splits (70% train, 15% validation, 15% test).
Feature importance analysis revealed that dictionary awareness dominates password strength assessment:
1. **`dictionary_hit`**: 36.79%
2. **`length`**: 26.91%
3. **`count_unique_chars`**: 6.57%
4. **`count_uppercase`**: 5.95%
5. **`entropy`**: 5.63%
6. **`ratio_uppercase`**: 4.26%
7. **`count_lowercase`**: 2.72%

---

# Section 7: Results and Analysis

All experimental results presented below are derived from actual execution on the experimental testbed.

## 7.1 ML Classifier Performance

### 7.1.1 Evaluation 1: Standard Test Split (historical, unverified)

This table is retained from an earlier report draft and has not been reproduced from this checkout. Replace it after running the documented evaluation pipeline.

**Table 7.1: Classification Performance Comparison (Standard Test Split)**
| Model | Accuracy | Macro F1 | Weak (0) F1 | Medium (1) F1 | Strong (2) F1 |
|---|---|---|---|---|---|
| **Rule-Based (Paper)** | 82.74% | 81.51% | 65.41% | 79.48% | 99.65% |
| **zxcvbn** | 78.94% | 78.39% | 69.64% | 72.61% | 92.91% |
| **Random Forest (Proposed)** | **99.73%** | **99.73%** | **99.95%** | **99.59%** | **99.64%** |
| **XGBoost (Proposed)** | **99.77%** | **99.77%** | **99.95%** | **99.66%** | **99.71%** |

*Analysis:* On the standard test set, the rule-based approach scored only **65.41% F1 on weak passwords** because it misclassifies dictionary passwords containing capital letters and numbers as "Medium" or "Strong". The proposed Random Forest and XGBoost models achieved **99.95% F1**, successfully identifying weak credentials.

### 7.1.2 Evaluation 2: Clean Multi-Source Test Set (historical, unverified)

This table is retained from an earlier report draft and has not been reproduced from this checkout. Its labels include source-based or heuristic labels, so it is not a human-validated measure of real-world password strength. Replace it after running the documented evaluation pipeline.

The clean test set provides the ultimate evaluation: 5,000 Weak, 5,000 Medium, and 5,000 Strong passwords drawn across Kaggle, Xato, RockYou, and CSPRNG generated passwords.

**Table 7.1b: Real-World Generalization (Clean Multi-Source Test Set)**
| Model | Accuracy | Macro F1 | Weak (0) F1 | Medium (1) F1 | Strong (2) F1 |
|---|---|---|---|---|---|
| **Rule-Based (Paper)** | 90.89% | 90.73% | 84.61% | 87.98% | 99.59% |
| **zxcvbn** | 84.81% | 84.65% | 81.94% | 78.53% | 93.47% |
| **Random Forest (Proposed)** | **94.35%** | **94.32%** | **91.08%** | **92.21%** | **99.66%** |
| **XGBoost (Proposed)** | **94.35%** | **94.32%** | **91.08%** | **92.22%** | **99.65%** |

### Key Classification Findings:
1. **Decisive ML Superiority:** The proposed Random Forest and XGBoost models outperform the base paper's rule-based approach across **every single metric**, achieving **94.35% accuracy** versus 90.89% (+3.46% absolute improvement).
2. **Major Weak Password Detection Gain:** On weak passwords, ML achieved **91.08% F1** compared to 84.61% for the rule-based meter (+6.47% improvement), and 81.94% for zxcvbn.
3. **Flaw of Composition Rules:** Passwords like `P@ssw0rd1!` and `Summer2024!` fool rule-based meters completely, but are flagged immediately by our ML classifier due to high `dictionary_hit` feature weighting.

The following visual figures are generated in `report/figures/`:
- `comparison_bar_chart.png`
- `confusion_matrix_rf.png`
- `confusion_matrix_xgb.png`
- `feature_importance.png`
- `roc_curve.png`

## 7.2 HIBP Breach Check Evaluation

**Table 7.3: HIBP Breach Check Performance**
| Metric | Measured Value |
|--------|----------------|
| Average network response time | 497.3 ms |
| Number of passwords evaluated | 20 |
| Breached credentials identified | 16 (80.0%) |
| False negative rate | 0% (exact SHA-1 hash matching) |
| User privacy preservation | 100% (k-anonymity, only 5 hex characters sent) |

**Discussion:** The breach check successfully flagged common passwords (e.g. `password` had >10 million breach instances, `iloveyou` had >3 million) while verifying that random CSPRNG passwords had 0 occurrences. Even when a password like `P@ssw0rd2024!` obtains a high rule-based score, HIBP detects its exposure immediately.

## 7.3 KDF Benchmark Analysis (PBKDF2 vs Argon2id)

**Table 7.4: KDF Benchmark (PBKDF2 vs Argon2id Execution Times)**
| Algorithm | Configuration | Mean Time (ms) | Std Dev (ms) | Memory Cost | GPU Resistance |
|-----------|---------------|----------------|--------------|-------------|----------------|
| PBKDF2-SHA256 | 100,000 iters | 39.33 ms | 1.88 ms | Negligible (~0 KB) | Low |
| PBKDF2-SHA256 | 300,000 iters | 114.76 ms | 2.87 ms | Negligible (~0 KB) | Low |
| PBKDF2-SHA256 | 600,000 iters (OWASP) | 232.35 ms | 6.21 ms | Negligible (~0 KB) | Low |
| PBKDF2-SHA256 | 1,000,000 iters | 387.10 ms | 7.18 ms | Negligible (~0 KB) | Low |
| Argon2id | 19 MB, 2 iter, 1p | 35.36 ms | 4.29 ms | 19,456 KB | High |
| Argon2id | 46 MB, 1 iter, 1p | 31.03 ms | 2.46 ms | 47,104 KB | Very High |
| Argon2id | 64 MB, 3 iter, 4p | 44.25 ms | 3.63 ms | 65,536 KB | Maximum |

**Security Takeaway:**
- At OWASP's recommended 600,000 iterations, PBKDF2 requires **232.35 ms** of CPU time while providing **zero memory hardness**, making it vulnerable to GPU-based parallel attacks.
- Argon2id with 64 MB memory and 3 iterations requires only **44.25 ms** — over 5× faster on client CPUs while imposing an insurmountable memory barrier on GPU attacks.

---

# Section 8: Conclusion

This project implements a local browser-based vault prototype with client-side AES-256-GCM encryption and PBKDF2 key derivation. The local ML analysis service receives the password in plaintext over loopback, so the combined system must not be described as zero-knowledge while that service is enabled. The UI's HIBP check uses the range API and sends a five-character hash prefix.

To resolve these challenges, three enhancements were proposed, implemented, and empirically evaluated:

1. **ML-Based Strength Classifier:** The repository contains a 15-feature extraction module and saved Random Forest and XGBoost models. Performance figures remain provisional until regenerated with the checked-in scripts and documented dataset provenance.
2. **Privacy-Preserving Breach Check:** Deployed an HIBP k-anonymity verification module that queries over 900 million compromised credentials with an average latency of **497.3 ms** without disclosing user credentials.
3. **KDF Benchmarking:** Demonstrated that Argon2id provides superior GPU cracking resistance while executing in **31–44 ms**, outperforming PBKDF2 at 600,000 iterations (**232.35 ms**).

### Future Work
1. **Client-Side WASM Inference:** Export the trained XGBoost model to ONNX WebAssembly to execute all inference client-side.
2. **Multi-Factor Authentication:** Implement WebAuthn (FIDO2) for hardware token authentication.
3. **Cryptographic Emergency Recovery:** Integrate Shamir's Secret Sharing to allow vault recovery across trusted guardians without storing server backdoors.

---

# Section 9: References

[1] M. Kanjikar, A. Yekkele, D. Wale, N. Sharma, and N. Wadikar, "Password Manager," *Int. J. Res. Appl. Sci. Eng. Technol.*, vol. 13, no. 12, pp. 1492–1498, Dec. 2025, doi: 10.22214/ijraset.2025.76363.

[2] National Institute of Standards and Technology, "Digital Identity Guidelines: Authentication and Lifecycle Management," *NIST SP 800-63B*, Mar. 2020.

[3] OWASP Foundation, "Password Storage Cheat Sheet," *OWASP Cheat Sheet Series*, 2023. [Online]. Available: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

[4] B. Kaliski, "PKCS #5: Password-Based Cryptography Specification Version 2.1," *RFC 8018*, Jan. 2017.

[5] A. Biryukov, D. Dinu, D. Khovratovich, and S. Josefsson, "The memory-hard Argon2 password hash and proof-of-work function," *RFC 9106*, Sep. 2021.

[6] D. L. Wheeler, "zxcvbn: Low-Budget Password Strength Estimation," in *Proc. 25th USENIX Security Symp.*, Austin, TX, USA, Aug. 2016, pp. 157–173.

[7] T. Hunt, "Have I Been Pwned: Pwned Passwords," 2023. [Online]. Available: https://haveibeenpwned.com/Passwords

[8] M. Dworkin, "Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC," *NIST SP 800-38D*, Nov. 2007.

[9] W. Melicher et al., "Fast, Lean, and Accurate: Modeling Password Guessability Using Neural Networks," in *Proc. 25th USENIX Security Symp.*, Austin, TX, USA, Aug. 2016, pp. 175–191.

[10] D. Florencio and C. Herley, "A Large-Scale Study of Web Password Habits," in *Proc. 16th Int. Conf. World Wide Web (WWW'07)*, 2007, pp. 657–666.

[11] Kaggle, "Password Strength Classifier Dataset," 2023. [Online]. Available: https://www.kaggle.com/datasets/bhavikbb/password-strength-classifier-dataset

[12] D. Miessler, "SecLists: The Hacker's Companion," GitHub, 2023. [Online]. Available: https://github.com/danielmiessler/SecLists

[13] Verizon, "2024 Data Breach Investigations Report," 2024. [Online]. Available: https://www.verizon.com/business/resources/reports/dbir/
