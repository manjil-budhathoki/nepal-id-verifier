import re
import unicodedata
from difflib import SequenceMatcher
from app.utils.nepali import NEP_CONSONANT_MAP

def normalize_unicode(text):
    if not text: return ""
    text = unicodedata.normalize('NFKC', text)
    return "".join(ch for ch in text if unicodedata.category(ch)[0] != 'C')

def repair_spacing(text):
    # Fix Year2000 -> Year 2000
    text = re.sub(r'([a-zA-Z\u0900-\u097F])(\d)', r'\1 \2', text)
    text = re.sub(r'(\d)([a-zA-Z\u0900-\u097F])', r'\1 \2', text)
    # Fix standard keywords
    keywords = ["Year", "Month", "Day", "नाम", "थर", "जन्म", "मिति", "नं"]
    for kw in keywords:
        text = re.sub(f"({kw})", r" \1 ", text, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', text).strip()

def process_robust_text(raw_text):
    """Main pipeline called by the Service Layer."""
    if not raw_text: return ""
    text = normalize_unicode(raw_text)
    text = repair_spacing(text)
    text = re.sub(r'[:;|।!]', ' : ', text)
    return text.strip()

def get_consonant_skeleton(text, script="english"):
    """
    Extracts 'skeleton' (mnjl from Manjil or मन्जिल).
    Used for fuzzy matching across scripts.
    """
    skeleton = ""
    text = text.lower().strip()
    
    if script == "nepali":
        for char in text:
            if char in NEP_CONSONANT_MAP:
                skeleton += NEP_CONSONANT_MAP[char]
    else:
        # English: Keep consonants only
        clean_text = re.sub(r'[^a-z]', '', text)
        for char in clean_text:
            if char not in "aeiou":
                skeleton += char
    return skeleton

def fuzzy_match_score(a, b):
    return int(SequenceMatcher(None, a, b).ratio() * 100)