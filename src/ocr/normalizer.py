import re
import unicodedata

def normalize_unicode(text):
    """Layer A: Fixes Devanagari variations and removes junk."""
    if not text: return ""
    # NFKC normalizes composed/decomposed forms (critical for matching)
    text = unicodedata.normalize('NFKC', text)
    # Remove non-printable characters
    return "".join(ch for ch in text if unicodedata.category(ch)[0] != 'C')

def repair_spacing(text):
    """Layer B: Fixes concatenation like Year2000 or MonthJAN."""
    # 1. Split letters/script from digits (e.g., Year2000 -> Year 2000)
    text = re.sub(r'([a-zA-Z\u0900-\u097F])(\d)', r'\1 \2', text)
    text = re.sub(r'(\d)([a-zA-Z\u0900-\u097F])', r'\1 \2', text)

    # 2. Pad specific keywords to ensure they are distinct tokens
    keywords = ["Year", "Month", "Day", "नाम", "थर", "जन्म", "मिति", "नं"]
    for kw in keywords:
        text = re.sub(f"({kw})", r" \1 ", text, flags=re.IGNORECASE)

    # 3. Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def process_robust_text(raw_text):
    """The full Normalization Pipeline for Step 7."""
    if not raw_text: return ""
    text = normalize_unicode(raw_text)
    text = repair_spacing(text)
    # Standardize colons and separators
    text = re.sub(r'[:;|।!]', ' : ', text)
    return text.strip()