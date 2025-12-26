import re
from difflib import SequenceMatcher
import nepali_datetime
import datetime

# --- 1. MAPPINGS ---

# Map Nepali Consonants to English (Skeleton Mapping)
NEP_CONSONANT_MAP = {
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'n',
    'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'n',
    'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
    'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'f', 'ब': 'b', 'भ': 'bh', 'म': 'm',
    'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'b', 'श': 's', 
    'ष': 'sh', 'स': 's', 'ह': 'h', 'क्ष': 'ksh', 'त्र': 'tr', 'ज्ञ': 'gy'
}

NEP_TO_ENG_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
ENG_TO_NEP_DIGITS = str.maketrans("0123456789", "०१२३४५६७८९")

# --- 2. HELPERS ---

def get_consonant_skeleton(text, script="english"):
    """
    Extracts the 'skeleton' of the word by removing vowels and matras.
    'Manjil' -> 'mnjl'
    'मन्जिल' -> 'mnjl'
    """
    skeleton = ""
    text = text.lower().strip()
    
    if script == "nepali":
        for char in text:
            if char in NEP_CONSONANT_MAP:
                skeleton += NEP_CONSONANT_MAP[char]
    else:
        # English: Remove a, e, i, o, u, y(sometimes), spaces, special chars
        # Keep only basic consonants
        clean_text = re.sub(r'[^a-z]', '', text)
        for char in clean_text:
            if char not in "aeiou":
                skeleton += char
                
    return skeleton

def fuzzy_match(a, b):
    return int(SequenceMatcher(None, a, b).ratio() * 100)

def normalize_text(text):
    return re.sub(r'\s+', ' ', text.strip().lower()) if text else ""

# --- 3. VERIFIERS ---

def verify_name(u_name, raw_text, norm_text):
    """
    Uses 'Consonant Skeleton' matching to handle spelling variations.
    """
    full_corpus = raw_text + " " + norm_text
    
    # 1. Direct English Match
    if u_name.lower() in full_corpus.lower():
        return {"score": 100, "status": "MATCH", "span": u_name, "error_type": "SUCCESS"}

    # 2. Consonant Skeleton Match (Cross-Script)
    # Convert User Input to Skeleton (Manjil -> mnjl)
    u_skeleton = get_consonant_skeleton(u_name, "english")
    
    # Extract Nepali parts from OCR and convert to Skeleton (मन्जिल -> mnjl)
    nepali_text = "".join(re.findall(r'[\u0900-\u097F]+', full_corpus))
    ocr_skeleton = get_consonant_skeleton(nepali_text, "nepali")
    
    # Fuzzy match the skeletons
    score = 0
    if u_skeleton and ocr_skeleton:
        # Search for the user skeleton inside the massive OCR skeleton
        if u_skeleton in ocr_skeleton:
            score = 100 
        else:
            # Fallback: Check similarity
            score = fuzzy_match(u_skeleton, ocr_skeleton)
            # Boost score if substring match
            if u_skeleton in ocr_skeleton: score = 100

    return {
        "score": score,
        "status": "MATCH" if score > 80 else "PARTIAL" if score > 50 else "MISMATCH",
        "span": f"Skeleton Match ({u_skeleton})",
        "error_type": "SUCCESS" if score > 80 else "NAME_MISMATCH"
    }

def verify_id_number(u_id, raw_text, norm_text):
    """
    Checks ID digits. Handles 07 vs 05 explicitly.
    """
    full_text = (raw_text + " " + norm_text).translate(NEP_TO_ENG_DIGITS)
    ocr_digits = re.sub(r'\D', '', full_text)
    u_digits = re.sub(r'\D', '', u_id)
    
    if u_digits in ocr_digits:
        return {"score": 100, "status": "MATCH", "span": u_id, "error_type": "SUCCESS"}
    
    # If not found, return 0 (Strict ID checking)
    return {"score": 0, "status": "MISMATCH", "span": "Not Found", "error_type": "ID_DIGIT_MISREAD"}

def verify_dob(u_dob, raw_text, norm_text):
    """
    Smart Date Verification:
    - Converts User AD -> BS (Nep Date)
    - Checks both AD and BS tokens in text
    """
    full_corpus = (raw_text + " " + norm_text).translate(NEP_TO_ENG_DIGITS) # Normalize to Eng Digits
    
    # 1. Parse User Date (AD)
    try:
        y_ad, m_ad, d_ad = map(int, u_dob.split('-'))
        u_ad_tokens = {str(y_ad), f"{m_ad:02}", f"{d_ad:02}"}
        
        # 2. Convert to BS (Nepali Date)
        ad_date = datetime.date(y_ad, m_ad, d_ad)
        bs_date = nepali_datetime.date.from_datetime_date(ad_date)
        y_bs, m_bs, d_bs = bs_date.year, bs_date.month, bs_date.day
        
        u_bs_tokens = {str(y_bs), f"{m_bs:02}", f"{d_bs:02}"}
        
        # Also allow single digit match (e.g. '01' matching '1')
        u_bs_tokens.add(str(m_bs))
        u_bs_tokens.add(str(d_bs))

    except Exception as e:
        return {"score": 0, "status": "ERROR", "span": str(e), "error_type": "DATE_PARSE_ERR"}

    # 3. Search Corpus
    # Check AD Match (Back of card usually)
    ad_matches = [t for t in u_ad_tokens if t in full_corpus]
    
    # Check BS Match (Front of card usually)
    bs_matches = [t for t in u_bs_tokens if t in full_corpus]
    
    # Decision: Need at least Year + (Month or Day)
    has_year_ad = str(y_ad) in full_corpus
    has_year_bs = str(y_bs) in full_corpus
    
    match_ad = has_year_ad and len(ad_matches) >= 2
    match_bs = has_year_bs and len(bs_matches) >= 2
    
    if match_bs:
        return {"score": 100, "status": "MATCH", "span": f"BS: {y_bs}-{m_bs:02}-{d_bs:02}", "error_type": "SUCCESS"}
    if match_ad:
        return {"score": 100, "status": "MATCH", "span": f"AD: {y_ad}-{m_ad:02}-{d_ad:02}", "error_type": "SUCCESS"}
        
    return {"score": 0, "status": "MISMATCH", "span": f"Expected BS: {y_bs}-{m_bs}-{d_bs}", "error_type": "DOB_MISMATCH"}



def extract_structured_data(ocr_results, user_entry):
    combined_raw = " ".join([res.get('raw_text', '') for res in ocr_results])
    combined_norm = " ".join([res.get('text', '') for res in ocr_results])
    
    report = {}
    report['name'] = verify_name(user_entry.get('name', ''), combined_raw, combined_norm)
    report['id_number'] = verify_id_number(user_entry.get('id_number', ''), combined_raw, combined_norm)
    report['dob'] = verify_dob(user_entry.get('dob', ''), combined_raw, combined_norm)

    return report