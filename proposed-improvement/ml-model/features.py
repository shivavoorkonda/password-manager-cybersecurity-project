import math
import re
from typing import Dict, Any, Set, Optional

def compute_length(password: str) -> int:
    """Returns the length of the password."""
    return len(password)

def compute_entropy(password: str) -> float:
    """Computes the Shannon entropy of the password."""
    if not password:
        return 0.0
    char_counts = {}
    for char in password:
        char_counts[char] = char_counts.get(char, 0) + 1
    entropy = 0.0
    length = len(password)
    for count in char_counts.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy

def count_uppercase(password: str) -> Dict[str, float]:
    """Counts uppercase characters and returns their count and ratio."""
    count = sum(1 for c in password if c.isupper())
    ratio = count / len(password) if password else 0.0
    return {"count_uppercase": count, "ratio_uppercase": ratio}

def count_lowercase(password: str) -> Dict[str, float]:
    """Counts lowercase characters and returns their count and ratio."""
    count = sum(1 for c in password if c.islower())
    ratio = count / len(password) if password else 0.0
    return {"count_lowercase": count, "ratio_lowercase": ratio}

def count_digits(password: str) -> Dict[str, float]:
    """Counts digit characters and returns their count and ratio."""
    count = sum(1 for c in password if c.isdigit())
    ratio = count / len(password) if password else 0.0
    return {"count_digits": count, "ratio_digits": ratio}

def count_symbols(password: str) -> Dict[str, float]:
    """Counts symbol characters (non-alphanumeric) and returns count and ratio."""
    count = sum(1 for c in password if not c.isalnum())
    ratio = count / len(password) if password else 0.0
    return {"count_symbols": count, "ratio_symbols": ratio}

def count_unique_chars(password: str) -> Dict[str, float]:
    """Counts unique characters and returns their count and ratio."""
    count = len(set(password))
    ratio = count / len(password) if password else 0.0
    return {"count_unique_chars": count, "ratio_unique_chars": ratio}

def detect_sequences(password: str) -> int:
    """Counts sequential character patterns (e.g., abc, 123, qwerty rows)."""
    password_lower = password.lower()
    seq_count = 0
    # Simple ASCII sequences
    for i in range(len(password_lower) - 2):
        if ord(password_lower[i+2]) - ord(password_lower[i+1]) == 1 and \
           ord(password_lower[i+1]) - ord(password_lower[i]) == 1:
            seq_count += 1
    
    # QWERTY rows
    qwerty_rows = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
    for row in qwerty_rows:
        for i in range(len(row) - 2):
            if row[i:i+3] in password_lower:
                seq_count += 1
                
    return seq_count

def detect_repeats(password: str) -> int:
    """Counts consecutive repeated characters."""
    repeats = 0
    for i in range(len(password) - 1):
        if password[i] == password[i+1]:
            repeats += 1
    return repeats

def _get_char_class(char: str) -> int:
    """Helper for transitions: 0=lower, 1=upper, 2=digit, 3=symbol."""
    if char.islower(): return 0
    if char.isupper(): return 1
    if char.isdigit(): return 2
    return 3

def count_char_transitions(password: str) -> int:
    """Counts transitions between character classes (e.g., lowercase to uppercase)."""
    if len(password) <= 1:
        return 0
    transitions = 0
    for i in range(len(password) - 1):
        if _get_char_class(password[i]) != _get_char_class(password[i+1]):
            transitions += 1
    return transitions

def dictionary_hit(password: str, dictionary_set: Optional[Set[str]]) -> int:
    """Checks if password or common substrings appear in the dictionary."""
    if not dictionary_set or not password:
        return 0
    
    pwd_lower = password.lower()
    if pwd_lower in dictionary_set:
        return 1
        
    # Check simple substrings (e.g. without trailing numbers)
    clean_pwd = re.sub(r'\d+$', '', pwd_lower)
    if clean_pwd and clean_pwd in dictionary_set:
        return 1
        
    return 0

def has_common_pattern(password: str) -> int:
    """Checks for common patterns like dates or phone numbers via regex."""
    if re.search(r'(19|20)\d{2}', password): # Years like 19xx, 20xx
        return 1
    if re.search(r'\d{4,8}', password): # Pin codes or dates
        return 1
    return 0

def extract_all_features(password: str, dictionary_set: Optional[Set[str]] = None) -> Dict[str, Any]:
    """Extracts all features from the password and returns them as a dictionary."""
    pwd = str(password) if password else ""
    features = {
        "length": compute_length(pwd),
        "entropy": compute_entropy(pwd),
        **count_uppercase(pwd),
        **count_lowercase(pwd),
        **count_digits(pwd),
        **count_symbols(pwd),
        **count_unique_chars(pwd),
        "sequences": detect_sequences(pwd),
        "repeats": detect_repeats(pwd),
        "transitions": count_char_transitions(pwd),
        "dictionary_hit": dictionary_hit(pwd, dictionary_set),
        "common_patterns": has_common_pattern(pwd)
    }
    return features
