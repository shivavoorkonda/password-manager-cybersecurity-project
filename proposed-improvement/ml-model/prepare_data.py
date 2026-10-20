"""
prepare_data.py - Combines multiple datasets for training and evaluation.

Datasets used:
  1. Kaggle Password Strength Classifier (bhavikbb) - ~670k labelled passwords
  2. RockYou wordlist - 14M leaked passwords (used as "known weak" class)
  3. SecLists Common Passwords - top 10k/100k common passwords (weak class)
  4. Xato 10-million password list (from SecLists) - additional weak/medium
  5. Synthetically generated strong passwords (our generator) - strong class

This script creates:
  - combined_train.csv  (for model training)
  - clean_test.csv      (multi-source test set, NOT from Kaggle heuristic labels)
  - dictionary.txt      (merged dictionary for feature extraction)
"""

import argparse
import os
import string
import secrets
import math
import csv
import random
from pathlib import Path
from collections import Counter

import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def generate_strong_password(length: int = None) -> str:
    """Generate a cryptographically random strong password."""
    if length is None:
        length = random.randint(14, 24)
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_passphrase(word_list: list, n_words: int = None) -> str:
    """Generate a random passphrase from a word list."""
    if n_words is None:
        n_words = random.randint(4, 6)
    words = [secrets.choice(word_list) for _ in range(n_words)]
    sep = secrets.choice(['-', '_', '.', ' '])
    return sep.join(words)


def load_lines(path: str, limit: int = None, encoding: str = 'utf-8') -> list:
    """Load lines from a text file, stripping whitespace."""
    lines = []
    try:
        with open(path, 'r', encoding=encoding, errors='ignore') as f:
            for i, line in enumerate(f):
                if limit and i >= limit:
                    break
                stripped = line.strip()
                if stripped:
                    lines.append(stripped)
    except FileNotFoundError:
        print(f"  [SKIP] File not found: {path}")
    return lines


def compute_entropy(password: str) -> float:
    """Shannon entropy of a password."""
    if not password:
        return 0.0
    counts = Counter(password)
    length = len(password)
    return -sum((c / length) * math.log2(c / length) for c in counts.values())


def heuristic_strength(password: str) -> int:
    """
    A more realistic strength label than pure rule-based:
      0 = weak   (short, low entropy, or common pattern)
      1 = medium (moderate length + some complexity)
      2 = strong (long, high entropy, mixed classes)
    """
    if not password or len(password) < 6:
        return 0

    length = len(password)
    entropy = compute_entropy(password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(not c.isalnum() for c in password)
    char_classes = sum([has_upper, has_lower, has_digit, has_symbol])

    # Definitely weak
    if length < 8:
        return 0
    if entropy < 2.5:
        return 0

    # Strong criteria
    if length >= 14 and entropy >= 3.5 and char_classes >= 3:
        return 2
    if length >= 12 and entropy >= 3.8 and char_classes >= 4:
        return 2

    # Medium
    if length >= 8 and entropy >= 2.8 and char_classes >= 2:
        return 1

    return 0


# ---------------------------------------------------------------------------
# Dataset loaders
# ---------------------------------------------------------------------------

def load_kaggle_dataset(path: str) -> pd.DataFrame:
    """Load the bhavikbb Kaggle Password Strength Classifier Dataset."""
    print(f"\n[1/5] Loading Kaggle dataset from {path}...")
    df = pd.read_csv(path)
    # Expected columns: password, strength (0, 1, 2)
    df = df[['password', 'strength']].dropna()
    df['password'] = df['password'].astype(str)
    df['source'] = 'kaggle'
    print(f"  Loaded {len(df)} passwords (Weak: {(df.strength==0).sum()}, "
          f"Medium: {(df.strength==1).sum()}, Strong: {(df.strength==2).sum()})")
    return df


def load_rockyou(path: str, limit: int = 200000) -> pd.DataFrame:
    """Load RockYou wordlist as 'weak' passwords."""
    print(f"\n[2/5] Loading RockYou wordlist from {path} (limit={limit})...")
    lines = load_lines(path, limit=limit)
    if not lines:
        return pd.DataFrame(columns=['password', 'strength', 'source'])
    df = pd.DataFrame({'password': lines, 'strength': 0, 'source': 'rockyou'})
    # Remove very short or empty
    df = df[df['password'].str.len() >= 3]
    print(f"  Loaded {len(df)} passwords (all labelled Weak)")
    return df


def load_seclists(base_path: str) -> pd.DataFrame:
    """
    Load common password lists from SecLists.
    Looks for files in: <base_path>/Passwords/Common-Credentials/
    """
    print(f"\n[3/5] Loading SecLists common passwords from {base_path}...")
    target_dir = os.path.join(base_path, 'Passwords', 'Common-Credentials')
    all_passwords = []

    # Try specific well-known files
    files_to_try = [
        'top-passwords-shortlist.txt',
        '10-million-password-list-top-10000.txt',
        '10-million-password-list-top-100000.txt',
        '10k-most-common.txt',
        'best1050.txt',
        'common-passwords-win.txt',
    ]

    # Also try the base_path directly (user may have put files there)
    search_dirs = [target_dir, base_path]

    for search_dir in search_dirs:
        for fname in files_to_try:
            fpath = os.path.join(search_dir, fname)
            lines = load_lines(fpath, limit=100000)
            if lines:
                all_passwords.extend(lines)
                print(f"  Loaded {len(lines)} from {fname}")

    if not all_passwords:
        print("  [SKIP] No SecLists files found. Place them in datasets/seclists/")
        return pd.DataFrame(columns=['password', 'strength', 'source'])

    # Deduplicate
    all_passwords = list(set(all_passwords))
    df = pd.DataFrame({'password': all_passwords, 'strength': 0, 'source': 'seclists'})
    df = df[df['password'].str.len() >= 3]
    print(f"  Total unique SecLists passwords: {len(df)} (all labelled Weak)")
    return df


def load_xato(path: str, limit: int = 500000) -> pd.DataFrame:
    """Load the Xato 10-million password list (subset)."""
    print(f"\n[4/5] Loading Xato password list from {path} (limit={limit})...")
    if path.lower().endswith('.csv'):
        try:
            raw = pd.read_csv(path, nrows=limit, on_bad_lines='skip')
            column = 'password' if 'password' in raw.columns else raw.columns[-1]
            lines = raw[column].dropna().astype(str).tolist()
        except FileNotFoundError:
            print(f"  [SKIP] File not found: {path}")
            lines = []
    else:
        lines = load_lines(path, limit=limit)
    if not lines:
        return pd.DataFrame(columns=['password', 'strength', 'source'])

    # Label using our heuristic (not just "all weak" since Xato has a mix)
    records = []
    for pwd in lines:
        records.append({
            'password': pwd,
            'strength': heuristic_strength(pwd),
            'source': 'xato'
        })
    df = pd.DataFrame(records)
    df = df[df['password'].str.len() >= 3]
    print(f"  Loaded {len(df)} passwords (Weak: {(df.strength==0).sum()}, "
          f"Medium: {(df.strength==1).sum()}, Strong: {(df.strength==2).sum()})")
    return df


def generate_strong_set(n: int = 50000, english_words_path: str = None) -> pd.DataFrame:
    """Generate synthetic strong passwords and passphrases."""
    print(f"\n[5/5] Generating {n} synthetic strong passwords...")
    passwords = []

    # 70% random strings
    for _ in range(int(n * 0.7)):
        passwords.append(generate_strong_password())

    # 30% passphrases (if we have a word list)
    word_list = None
    if english_words_path:
        word_list = load_lines(english_words_path, limit=10000)
        word_list = [w for w in word_list if 4 <= len(w) <= 8]

    if word_list and len(word_list) > 100:
        for _ in range(int(n * 0.3)):
            passwords.append(generate_passphrase(word_list))
    else:
        # Fall back to more random strings
        for _ in range(int(n * 0.3)):
            passwords.append(generate_strong_password(random.randint(16, 28)))

    df = pd.DataFrame({'password': passwords, 'strength': 2, 'source': 'generated'})
    print(f"  Generated {len(df)} strong passwords")
    return df


# ---------------------------------------------------------------------------
# Dictionary builder
# ---------------------------------------------------------------------------

def load_top10k(path: str) -> pd.DataFrame:
    """Load the checked-in common-password list and label entries as weak."""
    print(f"\nLoading top-10k common passwords from {path}...")
    try:
        raw = pd.read_csv(path, on_bad_lines='skip')
    except FileNotFoundError:
        print(f"  [SKIP] File not found: {path}")
        return pd.DataFrame(columns=['password', 'strength', 'source'])
    column = 'password' if 'password' in raw.columns else raw.columns[0]
    passwords = raw[column].dropna().astype(str).str.strip()
    df = pd.DataFrame({'password': passwords, 'strength': 0, 'source': 'top10k'})
    df = df[df['password'].str.len() >= 3].drop_duplicates(subset=['password'])
    print(f"  Loaded {len(df)} common passwords (labelled weak by source, not measured).")
    return df


def build_dictionary(rockyou_path: str, seclists_path: str, output_path: str,
                     top10k_path: str = None,
                     limit: int = 100000) -> set:
    """
    Build a merged dictionary of common/weak passwords for feature extraction.
    This dictionary is used by features.py to check dictionary_hit().
    """
    print("\nBuilding merged dictionary for feature extraction...")
    dictionary = set()

    # RockYou (first 100k)
    lines = load_lines(rockyou_path, limit=limit)
    dictionary.update(l.lower() for l in lines)
    print(f"  RockYou: {len(lines)} entries")

    # SecLists
    seclists_files = [
        os.path.join(seclists_path, 'Passwords', 'Common-Credentials',
                     '10-million-password-list-top-10000.txt'),
        os.path.join(seclists_path, 'Passwords', 'Common-Credentials',
                     '10-million-password-list-top-100000.txt'),
        os.path.join(seclists_path, '10k-most-common.txt'),
    ]
    for fpath in seclists_files:
        lines = load_lines(fpath)
        if lines:
            dictionary.update(l.lower() for l in lines)
            print(f"  SecLists ({os.path.basename(fpath)}): {len(lines)} entries")

    # Common English words (for substring matching)
    common_words = [
        'password', 'qwerty', 'dragon', 'master', 'monkey', 'shadow',
        'sunshine', 'princess', 'football', 'charlie', 'trustno1',
        'iloveyou', 'batman', 'access', 'hello', 'love', 'summer',
        'winter', 'spring', 'autumn', 'letmein', 'welcome', 'admin',
        'login', 'passw0rd', 'starwars', 'soccer', 'michael', 'ashley',
        'baseball', 'killer', 'whatever', 'jordan', 'daniel', 'hannah',
    ]
    dictionary.update(common_words)
    if top10k_path:
        top10k = load_top10k(top10k_path)
        dictionary.update(top10k['password'].str.lower().tolist())

    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        for word in sorted(dictionary):
            f.write(word + '\n')

    print(f"  Total dictionary size: {len(dictionary)} unique entries")
    print(f"  Saved to {output_path}")
    return dictionary


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Prepare multi-source dataset for password strength classifier.'
    )
    parser.add_argument('--kaggle-path', type=str,
                        default='../../datasets/password_strength.csv',
                        help='Path to Kaggle bhavikbb dataset CSV')
    parser.add_argument('--rockyou-path', type=str,
                        default='../../datasets/rockyou.txt',
                        help='Path to rockyou.txt')
    parser.add_argument('--seclists-path', type=str,
                        default='../../datasets/seclists',
                        help='Path to SecLists root directory')
    parser.add_argument('--xato-path', type=str,
                        default='../../datasets/xato-net-10-million-passwords.csv',
                        help='Path to Xato 10-million password list')
    parser.add_argument('--top10k-path', type=str,
                        default='../../datasets/top10k-common-passwords.csv',
                        help='Path to the checked-in common-password list')
    parser.add_argument('--output-dir', type=str,
                        default='../../datasets',
                        help='Output directory for processed datasets')
    parser.add_argument('--n-strong', type=int, default=50000,
                        help='Number of synthetic strong passwords to generate')
    parser.add_argument('--rockyou-limit', type=int, default=200000,
                        help='Max lines to load from RockYou')
    parser.add_argument('--xato-limit', type=int, default=500000,
                        help='Max lines to load from Xato list')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # -----------------------------------------------------------------------
    # Load all datasets
    # -----------------------------------------------------------------------
    datasets = []

    # 1. Kaggle (primary labelled dataset)
    kaggle_df = load_kaggle_dataset(args.kaggle_path)
    datasets.append(kaggle_df)

    # 2. RockYou (weak passwords)
    rockyou_df = load_rockyou(args.rockyou_path, limit=args.rockyou_limit)
    if len(rockyou_df) > 0:
        datasets.append(rockyou_df)

    # 3. SecLists (weak passwords)
    seclists_df = load_seclists(args.seclists_path)
    if len(seclists_df) > 0:
        datasets.append(seclists_df)

    # The repository includes a top10k CSV; load it explicitly even without SecLists.
    top10k_df = load_top10k(args.top10k_path)
    if len(top10k_df) > 0:
        datasets.append(top10k_df)

    # 4. Xato (mixed, labelled by entropy heuristic)
    xato_df = load_xato(args.xato_path, limit=args.xato_limit)
    if len(xato_df) > 0:
        datasets.append(xato_df)

    # 5. Generated strong passwords
    strong_df = generate_strong_set(n=args.n_strong)
    datasets.append(strong_df)

    # -----------------------------------------------------------------------
    # Combine and split
    # -----------------------------------------------------------------------
    combined = pd.concat(datasets, ignore_index=True)

    # Remove exact duplicates (keep first occurrence)
    before = len(combined)
    combined = combined.drop_duplicates(subset=['password'], keep='first')
    print(f"\nDeduplicated: {before} -> {len(combined)} passwords")

    # Print distribution
    print("\nCombined dataset distribution:")
    print(f"  Weak (0):   {(combined.strength==0).sum():>8,}")
    print(f"  Medium (1): {(combined.strength==1).sum():>8,}")
    print(f"  Strong (2): {(combined.strength==2).sum():>8,}")
    print(f"  Total:      {len(combined):>8,}")

    print("\nBy source:")
    for src in combined['source'].unique():
        count = (combined.source == src).sum()
        print(f"  {src:<15} {count:>8,}")

    # -----------------------------------------------------------------------
    # Create training set (Kaggle + supplements)
    # and clean test set (RockYou weak + generated strong + Xato medium)
    # -----------------------------------------------------------------------
    # Training: primarily Kaggle, supplemented with some RockYou and generated
    train_mask = combined['source'].isin(['kaggle'])
    supplement_mask = combined['source'].isin(['rockyou', 'seclists', 'xato', 'generated'])

    # Take a sample from supplementary sources for training
    supplement = combined[supplement_mask].copy()
    if len(supplement) > 100000:
        supplement = supplement.groupby('strength', group_keys=False).apply(
            lambda x: x.sample(min(len(x), 33333), random_state=42)
        )

    train_data = pd.concat([combined[train_mask], supplement], ignore_index=True)
    train_data = train_data.drop_duplicates(subset=['password'], keep='first')
    train_data = train_data.sample(frac=1, random_state=42).reset_index(drop=True)

    # Clean test set: passwords NOT in training set
    # Use RockYou (weak), generated (strong), and some Xato (medium)
    train_passwords = set(train_data['password'].values)

    test_candidates = combined[~combined['password'].isin(train_passwords)].copy()
    # Balance test set
    test_per_class = 5000
    test_parts = []
    for strength_val in [0, 1, 2]:
        subset = test_candidates[test_candidates['strength'] == strength_val]
        n_sample = min(len(subset), test_per_class)
        if n_sample > 0:
            test_parts.append(subset.sample(n=n_sample, random_state=42))
            print(f"  Clean test class {strength_val}: {n_sample} samples")
        else:
            print(f"  Clean test class {strength_val}: 0 samples (insufficient data)")

    if test_parts:
        test_data = pd.concat(test_parts, ignore_index=True)
        test_data = test_data.sample(frac=1, random_state=42).reset_index(drop=True)
    else:
        test_data = pd.DataFrame(columns=['password', 'strength', 'source'])

    # -----------------------------------------------------------------------
    # Save
    # -----------------------------------------------------------------------
    train_path = os.path.join(args.output_dir, 'combined_train.csv')
    test_path = os.path.join(args.output_dir, 'clean_test.csv')

    train_data.to_csv(train_path, index=False)
    test_data.to_csv(test_path, index=False)

    print(f"\n{'='*60}")
    print(f"Training set: {len(train_data):,} passwords -> {train_path}")
    print(f"  Weak: {(train_data.strength==0).sum():,}  "
          f"Medium: {(train_data.strength==1).sum():,}  "
          f"Strong: {(train_data.strength==2).sum():,}")
    print(f"Clean test set: {len(test_data):,} passwords -> {test_path}")
    print(f"  Weak: {(test_data.strength==0).sum():,}  "
          f"Medium: {(test_data.strength==1).sum():,}  "
          f"Strong: {(test_data.strength==2).sum():,}")

    # -----------------------------------------------------------------------
    # Build dictionary
    # -----------------------------------------------------------------------
    dict_path = os.path.join(args.output_dir, 'dictionary.txt')
    build_dictionary(args.rockyou_path, args.seclists_path, dict_path,
                     top10k_path=args.top10k_path)

    print(f"\n{'='*60}")
    print("Data preparation complete!")
    print("\nNext steps:")
    print("  1. python train_model.py --dataset-path ../../datasets/combined_train.csv \\")
    print("       --dict-path ../../datasets/dictionary.txt")
    print("  2. python evaluate_model.py --dataset-path ../../datasets/combined_train.csv \\")
    print("       --clean-test-path ../../datasets/clean_test.csv \\")
    print("       --dict-path ../../datasets/dictionary.txt")


if __name__ == '__main__':
    main()
