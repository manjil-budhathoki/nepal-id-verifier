import nepali_datetime
import datetime

# Consonant Mapping (Moved from field_extractor)
NEP_CONSONANT_MAP = {
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'n',
    'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'n',
    'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
    'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'f', 'ब': 'b', 'भ': 'bh', 'म': 'm',
    'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'b', 'श': 's', 
    'ष': 'sh', 'स': 's', 'ह': 'h', 'क्ष': 'ksh', 'त्र': 'tr', 'ज्ञ': 'gy'
}

ENG_TO_NEP = {'0':'०', '1':'१', '2':'२', '3':'३', '4':'४', '5':'५', '6':'६', '7':'७', '8':'८', '9':'९'}
NEP_TO_ENG_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")

def translate_digits_to_nepali(text):
    if not text: return ""
    return "".join(ENG_TO_NEP.get(char, char) for char in str(text))

def normalize_to_eng_digits(text):
    """Converts Nepali digits to English digits."""
    if not text: return ""
    return text.translate(NEP_TO_ENG_DIGITS)

def ad_to_bs_nepali(ad_date_str):
    """Converts 2000-01-29 to २०५६-१०-१५"""
    try:
        y, m, d = map(int, ad_date_str.replace('/', '-').split('-'))
        ad_date = datetime.date(y, m, d)
        bs_date = nepali_datetime.date.from_datetime_date(ad_date)
        return translate_digits_to_nepali(bs_date.strftime('%Y-%m-%d'))
    except:
        return None