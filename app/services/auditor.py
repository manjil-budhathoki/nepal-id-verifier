import re
import datetime
import nepali_datetime
from app.utils.text import get_consonant_skeleton, fuzzy_match_score
from app.utils.nepali import normalize_to_eng_digits

def verify_name(u_name, raw_text, norm_text):
    full_corpus = raw_text + " " + norm_text
    
    # 1. Direct English Match
    if u_name.lower() in full_corpus.lower():
        return {"score": 100, "status": "MATCH", "span": u_name, "error_type": "SUCCESS"}

    # 2. Consonant Skeleton Match
    u_skeleton = get_consonant_skeleton(u_name, "english")
    nepali_text = "".join(re.findall(r'[\u0900-\u097F]+', full_corpus))
    ocr_skeleton = get_consonant_skeleton(nepali_text, "nepali")
    
    score = 0
    if u_skeleton and ocr_skeleton:
        if u_skeleton in ocr_skeleton:
            score = 100 
        else:
            score = fuzzy_match_score(u_skeleton, ocr_skeleton)
            if u_skeleton in ocr_skeleton: score = 100

    return {
        "score": score,
        "status": "MATCH" if score > 80 else "PARTIAL" if score > 50 else "MISMATCH",
        "span": f"Skeleton: {u_skeleton}",
        "error_type": "SUCCESS" if score > 80 else "NAME_MISMATCH"
    }

def verify_id_number(u_id, raw_text, norm_text):
    full_text = normalize_to_eng_digits(raw_text + " " + norm_text)
    ocr_digits = re.sub(r'\D', '', full_text)
    u_digits = re.sub(r'\D', '', u_id)
    
    if u_digits in ocr_digits:
        return {"score": 100, "status": "MATCH", "span": u_id, "error_type": "SUCCESS"}
    
    return {"score": 0, "status": "MISMATCH", "span": "Not Found", "error_type": "ID_DIGIT_MISREAD"}

def verify_dob(u_dob, raw_text, norm_text):
    full_corpus = normalize_to_eng_digits(raw_text + " " + norm_text)
    
    try:
        y_ad, m_ad, d_ad = map(int, u_dob.split('-'))
        # Convert to BS
        ad_date = datetime.date(y_ad, m_ad, d_ad)
        bs_date = nepali_datetime.date.from_datetime_date(ad_date)
        y_bs, m_bs, d_bs = bs_date.year, bs_date.month, bs_date.day
        
        # Tokens to search for
        u_ad_tokens = {str(y_ad), f"{m_ad:02}", f"{d_ad:02}"}
        u_bs_tokens = {str(y_bs), f"{m_bs:02}", f"{d_bs:02}", str(m_bs), str(d_bs)}

    except Exception as e:
        return {"score": 0, "status": "ERROR", "span": str(e), "error_type": "DATE_PARSE_ERR"}

    match_ad = len([t for t in u_ad_tokens if t in full_corpus]) >= 2 and str(y_ad) in full_corpus
    match_bs = len([t for t in u_bs_tokens if t in full_corpus]) >= 2 and str(y_bs) in full_corpus
    
    if match_bs:
        return {"score": 100, "status": "MATCH", "span": f"BS: {y_bs}-{m_bs}-{d_bs}", "error_type": "SUCCESS"}
    if match_ad:
        return {"score": 100, "status": "MATCH", "span": f"AD: {y_ad}-{m_ad}-{d_ad}", "error_type": "SUCCESS"}
        
    return {"score": 0, "status": "MISMATCH", "span": f"Expected BS: {y_bs}", "error_type": "DOB_MISMATCH"}

def generate_audit_report(ocr_results, user_entry):
    """Main entry point for the service."""
    combined_raw = " ".join([res.get('raw_text', '') for res in ocr_results])
    combined_norm = " ".join([res.get('text', '') for res in ocr_results])
    
    report = {}
    report['name'] = verify_name(user_entry.get('name', ''), combined_raw, combined_norm)
    report['id_number'] = verify_id_number(user_entry.get('id_number', ''), combined_raw, combined_norm)
    report['dob'] = verify_dob(user_entry.get('dob', ''), combined_raw, combined_norm)
    
    # Taxonomy (Error Counting)
    tax_counts = {}
    for f_data in report.values():
        e_type = f_data['error_type']
        tax_counts[e_type] = tax_counts.get(e_type, 0) + 1
        
    return report, tax_counts