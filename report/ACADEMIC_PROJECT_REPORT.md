# Comprehensive Application-Based Project Report
## Enhancing Password Manager Security: ML-Based Strength Classification and Privacy-Preserving Breach-Exposure Detection

**Course:** Cyber Security / Information & Cyber Security (ICS)  
**Project Category:** Application-Based Cyber Security Project  
**Base Publication:** *"Password Manager"*, IJRASET, Vol. 13, Issue XII, December 2025 (DOI: [10.22214/ijraset.2025.76363](https://doi.org/10.22214/ijraset.2025.76363))  
**Authors of Base Paper:** Mahesh Kanjikar, Ashwini Yekkele, Divya Wale, Nandini Sharma, Nikita Wadikar (Bheemanna Khandre Institute of Technology, Bhalki)  
**Implementation Repository:** [`shivavoorkonda/password-manager-cybersecurity-project`](https://github.com/shivavoorkonda/password-manager-cybersecurity-project)  

---

## 1. Introduction

### 1.1 Introduction to the Selected Topic
In modern digital computing, authentication continues to serve as the primary security perimeter protecting confidential resources, financial systems, and personal identities. Despite ongoing developments in biometric and hardware-token authentication, the username-and-password paradigm remains the universal standard across web and enterprise services. 

To manage dozens or hundreds of accounts securely, **Password Managers** have become foundational security infrastructure. Operating as encrypted cryptographic vaults, password managers allow users to memorize a single high-entropy **Master Password** while generating, encrypting, storing, and auto-filling unique, complex credentials for all external accounts. 

### 1.2 Background and Motivation
The average digital user maintains between 70 and 100 online credentials. Human cognitive limitations create severe usability friction when attempting to recall high-entropy, distinct passwords for each service. Consequently, users default to insecure behavioral patterns:
1. **Password Reuse:** Using the identical password across multiple unrelated domains (e.g., banking, social media, shopping).
2. **Predictable Transformations:** Selecting a basic root word and appending simple modifications, years, or symbols (e.g., `Welcome@2024`, `P@ssw0rd1!`).
3. **Insecure Storage:** Writing credentials in plaintext documents, personal notes, or unencrypted local spreadsheets.

The selected base article, *"Password Manager"* (IJRASET, Dec 2025), proposed a web-based zero-knowledge password manager utilizing React, Node.js, Express, PostgreSQL, AES-256 symmetric encryption, and PBKDF2 key derivation. 

While the high-level architecture adopts zero-knowledge principles, critical security inspection reveals severe limitations:
* The base paper's security evaluation relies entirely on a **simplistic, rule-based strength meter** that counts character classes (length, uppercase, lowercase, numbers, symbols). This assigns a "Strong" rating to notoriously compromised passwords such as `P@ssw0rd1!` because they satisfy syntax rules, while being instantly crackable by attackers using dictionary and rule-based mask attacks.
* The system possesses **no threat intelligence or breach-exposure detection**. Even if a user stores a password that has appeared in public data breaches comprising hundreds of millions of leaked records, the system provides zero warnings.
* The paper utilizes **PBKDF2**, an older compute-bound Key Derivation Function that lacks memory hardness, making master passwords susceptible to GPU-accelerated mass brute-forcing.
* The base publication lacks any quantitative empirical measurements, benchmarking data, or validation datasets.

This project is motivated by the urgent necessity to bridge the gap between superficial heuristic security ("security theatre") and data-driven defensive cyber security.

### 1.3 Importance of the Topic in Cyber Security
According to the Verizon Data Breach Investigations Report (DBIR), more than **80% of web application breaches involve compromised, stolen, or weak credentials**. The primary threat vectors include:
* **Credential Stuffing:** Automated replay of billions of leaked username/password combinations across high-value portals.
* **Targeted Offline Cracking:** When an encrypted vault or password hash database is breached, attackers deploy GPU clusters running Hashcat or John the Ripper to test trillions of candidate combinations per second.
* **Security Theatre Vulnerability:** Rule-based strength meters actively deceive users into believing that their credentials are safe, lowering their vigilance against credential stuffing.

Enhancing password manager security with **Machine Learning (ML)-based strength assessment**, **privacy-preserving breach threat intelligence ($k$-anonymity)**, and **memory-hard key derivation (Argon2id)** provides measurable defense-in-depth against both automated credential-stuffing campaigns and offline GPU attacks.

### 1.4 Problem Statement and Objectives
**Problem Statement:**  
The baseline zero-knowledge password manager relies on deterministic, syntax-based rules that fail to detect predictable passwords, contains no awareness of historical data breaches, utilizes GPU-friendly key derivation, and provides no empirical verification of its defensive posture.

**Project Objectives:**
1. **Re-implement and Validate the Baseline:** Implement the full zero-knowledge web application architecture described in the base paper using client-side AES-256-GCM authenticated encryption, PBKDF2-HMAC-SHA256 key derivation, React/TypeScript frontend, and Express/PostgreSQL backend.
2. **Audit and Identify Limitations:** Systematically dissect the baseline system to identify architectural contradictions, cryptographic weaknesses, and false security metrics.
3. **Design and Implement ML Password Strength Classifier:** Extract 15 structural, entropy, and dictionary features across 1.29 million real-world passwords and train Random Forest and XGBoost classifiers with dictionary-corrected ground-truth labeling.
4. **Integrate Privacy-Preserving Breach Detection:** Deploy a client-side $k$-anonymity verification module querying the Have I Been Pwned (HIBP) database (>900 million breached records) without exposing user credentials.
5. **Benchmark Memory-Hard Key Derivation:** Conduct empirical benchmarks comparing PBKDF2-HMAC-SHA256 against Argon2id (RFC 9106) across multiple parameter sets to quantify resistance against GPU-accelerated cracking rigs.
6. **Empirical Evaluation and Comparative Analysis:** Measure classification performance (Accuracy, Precision, Recall, Macro F1, ROC-AUC) across both standard and clean multi-source test splits, and evaluate latency trade-offs.

---

## 2. Overview of the Existing Article/Tool/Technique

### 2.1 Detailed Explanation of the Selected Article
The base paper, *"Password Manager"*, presents **SecureVault**, a web-based password vault application designed around the **Zero-Knowledge Architecture** paradigm. Under zero-knowledge security, the hosting server acts purely as a blind storage provider for encrypted blobs (ciphertext), while all cryptographic operations occur strictly on the user's client device.

Key cryptographic and architectural attributes claimed in the paper:
* **Symmetric Encryption:** AES-256 (Advanced Encryption Standard with a 256-bit key) for encrypting stored passwords.
* **Key Derivation Function (KDF):** PBKDF2 (Password-Based Key Derivation Function 2) used to convert the user's master password into a 256-bit cryptographic key with a per-user salt.
* **Master Password Secrecy:** The master password is never transmitted across the network, logged, or written to disk.
* **Zero Plaintext Storage:** The server database stores solely encrypted strings, initialization vectors, and salts.

### 2.2 Working Methodology
1. **User Registration:** The client application collects the user's email and master password. A cryptographically random salt is generated. A client-side hash of the master password is sent to the server for authentication, while an encryption key is derived locally.
2. **Credential Ingestion & Encryption:** When the user enters a website credential, the client derives an encryption key from the master password and salt using PBKDF2. A random Initialization Vector (IV) is generated. The credential is encrypted with AES-256, and the resulting ciphertext, salt, and IV are transmitted over HTTPS to the backend REST API.
3. **Vault Decryption & Retrieval:** During user login, the client retrieves the encrypted blobs, uses the master password and salt to re-derive the key, and decrypts the records locally in the browser memory for display.

### 2.3 Architecture and Workflow
```
┌────────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER (Browser)                          │
│                                                                        │
│   ┌───────────────┐     ┌─────────────────────┐    ┌───────────────┐   │
│   │   React UI    │───▶│   Web Crypto API    │───▶│  AES-256-GCM  │   │
│   │  (TypeScript) │     │ (Client-Side Logic) │    │  Encrypt/Dec  │   │
│   └───────┬───────┘     └──────────┬──────────┘    └───────┬───────┘   │
│           │                        │                       │           │
│           │            Master Password + Salt              │           │
│           │            ──▶ PBKDF2 Derivation               │           │
│           ▼                                                ▼           │
│     Password Entry                              Ciphertext + IV + Salt │
│           │                                                │           │
└───────────┼────────────────────────────────────────────────┼───────────┘
            │                                                │
            │                  HTTPS REST API                │
            ▼                                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        SERVER LAYER (Node.js)                          │
│                                                                        │
│   ┌─────────────────────┐     ┌──────────────────┐                     │
│   │  Express.js Router  │────▶│ Rate Limiter &   │                     │
│   │  & JSON Validation  │     │ Session Handler  │                     │
│   └──────────┬──────────┘     └──────────────────┘                     │
│              │                                                         │
│              ▼                                                         │
│   ┌──────────────────────────────────────────────┐                     │
│   │  PostgreSQL Database (via Drizzle ORM)       │                     │
│   │  Stores: User ID, Ciphertext, IV, Salt       │                     │
│   │  (Zero plaintext passwords, Zero master key) │                     │
│   └──────────────────────────────────────────────┘                     │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.4 Advantages and Applications
* **Advantages:**
  * Mitigates server-side breach risks: If the central database is compromised, attackers only obtain encrypted ciphertext blobs.
  * Centralizes credential management without sacrificing master password privacy.
  * Built-in password generation encourages the deprecation of repeated passwords.
* **Applications:**
  * Consumer personal credential storage.
  * Small business and corporate team password management.
  * Secure storage for API keys, recovery codes, and sensitive personal notes.

---

## 3. Implementation of the Existing Approach

### 3.1 Tools, Technologies, and Experimental Setup
To rigorously evaluate the baseline, the system was implemented strictly adhering to the modern specifications outlined in the base paper:
* **Frontend Framework:** React 18.2 with TypeScript 5.0, bundled with Vite 4.4.
* **Styling Framework:** Tailwind CSS 3.3 for responsive UI rendering.
* **Client Cryptography:** Browser-native Web Crypto API (`window.crypto.subtle`), ensuring standard compliance without external insecure crypto libraries.
* **Backend Framework:** Node.js (v24 LTS runtime) with Express.js 4.18 REST API.
* **Database & ORM:** PostgreSQL 16 managed using Drizzle ORM for type-safe schema definitions and parameterized SQL queries.
* **Baseline Strength Checker:** Deterministic rule-based heuristic checking character-set composition and string length.

### 3.2 Implementation Methodology
The core client cryptographic operations were implemented in [`crypto.ts`](file:///c:/Users/vujja/OneDrive/Documents/OneDrive/Desktop/icsproject/password-manager-cybersecurity-project/existing-approach/client/src/lib/crypto.ts):

```typescript
// Client-side key derivation via Web Crypto API (OWASP standard 600,000 iterations)
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

// Client-side authenticated encryption using AES-256-GCM
export async function encrypt(plaintext: string, key: CryptoKey): Promise<{ ciphertext: string, iv: string }> {
  const iv = crypto.getRandomValues(new Uint8Array(12)); // 96-bit standard GCM nonce
  const enc = new TextEncoder();
  const encryptedBuf = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv: iv },
    key,
    enc.encode(plaintext)
  );
  return {
    ciphertext: bufferToBase64(encryptedBuf),
    iv: bufferToBase64(iv)
  };
}
```

The database persistence schema was implemented in [`schema.ts`](file:///c:/Users/vujja/OneDrive/Documents/OneDrive/Desktop/icsproject/password-manager-cybersecurity-project/existing-approach/server/src/schema.ts):

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

### 3.3 Experimental Setup and UI Results
The existing approach was validated by executing the client application locally. The user interface allows creating accounts, generating cryptographic salts, deriving AES keys, and adding encrypted vault records with real-time rule-based feedback:
* **Master Password Setup:** Salt is generated client-side using `crypto.getRandomValues(new Uint8Array(16))`.
* **Vault Dashboard:** Encrypted records are categorized (Social, Finance, Work) with zero plaintext ever reaching the server logs.
* **Auto-Lock Mechanism:** Client-side 5-minute inactivity timers trigger state clearance, purging decrypted passwords from React component state.

---

## 4. Challenges and Limitations

A comprehensive security audit of the base paper and its underlying implementation revealed eight critical vulnerabilities and design limitations.

### 4.1 Summary of Identified Limitations
| # | Limitation | Domain | Security Impact | Usability / Performance Impact |
|---|-----------|--------|----------------|--------------------------------|
| **1** | **Deceptive Rule-Based Strength Meter** | Authentication | **CRITICAL (Security Theatre)** | Gives false confidence; rates breached passwords as "Strong". |
| **2** | **Zero Breach-Exposure Intelligence** | Threat Intel | **HIGH (Credential Stuffing)** | Compromised passwords in RockYou/Collection #1 stored without warning. |
| **3** | **PBKDF2 Hardware Cracking Vulnerability** | Cryptography | **HIGH (Offline Brute Force)** | $O(1)$ memory usage allows massive parallelism on GPU/ASIC clusters. |
| **4** | **Master Password Recovery Flaw** | Architecture | **CRITICAL (Zero-Knowledge Breach)**| Base paper claims "account recovery", which violates zero-knowledge without backdoors. |
| **5** | **Absence of Multi-Factor Authentication** | Access Control | **HIGH (Single Point of Failure)** | Vulnerable if master password is compromised via phishing or shoulder surfing. |
| **6** | **Lack of Quantitative Evaluation** | Academic Rigor | **HIGH (No Empirical Proof)** | The base paper provides zero benchmark data, accuracy scores, or test datasets. |
| **7** | **Architectural Contradictions in Paper** | System Design | **HIGH (Document Inconsistency)** | Conclusion claims Python/Flask/SQLite; body describes React/Node/PostgreSQL. |
| **8** | **Unspecified Cryptographic Modes** | Cryptography | **HIGH (Implementation Risk)** | Base paper omits AES mode (CBC vs GCM) and PBKDF2 iteration parameters. |

### 4.2 In-Depth Analysis of the Core Challenges

#### Challenge 1: The Vulnerability of Rule-Based Password Strength Evaluation
The base article uses a naive heuristic checking string length ($\ge 8$, $\ge 12$), uppercase, lowercase, numbers, and symbols.
* **Failure Mode:** Consider the password `P@ssw0rd1!`. It is 10 characters long, has uppercase (`P`), lowercase (`sswrd`), a digit (`1`), and symbols (`@`, `!`). The rule-based meter gives it **100% (Strong / Very Strong)**.
* **The Cyber Threat:** In reality, `P@ssw0rd1!` exists in virtually every public breach wordlist (RockYou, Xato, SecLists) and is cracked by Hashcat using rule mutations in under 5 milliseconds. Relying on rule-based meters constitutes *security theatre* that actively harms user safety.

#### Challenge 2: Total Absence of Breach Intelligence
Even if a user creates a password that satisfies complexity rules, it may have already been published in a breach dump of hundreds of millions of credentials. Attackers do not brute force characters alphabetically; they execute **credential stuffing** using compiled breach dumps. Storing a compromised credential without checking against breach intelligence leaves the user entirely exposed.

#### Challenge 3: PBKDF2 Lack of Memory Hardness
PBKDF2 requires virtually zero memory ($O(1)$ RAM). An attacker who steals the encrypted database can utilize specialized graphics cards (e.g., Nvidia RTX 4090) where thousands of shader cores execute PBKDF2 iterations in parallel. Modern standards (NIST SP 800-63B, OWASP, RFC 9106) recommend memory-hard functions like **Argon2id**, which force each cracking thread to allocate megabytes of high-speed memory, neutralizing GPU parallelism.

---

## 5. Proposed Approach

To address the limitations identified in Section 4, this project proposes and implements three novel, cohesive enhancements:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ENHANCED ARCHITECTURE                           │
│                                                                        │
│   ┌───────────────┐     ┌─────────────────────┐    ┌───────────────┐   │
│   │   React UI    │───▶│   Candidate Password│───▶│ ML Strength   │   │
│   │  (TypeScript) │     │      Input Stream   │    │ Classifier    │   │
│   └───────┬───────┘     └──────────┬──────────┘    │ (15 Features) │   │
│           │                        │               └───────┬───────┘   │
│           │                        │                       │           │
│           │                        ▼                       ▼           │
│           │             ┌─────────────────────┐    ┌───────────────┐   │
│           │             │  Local SHA-1 Digest │    │ Weak / Med /  │   │
│           │             │  (Take 5 Hex Chars) │    │ Strong Score  │   │
│           │             └──────────┬──────────┘    └───────┬───────┘   │
│           │                        │                       │           │
│           │                        ▼ (k-anonymity)         │           │
│           │             ┌─────────────────────┐            │           │
│           │             │  HIBP API Query     │            │           │
│           │             │  (Zero Leaked Pwd)  │            │           │
│           │             └──────────┬──────────┘            │           │
│           │                        │                       │           │
│           ▼                        ▼                       ▼           │
│   ┌─────────────────────────────────────────────────────────────┐      │
│   │   Unified Cyber Security Dashboard:                         │      │
│   │   - ML Probability & Feature Importance Warnings            │      │
│   │   - Real-World Breach Exposure Alert (Exact Count)          │      │
│   └─────────────────────────────────────────────────────────────┘      │
│                                    │                                   │
│                        Argon2id / AES-256-GCM                          │
│                                    ▼                                   │
│                     Secure Client-Side Encrypted Vault                 │
└────────────────────────────────────────────────────────────────────────┘
```

### 5.1 Enhancement 1: Machine Learning-Based Password Strength Classifier
Replace naive heuristics with an ensemble ML model (Random Forest & XGBoost) trained on 15 features extracted from real passwords:
* Features incorporate Shannon entropy, character class transitions, alphanumeric walks, consecutive character runs, and base-word dictionary lookups with leetspeak normalization.
* **Dictionary-Corrected Ground Truth:** Any password found in breach wordlists is forced to label `0` (Weak), teaching the model that syntax complexity does not equal security.

### 5.2 Enhancement 2: Privacy-Preserving Breach Detection (HIBP $k$-Anonymity)
Implement a client-side verification engine that cross-references passwords against Have I Been Pwned's 900+ million breached passwords:
1. The client computes the SHA-1 hash locally: $\text{Hash} = \text{SHA-1}(\text{password})$.
2. The client splits the hash into a 5-character prefix (20 bits) and a 35-character suffix (140 bits).
3. The client queries `https://api.pwnedpasswords.com/range/{prefix}`.
4. The server returns 500–1,000 suffixes matching the prefix.
5. The client checks locally whether its suffix is in the bucket.
* **Mathematical Privacy Guarantee:** The API server and intermediate network snoops never see the full hash or the plaintext password, satisfying $k$-anonymity.

### 5.3 Enhancement 3: Memory-Hard KDF Benchmarking (Argon2id vs PBKDF2)
Conduct formal benchmarking of Argon2id (RFC 9106) against PBKDF2-HMAC-SHA256 to quantify CPU execution time versus memory allocation, proving superior defense against GPU/ASIC hardware rigs.

---

## 6. Implementation of the Proposed Approach

### 6.1 Multi-Source Dataset Ingestion and Label Correction (`prepare_data.py`)
To prevent model overfitting and eliminate synthetic bias, five disparate real-world datasets were aggregated and normalized:
1. **Kaggle Password Strength Dataset (bhavikbb):** 669,639 passwords with initial labels (0, 1, 2).
2. **RockYou Leak Corpus:** 199,987 confirmed breach passwords.
3. **Xato 10-Million Dataset:** 499,997 entries from user password studies.
4. **Top 10k Common Passwords (SecLists):** 10,000 most frequently exploited passwords.
5. **CSPRNG High-Entropy Set:** 50,000 cryptographically random strings.

#### The Breakthrough: Dictionary-Corrected Ground Truth Labeling
A custom dictionary of 118,914 common terms and leaked roots was extracted. Any credential containing common breach words or matching dictionary roots was systematically forced to **Class 0 (Weak)**:
* **Over 110,632 heuristic labels were corrected**, transforming misleading "strong" labels into accurate "weak" ground truths.
* **Data Splits Created:**
  * `combined_train.csv`: 660,565 training passwords.
  * `clean_test.csv`: 15,000 balanced evaluation passwords (5,000 Weak, 5,000 Medium, 5,000 Strong) with zero training data contamination.

### 6.2 Feature Engineering Pipeline (`features.py`)
Fifteen security-specific mathematical features are extracted for each password string $S$:

$$\text{Shannon Entropy: } H(S) = -\sum_{i=1}^{k} p(c_i) \log_2 p(c_i)$$

```python
# 15 engineered features extracted per candidate password
def extract_all_features(password: str, dictionary_words: set) -> dict:
    length = len(password)
    entropy = calculate_shannon_entropy(password)
    dict_hit = 1 if is_dictionary_word_or_variant(password, dictionary_words) else 0
    unique_chars = len(set(password))
    ratio_unique = unique_chars / length if length > 0 else 0
    
    # Counts and ratios for character classes
    n_upper = sum(1 for c in password if c.isupper())
    n_lower = sum(1 for c in password if c.islower())
    n_digits = sum(1 for c in password if c.isdigit())
    n_symbols = sum(1 for c in password if not c.isalnum())
    
    # Structural sequence and pattern detection
    transitions = count_character_class_transitions(password)
    sequential = detect_sequential_patterns(password) # e.g. "abc", "123", "qwe"
    repeats = detect_consecutive_repeats(password)     # e.g. "aaa", "111"
    common_pats = detect_year_and_common_suffixes(password) # e.g. "2024", "!"
    
    return {
        "dictionary_hit": dict_hit, "length": length, "entropy": entropy,
        "count_unique_chars": unique_chars, "ratio_unique_chars": ratio_unique,
        "count_uppercase": n_upper, "ratio_uppercase": n_upper / length,
        "count_lowercase": n_lower, "ratio_lowercase": n_lower / length,
        "count_digits": n_digits, "ratio_digits": n_digits / length,
        "count_symbols": n_symbols, "ratio_symbols": n_symbols / length,
        "transitions": transitions, "sequential_patterns": sequential,
        "repeats": repeats, "common_patterns": common_pats
    }
```

### 6.3 Model Training and Feature Importance (`train_model.py`)
Random Forest (100 estimators) and XGBoost (max depth 6, learning rate 0.1) classifiers were trained. The feature importance distribution demonstrates that dictionary awareness and length dominate true password resilience:
1. **`dictionary_hit`**: **36.79%**
2. **`length`**: **26.91%**
3. **`count_unique_chars`**: **6.57%**
4. **`count_uppercase`**: **5.95%**
5. **`entropy`**: **5.63%**
6. **`ratio_uppercase`**: **4.26%**
7. **`count_lowercase`**: **2.72%**

### 6.4 Privacy-Preserving HIBP Integration (`hibp_check.ts`)
```typescript
export async function checkPasswordBreach(password: string): Promise<{ breached: boolean; count: number }> {
  const enc = new TextEncoder();
  const hashBuffer = await crypto.subtle.digest('SHA-1', enc.encode(password));
  const hashHex = Array.from(new Uint8Array(hashBuffer))
    .map(b => b.toString(16).padStart(2, '0')).join('').toUpperCase();
    
  const prefix = hashHex.slice(0, 5); // 20-bit k-anonymity prefix
  const suffix = hashHex.slice(5);
  
  const response = await fetch(`https://api.pwnedpasswords.com/range/${prefix}`);
  const text = await response.text();
  
  for (const line of text.split('\n')) {
    const [h, count] = line.split(':');
    if (h.trim() === suffix) {
      return { breached: true, count: parseInt(count.trim(), 10) };
    }
  }
  return { breached: false, count: 0 };
}
```

---

## 7. Results and Analysis

All experimental evaluations were conducted on a standardized hardware and software testbed (Windows 11, Node.js 24 LTS, Python 3.13, Intel 64-bit multi-core architecture).

### 7.1 ML Classifier Performance Comparison

#### 7.1.1 Evaluation on Clean Multi-Source Test Set (15,000 Balanced Passwords)
The models were evaluated against an independent, balanced test set composed of 5,000 Weak, 5,000 Medium, and 5,000 Strong passwords with zero data contamination:

**Table 7.1: Performance Comparison on Clean Multi-Source Test Set**
| Model / Technique | Accuracy | Macro F1-Score | Weak (0) F1 | Medium (1) F1 | Strong (2) F1 |
|---|:---:|:---:|:---:|:---:|:---:|
| **Rule-Based (Base Paper)** | 90.89% | 90.73% | 84.61% | 87.98% | 99.59% |
| **zxcvbn (Wheeler et al.)** | 84.81% | 84.65% | 81.94% | 78.53% | 93.47% |
| **Random Forest (Proposed)** | **94.35%** | **94.32%** | **91.08%** | **92.21%** | **99.66%** |
| **XGBoost (Proposed)** | **94.35%** | **94.32%** | **91.08%** | **92.22%** | **99.65%** |

#### 7.1.2 Evaluation on Standard Split (21,000 Stratified Samples)
**Table 7.2: Classification Metrics on Standard Split**
| Model / Technique | Accuracy | Macro F1 | Weak (0) F1 | Medium (1) F1 | Strong (2) F1 |
|---|:---:|:---:|:---:|:---:|:---:|
| **Rule-Based (Base Paper)** | 82.74% | 81.51% | 65.41% | 79.48% | 99.65% |
| **zxcvbn** | 78.94% | 78.39% | 69.64% | 72.61% | 92.91% |
| **Random Forest (Proposed)** | **99.73%** | **99.73%** | **99.95%** | **99.59%** | **99.64%** |
| **XGBoost (Proposed)** | **99.77%** | **99.77%** | **99.95%** | **99.66%** | **99.71%** |

#### Critical Findings and Comparative Discussion:
1. **Decisive Weak Password Detection Superiority:** On the standard test set, the base paper's rule-based meter achieved only **65.41% F1 on weak passwords**, misclassifying over 34% of dangerous passwords as medium or strong. The proposed ML model achieved **99.95% F1**, completely eliminating these dangerous misclassifications.
2. **Generalization across Leak Sets:** On the clean multi-source test set, the proposed ML models achieved **94.35% overall accuracy** compared to 90.89% for rule-based (+3.46% absolute improvement) and 84.81% for zxcvbn (+9.54% improvement).
3. **Flaw of Composition Rules Exposed:** Common dictionary passwords with standard substitutions (`P@ssw0rd1!`, `Summer2024!`) fool the base paper's rule-based meter completely, but are immediately flagged as weak by our ML model because of the heavy weight on `dictionary_hit` (36.79%).

### 7.2 Generated Experimental Visualizations
The experimental pipeline produced 7 analytical charts:
* **Confusion Matrices:** `confusion_matrix_rf.png` and `confusion_matrix_xgb.png` confirming near-zero false negatives for weak passwords.
* **ROC Curve:** `roc_curve.png` showing an Area Under the Curve (AUC) exceeding 0.99 for all three classes.
* **Feature Importance Chart:** `feature_importance.png` illustrating how dictionary lookups and string length overshadow superficial character counts.
* **Comparison Bar Chart:** `comparison_bar_chart.png` depicting head-to-head performance across all four estimators.
* **KDF Benchmark Visualizations:** `kdf_benchmark_bar.png` and `kdf_benchmark_table.png`.

### 7.3 HIBP Breach-Exposure Evaluation
**Table 7.3: HIBP Threat Intelligence Experimental Results**
| Parameter / Metric | Measured Observation |
|---|---|
| Passwords Evaluated in Live Verification | 20 real-world sample credentials |
| Breached Credentials Successfully Identified | 16 / 20 (80.0% breach exposure) |
| Known Breach Frequency Detected | `password`: 10,434,572 times; `iloveyou`: 3,842,109 times |
| False Negative Rate for Hash Matching | 0% (exact SHA-1 hash lookup) |
| Average Network Latency | **497.3 ms** |
| User Privacy Preserved | **100% (only 5 hex prefix characters transmitted)** |

**Takeaway:** No offline classifier (rule-based or ML) can know if an arbitrary high-entropy password has appeared in a breach dump. Integrating client-side HIBP $k$-anonymity provides essential defense-in-depth.

### 7.4 KDF Cryptographic Benchmarking (PBKDF2 vs Argon2id)
**Table 7.4: Cryptographic Key Derivation Benchmark**
| Algorithm | Parameter Configuration | Execution Time (Mean ± Std) | Memory Allocation | GPU / ASIC Resistance |
|---|---|:---:|:---:|:---:|
| **PBKDF2-HMAC-SHA256** | 100,000 iterations | 39.33 ± 1.88 ms | ~0 KB | Low |
| **PBKDF2-HMAC-SHA256** | 300,000 iterations | 114.76 ± 2.87 ms | ~0 KB | Low |
| **PBKDF2-HMAC-SHA256** | 600,000 iterations (OWASP) | **232.35 ± 6.21 ms** | ~0 KB | Low |
| **PBKDF2-HMAC-SHA256** | 1,000,000 iterations | 387.10 ± 7.18 ms | ~0 KB | Low |
| **Argon2id** | $m=19\,\text{MB}$, $t=2$, $p=1$ | 35.36 ± 4.29 ms | 19,456 KB | High |
| **Argon2id** | $m=46\,\text{MB}$, $t=1$, $p=1$ | 31.03 ± 2.46 ms | 47,104 KB | Very High |
| **Argon2id** | $m=64\,\text{MB}$, $t=3$, $p=4$ | **44.25 ± 3.63 ms** | **65,536 KB** | **Maximum** |

**Discussion:**
* At OWASP's recommended 600,000 iterations, PBKDF2 requires **232.35 ms** of CPU time while offering zero memory hardness, allowing attackers to parallelize cracking across thousands of GPU shader cores.
* Argon2id with 64 MB of RAM and 3 iterations executes in **44.25 ms—over 5× faster on client CPUs** while enforcing a 64 MB memory barrier per guess that completely incapacitates GPU cracking rigs.

---

## 8. Conclusion

### 8.1 Summary of Work Carried Out
This application-based project thoroughly investigated, implemented, audited, and enhanced the zero-knowledge password manager concept presented in the base article (IJRASET, Dec 2025). 

We developed a complete 37-file full-stack architecture comprising a React 18 / TypeScript frontend with native Web Crypto API cryptographic operations, and an Express.js / PostgreSQL backend. Through rigorous security auditing, we identified fundamental vulnerabilities in the baseline approach:
1. Deceptive rule-based strength estimation.
2. Complete absence of breach threat intelligence.
3. Vulnerability of PBKDF2 to GPU-accelerated mass attacks.
4. Total absence of empirical data or validation.

To solve these challenges, we implemented three major enhancements:
1. An **ML-Based Strength Classifier** powered by Random Forest and XGBoost trained on 15 features across 1.29 million passwords with dictionary-corrected ground-truth labeling.
2. A **Privacy-Preserving Breach Detection Engine** utilizing Have I Been Pwned's API with $k$-anonymity.
3. A **Formal KDF Cryptographic Benchmark** comparing PBKDF2 and Argon2id.

### 8.2 Major Findings and Effectiveness of Proposed Approach
* **Detection of Weak Passwords:** On an independent 15,000-password balanced clean test set, the proposed ML models achieved **94.35% accuracy** and **91.08% Weak F1**, outperforming the base paper's rule-based meter (**90.89% accuracy, 84.61% Weak F1**) and standard zxcvbn (**84.81% accuracy, 81.94% Weak F1**). On the standard test split, the ML classifier achieved **99.95% Weak F1 vs. 65.41% for rule-based**, successfully eliminating false "strong" ratings for passwords like `P@ssw0rd1!`.
* **Breach Prevention:** The $k$-anonymity breach check identified 80% of test credentials as compromised with zero disclosure of user passwords and an average latency of only 497.3 ms.
* **Cryptographic Efficiency:** Argon2id proved over 5× faster than PBKDF2-600k on client CPUs (44.25 ms vs 232.35 ms) while imposing a 64 MB memory requirement that cripples GPU attack hardware.

### 8.3 Future Work
1. **Client-Side WASM Inference:** Export the trained XGBoost model to ONNX WebAssembly (`onnxruntime-web`) to perform ML inference directly in browser memory without local HTTP requests.
2. **Multi-Factor Authentication (MFA):** Integrate WebAuthn (FIDO2) to provide hardware-token (YubiKey) authentication for vault access.
3. **Trustless Recovery via Shamir's Secret Sharing:** Replace server-side recovery with $(k, n)$ threshold secret sharing across trusted contacts, preserving zero-knowledge guarantees.

---

## 9. References

1. **M. Kanjikar, A. Yekkele, D. Wale, N. Sharma, and N. Wadikar**, "Password Manager," *International Journal for Research in Applied Science & Engineering Technology (IJRASET)*, vol. 13, no. 12, pp. 1492–1498, Dec. 2025. DOI: [10.22214/ijraset.2025.76363](https://doi.org/10.22214/ijraset.2025.76363). *(Base Article)*
2. **National Institute of Standards and Technology (NIST)**, "Digital Identity Guidelines: Authentication and Lifecycle Management," *NIST Special Publication 800-63B*, Mar. 2020.
3. **OWASP Foundation**, "Password Storage Cheat Sheet," *OWASP Cheat Sheet Series*, 2023. [Online]. Available: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
4. **B. Kaliski**, "PKCS #5: Password-Based Cryptography Specification Version 2.1," *Internet Engineering Task Force (IETF) RFC 8018*, Jan. 2017.
5. **A. Biryukov, D. Dinu, D. Khovratovich, and S. Josefsson**, "The memory-hard Argon2 password hash and proof-of-work function," *Internet Engineering Task Force (IETF) RFC 9106*, Sep. 2021.
6. **D. L. Wheeler**, "zxcvbn: Low-Budget Password Strength Estimation," in *Proceedings of the 25th USENIX Security Symposium*, Austin, TX, USA, Aug. 2016, pp. 157–173.
7. **T. Hunt**, "Have I Been Pwned: Pwned Passwords API v3," 2023. [Online]. Available: https://haveibeenpwned.com/Passwords
8. **M. Dworkin**, "Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC," *NIST Special Publication 800-38D*, Nov. 2007.
9. **W. Melicher, B. Ur, S. M. Segreti, S. Komanduri, L. Bauer, N. Christin, and L. F. Cranor**, "Fast, Lean, and Accurate: Modeling Password Guessability Using Neural Networks," in *Proceedings of the 25th USENIX Security Symposium*, Austin, TX, USA, Aug. 2016, pp. 175–191.
10. **D. Florêncio and C. Herley**, "A Large-Scale Study of Web Password Habits," in *Proceedings of the 16th International Conference on World Wide Web (WWW'07)*, Banff, Alberta, Canada, 2007, pp. 657–666.
11. **B. B. Bhavik**, "Password Strength Classifier Dataset," *Kaggle*, 2023. [Online]. Available: https://www.kaggle.com/datasets/bhavikbb/password-strength-classifier-dataset
12. **D. Miessler**, "SecLists: The Hacker's Companion," *GitHub Repository*, 2023. [Online]. Available: https://github.com/danielmiessler/SecLists
13. **Verizon Business**, "2024 Data Breach Investigations Report (DBIR)," *Verizon Enterprise Solutions*, May 2024. [Online]. Available: https://www.verizon.com/business/resources/reports/dbir/
