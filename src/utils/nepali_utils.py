import nepali_datetime
import datetime

# Digit Mapping
ENG_TO_NEP = {'0':'०', '1':'१', '2':'२', '3':'३', '4':'४', '5':'५', '6':'६', '7':'७', '8':'८', '9':'९'}

def translate_digits_to_nepali(text):
    """Converts 123 to १२३."""
    if not text: return ""
    return "".join(ENG_TO_NEP.get(char, char) for char in str(text))

def ad_to_bs_nepali(ad_date_str):
    """
    Converts 2000-01-29 to २०५६-१०-१५
    1. AD -> BS
    2. English Digits -> Nepali Digits
    """
    try:
        y, m, d = map(int, ad_date_str.replace('/', '-').split('-'))
        ad_date = datetime.date(y, m, d)
        bs_date = nepali_datetime.date.from_datetime_date(ad_date)
        
        # Get numeric string like '2056-10-15'
        bs_numeric = bs_date.strftime('%Y-%m-%d')
        # Translate to '२०५६-१०-१५'
        return translate_digits_to_nepali(bs_numeric)
    except:
        return None